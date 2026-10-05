import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

CODE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("piano_builder", CODE/"build_piano_blog.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class PianoBlogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/"code").mkdir()
        (self.root/"output").mkdir()
        for name in ("02_piano_downsampling.ipynb", "piano_blog_template.html"):
            shutil.copyfile(CODE/name, self.root/"code"/name)
        self.manifest = json.loads((CODE.parent/"output"/"piano_results.json").read_text())
        for record in self.manifest["artifacts"].values():
            target = self.root/record["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(CODE.parent/record["path"], target)
        (self.root/"output"/"piano_results.json").write_text(json.dumps(self.manifest))

    def test_verified_article(self):
        html = builder.build_blog(self.root).read_text(encoding="utf-8")
        self.assertEqual(html.count("<audio "), 3)
        self.assertEqual(html.count("<pre>"), 2)
        self.assertEqual(html.count("<img "), 4)
        self.assertIn(f'{self.manifest["measurements"]["out_of_band_energy_percent"]:.4f}', html)
        self.assertIn("subtle", html)

    def test_missing_manifest_never_recreated(self):
        path = self.root/"output"/"piano_results.json"
        path.unlink()
        with self.assertRaisesRegex(ValueError, "Run and verify"):
            builder.build_blog(self.root)
        self.assertFalse(path.exists())

    def test_missing_artifact_preserves_existing_page(self):
        output = self.root/"output"/"piano.html"
        output.write_text("previous")
        (self.root/self.manifest["artifacts"]["filtered_audio"]["path"]).unlink()
        with self.assertRaisesRegex(ValueError, "Missing or invalid"):
            builder.build_blog(self.root)
        self.assertEqual(output.read_text(), "previous")

    def test_changed_input_rejected(self):
        (self.root/self.manifest["artifacts"]["source_audio"]["path"]).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "Artifact changed"):
            builder.build_blog(self.root)

    def test_code_change_rejected(self):
        path = self.root/"code"/"02_piano_downsampling.ipynb"
        nb = json.loads(path.read_text(encoding="utf-8"))
        next(c for c in nb["cells"] if c["cell_type"] == "code")["source"] = ["changed"]
        path.write_text(json.dumps(nb))
        with self.assertRaisesRegex(ValueError, "Notebook code changed"):
            builder.build_blog(self.root)

    def test_changed_attribution_rejected(self):
        path = self.root/self.manifest["artifacts"]["attribution"]["path"]
        path.write_text("changed source attribution", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Artifact changed: attribution"):
            builder.build_blog(self.root)

    def test_path_outside_experiment_rejected(self):
        self.manifest["artifacts"]["original_audio"]["path"] = "../outside.wav"
        (self.root/"output"/"piano_results.json").write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError, "Missing or invalid"):
            builder.build_blog(self.root)

if __name__ == "__main__":
    unittest.main()
