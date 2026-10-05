"""Render a blog from verified notebook artifacts. No DSP is executed here."""

import argparse
import hashlib
from html import escape
import json
import os
from pathlib import Path
from string import Template
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ("original_audio", "unfiltered_audio", "filtered_audio", "original_plot",
             "unfiltered_plot", "filtered_plot", "filter_response")


def build_blog(root=ROOT, source_url=None):
    root = Path(root).resolve()
    manifest_path = root / "output" / "results.json"
    if not manifest_path.is_file():
        raise ValueError("Missing output/results.json. Run and verify the notebook first.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("verified") is not True:
        raise ValueError("The notebook results are not marked as verified.")
    notebook = json.loads((root / "code" / "01_pcm_aliasing_walkthrough.ipynb").read_text(encoding="utf-8"))
    source = "\n".join("".join(cell["source"]) for cell in notebook["cells"]
                       if cell["cell_type"] == "code")
    if hashlib.sha256(source.encode("utf-8")).hexdigest() != manifest["source_code_sha256"]:
        raise ValueError("Notebook code changed after verification. Run it again.")
    context = {}
    for name in ARTIFACTS:
        record = manifest["artifacts"][name]
        path = (root / record["path"]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"Missing or invalid artifact: {name}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(f"Artifact changed after verification: {name}. Run the notebook again.")
        context[name] = escape(quote(os.path.relpath(path, root / "output").replace(os.sep, "/")), quote=True)
    values = manifest["measurements"]
    context.update(
        reduction=f'{values["alias_reduction_db"]:.2f}',
        before_alias=f'{values["unfiltered_1khz_amplitude_fs"]:.6f}',
        after_alias=f'{values["filtered_1khz_amplitude_fs"]:.8f}',
        taps=str(values["fir_taps"]), cutoff=f'{values["nominal_cutoff_hz"] / 1000:g}',
        delay=f'{values["group_delay_ms"]:g}',
        source_url=escape(source_url or "../code/01_pcm_aliasing_walkthrough.ipynb", quote=True),
    )
    template = Template((root / "code" / "blog_template.html").read_text(encoding="utf-8"))
    destination = root / "output" / "blog.html"
    destination.write_text(template.substitute(context), encoding="utf-8")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", help="Public GitHub notebook URL, once available")
    args = parser.parse_args()
    try:
        print(build_blog(source_url=args.source_url))
    except (ValueError, KeyError, OSError) as error:
        print(f"Cannot build blog: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
