# What this means for firmware

Consider a MEMS microphone delivering mono PCM at 64 kHz through a digital interface.
The microphone has already sampled and digitized the acoustic signal. Reading
the same output faster does not automatically improve its measurement quality.

Firmware can nevertheless alter the signal by discarding samples. Keeping
alternate samples creates a 32 kHz sequence, whose Nyquist frequency is 16 kHz.
An internal microphone filter designed for the original output rate may not
adequately attenuate everything above this new limit.

## Distinguish these operations

| Firmware behavior | Consequence |
|---|---|
| Read all buffered samples in occasional DMA/FIFO batches | Collection can preserve the original rate if no data is lost |
| Retain every other sample | Downsampling; requires suitable bandwidth limitation |
| Lose a whole buffer and insert silence | Gap in the recording; edges may produce clicks |
| Lose a whole buffer and concatenate the remainder | Missing time interval; possible discontinuity and synchronization error |
| Update a display slowly while processing all samples | Slow display refresh alone does not reduce the data's sample rate |

## Measurements for a future MCU implementation

- Input/output sample counts and timestamps.
- Filter passband error and attenuation above the new Nyquist limit.
- Worst-case execution time per audio block.
- Buffer capacity, overrun count and RAM usage.
- End-to-end latency, including filter and buffering delay.

These are future measurements, not results claimed by the current desktop demo.
