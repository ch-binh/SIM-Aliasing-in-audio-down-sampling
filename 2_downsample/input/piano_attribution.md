# Piano source and transformations

- Note: A6, forte; actual recorded piano, not a synthesized oscillator.
- Creator: Lawrence Fritts, University of Iowa Musical Instrument Samples project.
- Distributed file: 39221__Piano.ff.A6.wav from Pimoroni Piano-HAT.
- Download: https://raw.githubusercontent.com/pimoroni/Piano-HAT/master/examples/sounds/piano/39221__Piano.ff.A6.wav
- Distributor license statement: https://github.com/pimoroni/Piano-HAT/blob/master/examples/sounds/piano/LICENSE.txt
- Original project: https://theremin.music.uiowa.edu/MIS.html
- Downloaded: 2026-10-05.

The distributor identifies this Iowa sample among the missing notes added to jobro's pack and quotes permission for use in any projects without restrictions. The original project also grants unrestricted project use. The bundled piano_source_LICENSE.txt preserves the distributor's complete statement (including the separate attribution requirement for jobro samples).

The distributed sample was already trimmed by Pimoroni. We preserve those source bytes. The notebook averages stereo channels, uses filtered resampling from 44.1 to 48 kHz, applies one shared gain for headroom, and trims at most five samples. The two outputs keep every sixth sample, either directly or after a low-pass FIR. No independent loudness normalization or injected tones.
