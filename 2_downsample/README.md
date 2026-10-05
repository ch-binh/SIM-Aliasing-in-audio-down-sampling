# 2 · Notebook → Results → Blog

The notebook is the computational source of truth. The blog is a separate,
less technical article written using its measured results.

| Directory | Contents |
|---|---|
| `input/` | Synthetic 64 kHz PCM16: 3, 10 and 31 kHz |
| `code/` | Notebook, blog builder/template, dependencies and technical notes |
| `output/` | Audio, plots, verified results and blog HTML |

## Step 1: execute locally

From the repository root:

```powershell
.\.venv314\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=120 --ExecutePreprocessor.kernel_name=pcm-aliasing 2_downsample/code/01_pcm_aliasing_walkthrough.ipynb
```

The notebook covers input playback, direct downsampling, both FFTs, filtering
before downsampling, conclusions and future discovery. It verifies sample rates,
duration, clipping, frequencies and alias suppression. Only after success does
it write `output/results.json`, containing measurements and hashes of code/artifacts.

## Step 2: write and build the blog

Review the results and edit the English article in `code/blog_template.html`.
The builder supplies the measured values and artifact links:

```powershell
.\.venv314\Scripts\python.exe 2_downsample/code/build_blog.py
```

It renders `output/blog.html` without running DSP or executing the notebook.
It fails on absent, unverified or changed results. Any previously built blog
is left unchanged on failure; do not publish it as a new result until both steps succeed.

The article shows only two library-call snippets. All computation is in the notebook.
Serve the experiment directory, not just `output`, so audio and source links work.
See the root README for fresh-venv setup, preview and validation commands.

The expected unfiltered tones are 1, 3 and 10 kHz. The filtered reference keeps
3 and 10 kHz and suppresses the 1 kHz alias by approximately 69 dB in this test.
Exact values come from the verified run. Ordinary playback cannot reproduce
31 kHz faithfully; FFTs analyze the saved PCM rather than the speaker output.

## Companion: a real piano note

`code/02_piano_downsampling.ipynb` preserves the synthetic demo and adds a real
recorded A6 note from the University of Iowa collection via Pimoroni. Source bytes,
license and transformations are documented in `input/piano_attribution.md`.
The original stereo 44.1 kHz sample is averaged to mono and safely resampled to
48 kHz before comparing direct sample dropping with low-pass then dropping,
both played at 8 kHz. One shared gain preserves relative amplitudes.

Run computation first, then build the article separately:

```powershell
.\.venv314\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=120 --ExecutePreprocessor.kernel_name=pcm-aliasing 2_downsample/code/02_piano_downsampling.ipynb
.\.venv314\Scripts\python.exe 2_downsample/code/build_piano_blog.py
.\.venv314\Scripts\python.exe -m jupyter nbconvert --to html 2_downsample/code/02_piano_downsampling.ipynb --output piano_notebook_reference --output-dir 2_downsample/output
```

Open `output/piano.html` through the local preview server. The article uses three
WAVs, four plots and `output/piano_results.json`; its builder checks hashes and
never computes DSP or downloads replacement input. Notebook execution is offline
because the licensed source sample is bundled.

This sample has very little energy above 4 kHz, so audible aliasing may be subtle.
The notebook reports input out-of-band energy and pre-decimation filter suppression,
not isolated alias suppression or perceptual quality. Centered convolution aligns
the offline comparison; firmware requires a causal implementation and filter state.
