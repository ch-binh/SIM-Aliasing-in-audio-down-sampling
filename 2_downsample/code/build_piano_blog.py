"""Build the piano article from verified notebook results; never execute DSP."""
import hashlib
from html import escape
import json
import os
from pathlib import Path
from string import Template
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent

def build_blog(root=ROOT):
    root = Path(root).resolve()
    manifest_path = root / "output" / "piano_results.json"
    if not manifest_path.is_file():
        raise ValueError("Missing piano results. Run and verify the piano notebook first.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("verified") is not True:
        raise ValueError("Piano results are not verified.")
    notebook = json.loads((root/"code"/"02_piano_downsampling.ipynb").read_text(encoding="utf-8"))
    source = "\n".join("".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code")
    if hashlib.sha256(source.encode()).hexdigest() != manifest["source_code_sha256"]:
        raise ValueError("Notebook code changed. Execute it again.")
    required = ("source_audio", "source_license", "attribution", "original_audio",
                "unfiltered_audio", "filtered_audio", "original_plot", "unfiltered_plot",
                "filtered_plot", "comparison_plot")
    context = {}
    for name in required:
        record = manifest["artifacts"][name]
        path = (root/record["path"]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"Missing or invalid artifact: {name}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(f"Artifact changed: {name}")
        context[name] = escape(quote(os.path.relpath(path, root/"output").replace(os.sep, "/")), quote=True)
    m = manifest["measurements"]
    context.update(energy=f'{m["out_of_band_energy_percent"]:.4f}',
                   suppression=f'{m["pre_decimation_reduction_db"]:.2f}',
                   peak=f'{m["strongest_out_of_band_hz"]:.0f}',
                   folded=f'{m["predicted_folded_hz"]:.0f}',
                   fundamental=f'{m["fundamental_hz"]:.0f}',
                   duration=f'{m["duration_s"]:.4f}')
    page = Template((root/"code"/"piano_blog_template.html").read_text(encoding="utf-8")).substitute(context)
    target = root/"output"/"piano.html"
    target.write_text(page, encoding="utf-8")
    return target

if __name__ == "__main__":
    try:
        print(build_blog())
    except (OSError, ValueError, KeyError) as error:
        print(f"Cannot build piano blog: {error}", file=sys.stderr)
        raise SystemExit(1)
