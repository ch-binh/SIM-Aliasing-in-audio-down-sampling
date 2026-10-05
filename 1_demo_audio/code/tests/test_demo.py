"""Numerical regression checks for the signal transformation, not playback hardware."""

from pathlib import Path
import tempfile
import unittest

import numpy as np

from pcm_aliasing.demo import FS, generate_pcm, read_pcm, spectrum, verify, write_pcm


class AliasingTests(unittest.TestCase):
    def test_ultrasonic_tone_folds_to_one_khz(self):
        time = np.arange(4 * FS) / FS
        original = np.rint(0.12 * np.cos(2 * np.pi * 31_000 * time) * 32767).astype(np.int16)
        frequencies, amplitudes = spectrum(original[::2], FS // 2)
        self.assertEqual(frequencies[np.argmax(amplitudes)], 1_000)
        self.assertAlmostEqual(float(np.max(amplitudes)), 0.12, places=4)

    def test_in_band_tone_preserves_frequency(self):
        time = np.arange(4 * FS) / FS
        original = np.rint(0.12 * np.cos(2 * np.pi * 3_000 * time) * 32767).astype(np.int16)
        frequencies, amplitudes = spectrum(original[::2], FS // 2)
        self.assertEqual(frequencies[np.argmax(amplitudes)], 3_000)

    def test_saved_pcm_and_frequency_results(self):
        pcm = generate_pcm()
        with tempfile.TemporaryDirectory() as temp:
            before_path = Path(temp) / "before.wav"
            after_path = Path(temp) / "after.wav"
            write_pcm(before_path, pcm, FS)
            write_pcm(after_path, pcm[::2], FS // 2)
            before, before_rate = read_pcm(before_path)
            after, after_rate = read_pcm(after_path)
            np.testing.assert_array_equal(before, pcm)
            np.testing.assert_array_equal(after, pcm[::2])
            report = verify(before, after, before_rate, after_rate)
        self.assertEqual(report["before"]["duration_seconds"], 4)
        self.assertEqual(report["after"]["fft_peaks_hz"], [1_000, 3_000, 10_000])

    def test_incorrect_playback_metadata_is_rejected(self):
        pcm = generate_pcm()
        with self.assertRaises(AssertionError):
            verify(pcm, pcm[::2], FS, FS)


if __name__ == "__main__":
    unittest.main()
