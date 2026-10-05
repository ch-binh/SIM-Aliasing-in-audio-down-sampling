# 1 · Original Audio Demo

The initial experiment retains alternate samples of 64 kHz PCM containing
3, 10 and 31 kHz, then saves and plays the result at 32 kHz. The 31 kHz tone
aliases to 1 kHz. Anti-alias filtering is intentionally omitted.

- `input/`: original PCM16 WAV.
- `code/`: demo, tests and dependencies; unchanged early experiments in `learning_history/`.
- `output/`: unfiltered WAV, plots, numerical verification and playback report.

From the repository root:

```powershell
.\.venv314\Scripts\python.exe 1_demo_audio/code/run_demo.py
```

For regression tests, change to `1_demo_audio/code` and run the venv's Python
with `-m unittest discover -s tests -v`.

Serve this experiment directory and open `/output/index.html` for playback.
The full notebook → filter → blog pipeline is in `2_downsample`.
