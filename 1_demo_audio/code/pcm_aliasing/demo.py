"""Generate and verify a reproducible, unfiltered PCM downsampling demo."""

from pathlib import Path
import json
import wave

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


OUT = Path(__file__).resolve().parents[2] / "output"
FS = 64_000
DURATION = 4
FREQUENCIES = (3_000, 10_000, 31_000)
AMPLITUDE = 0.12


def write_pcm(path, pcm, fs):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(fs)
        wav.writeframes(pcm.astype("<i2").tobytes())


def read_pcm(path):
    with wave.open(str(path), "rb") as wav:
        assert wav.getnchannels() == 1 and wav.getsampwidth() == 2
        fs = wav.getframerate()
        pcm = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
    return pcm, fs


def spectrum(pcm, fs):
    # A coherent 2-second segment excludes the 10-ms playback fades.
    segment = pcm[fs:3 * fs].astype(np.float64) / 32767
    frequencies = np.fft.rfftfreq(len(segment), 1 / fs)
    magnitude = np.abs(np.fft.rfft(segment)) / len(segment)
    magnitude[1:-1] *= 2
    return frequencies, magnitude


def plot_case(pcm, fs, name, expected, highlight, output_dir=OUT):
    values = pcm.astype(np.float64) / 32767
    frequencies, magnitude = spectrum(pcm, fs)
    fig, axes = plt.subplots(2, 1, figsize=(12, 6.8), constrained_layout=True)
    start = fs  # 1 ms in the steady-state portion, with sample markers.
    end = start + fs // 1000 + 1
    time_ms = np.arange(end - start) / fs * 1000
    axes[0].plot(time_ms, values[start:end], ".-", markersize=5, linewidth=1)
    axes[0].set(title=f"{name}: PCM waveform, 1 ms zoom",
                xlabel="Time (ms)", ylabel="Amplitude (full scale)",
                xlim=(0, 1), ylim=(-0.4, 0.4))
    axes[1].plot(frequencies / 1000, magnitude, color="#2563eb", linewidth=1)
    for frequency in expected:
        index = int(np.argmin(np.abs(frequencies - frequency)))
        color = "#dc2626" if frequency == highlight else "#2563eb"
        axes[1].plot(frequency / 1000, magnitude[index], "o", color=color)
        axes[1].annotate(f"{frequency / 1000:g} kHz",
                         (frequency / 1000, magnitude[index]),
                         xytext=(0, 10), textcoords="offset points",
                         ha="center", color=color, fontweight="bold")
    axes[1].axvline(fs / 2000, color="#64748b", linestyle="--", linewidth=1)
    axes[1].set(title="One-sided FFT amplitude of saved WAV (middle 2 seconds)",
                xlabel="Frequency (kHz)", ylabel="Amplitude (full scale)",
                xlim=(0, fs / 2000 + 0.5), ylim=(0, 0.155))
    for axis in axes:
        axis.grid(alpha=0.25)
    fig.savefig(output_dir / f"{name.split(':')[0].lower()}.png", dpi=160)
    plt.close(fig)


def verify(pcm_before, pcm_after, fs_before, fs_after):
    assert fs_before == 64_000 and fs_after == 32_000
    assert len(pcm_before) / fs_before == len(pcm_after) / fs_after == DURATION
    assert np.array_equal(pcm_after, pcm_before[::2])
    assert max(np.max(np.abs(pcm_before.astype(int))),
               np.max(np.abs(pcm_after.astype(int)))) < 32767
    results = {}
    for label, pcm, fs, expected in (
        ("before", pcm_before, fs_before, FREQUENCIES),
        ("after", pcm_after, fs_after, (1_000, 3_000, 10_000)),
    ):
        frequencies, magnitude = spectrum(pcm, fs)
        indices = np.argsort(magnitude)[-3:]
        peaks = sorted(float(frequencies[i]) for i in indices)
        assert peaks == sorted(expected), (label, peaks)
        for frequency in expected:
            index = int(np.argmin(np.abs(frequencies - frequency)))
            assert abs(magnitude[index] - AMPLITUDE) < 0.0001
        one_k = int(np.argmin(np.abs(frequencies - 1_000)))
        results[label] = {
            "sample_rate_hz": fs,
            "samples": len(pcm),
            "duration_seconds": len(pcm) / fs,
            "fft_peaks_hz": peaks,
            "amplitude_at_1khz_fs": float(magnitude[one_k]),
        }
    assert results["before"]["amplitude_at_1khz_fs"] < 0.0001
    assert results["after"]["amplitude_at_1khz_fs"] > 0.119
    return results


def generate_pcm():
    """Create deterministic, unclipped PCM16 with endpoint fades."""
    time = np.arange(FS * DURATION, dtype=np.float64) / FS
    signal = sum(AMPLITUDE * np.cos(2 * np.pi * f * time) for f in FREQUENCIES)
    fade_count = FS // 100  # 10 ms, applied only at recording endpoints.
    fade = np.linspace(0, 1, fade_count)
    signal[:fade_count] *= fade
    signal[-fade_count:] *= fade[::-1]
    return np.rint(signal * 32767).astype(np.int16)


def main(output_dir=OUT):
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    pcm = generate_pcm()
    input_dir = OUT.parent / "input" if output_dir == OUT else output_dir
    input_dir.mkdir(parents=True, exist_ok=True)
    write_pcm(input_dir / "before_64khz.wav", pcm, FS)
    write_pcm(output_dir / "after_32khz_unfiltered.wav", pcm[::2], FS // 2)
    before, fs_before = read_pcm(input_dir / "before_64khz.wav")
    after, fs_after = read_pcm(output_dir / "after_32khz_unfiltered.wav")
    report = verify(before, after, fs_before, fs_after)
    (output_dir / "verification.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    plot_case(before, fs_before, "Before: 64 kHz", FREQUENCIES, 31_000, output_dir)
    plot_case(after, fs_after, "After: 32 kHz",
              (1_000, 3_000, 10_000), 1_000, output_dir)
    html = (Path(__file__).parent / "report.html").read_text(encoding="utf-8")
    if output_dir == OUT:
        html = html.replace('src="before_64khz.wav"', 'src="../input/before_64khz.wav"')
    (output_dir / "index.html").write_text(html, encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Artifacts: {output_dir}")
    return report


if __name__ == "__main__":
    main()
