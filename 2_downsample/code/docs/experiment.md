# Experiment methodology

Date: 2026-10-05. This document describes the synthetic PCM experiment, not a hardware test.

## Hypothesis

Reducing a PCM stream from 64 to 32 kHz by keeping alternate samples, without
adequate anti-alias filtering, maps an existing 31 kHz component to 1 kHz.
Playing the output at its correct 32 kHz rate does not reverse this mapping.

## Input and operation

The signal is the sum of three cosine waves at 3, 10 and 31 kHz, each with
peak amplitude 0.12 FS. It is sampled at 64 kHz for 4 seconds and rounded to
signed PCM16. A 10 ms linear fade is applied only at recording endpoints.

The output is `x[::2]`, saved as PCM16 at 32 kHz. No filter and no gain change
are applied. Samples are discarded, not replaced with zeros.

For the 31 kHz component, retained samples have phase advance
`2π * 31/32` per output sample. This equals `-2π * 1/32` modulo `2π`.
Because the component is a zero-phase real cosine, its samples match a 1 kHz cosine.

The 3 and 10 kHz components remain within the new Nyquist interval.

## Measurement

WAV files are decoded back to integer samples. A 2-second segment from
1 to 3 seconds is used for the FFT. All tones contain an integer number of cycles
in that segment, so a rectangular window is sufficient for this experiment.
This choice is not a general recommendation for arbitrary microphone recordings.

The FFT has 0.5 Hz bin spacing. One-sided amplitudes are scaled by the segment
length and doubled except at DC and Nyquist. Both plots use the same amplitude
scale. Waveform plots show 1 ms, with actual sample markers; interpolating lines
are only a visual aid.

## Results and acceptance criteria

- Input peaks: 3,000; 10,000; 31,000 Hz.
- Output peaks: 1,000; 3,000; 10,000 Hz.
- Each peak remains within 0.0001 FS of the specified 0.12 FS amplitude.
- Input 1 kHz amplitude is below 0.0001 FS; output 1 kHz amplitude exceeds 0.119 FS.
- WAV rates are 64 and 32 kHz; duration is 4 seconds in both.
- Output samples exactly match even-indexed input samples; neither WAV clips.

See the generated `verification.json` for measured values. Automated tests also
exercise an isolated 31 kHz tone, an in-band 3 kHz tone and WAV round-trip behavior.

## Playback interpretation

The original file is not expected to reproduce 31 kHz faithfully on ordinary
audio hardware. Browser/OS resampling may remove that component before playback.
The plots analyze the saved PCM directly. The audible evidence is the extra
1 kHz component after downsampling, supported by the numerical FFT.
