import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

CODE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("blog_builder", CODE / "build_blog.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BlogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "code").mkdir()
        (self.root / "output").mkdir()
        for name in ("blog_template.html", "01_pcm_aliasing_walkthrough.ipynb"):
            shutil.copyfile(CODE / name, self.root / "code" / name)
        self.manifest = json.loads((CODE.parent / "output" / "results.json").read_text())
        for record in self.manifest["artifacts"].values():
            destination = self.root / record["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(CODE.parent / record["path"], destination)
        (self.root / "output" / "results.json").write_text(json.dumps(self.manifest))

    def test_success_shows_three_players_and_only_two_snippets(self):
        html = builder.build_blog(self.root).read_text(encoding="utf-8")
        self.assertEqual(html.count("<audio "), 3)
        self.assertEqual(html.count("<pre>"), 2)
        self.assertIn(f'{self.manifest["measurements"]["alias_reduction_db"]:.2f}', html)

    def test_missing_results_fail_without_recreating_them(self):
        path = self.root / "output" / "results.json"
        path.unlink()
        with self.assertRaisesRegex(ValueError, "Run and verify"):
            builder.build_blog(self.root)
        self.assertFalse(path.exists())

    def test_tampered_audio_is_rejected(self):
        path = self.root / self.manifest["artifacts"]["original_audio"]["path"]
        path.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "Artifact changed"):
            builder.build_blog(self.root)

    def test_missing_audio_is_rejected(self):
        path = self.root / self.manifest["artifacts"]["original_audio"]["path"]
        path.unlink()
        with self.assertRaisesRegex(ValueError, "Missing or invalid"):
            builder.build_blog(self.root)

    def test_changed_code_is_rejected(self):
        path = self.root / "code" / "01_pcm_aliasing_walkthrough.ipynb"
        notebook = json.loads(path.read_text(encoding="utf-8"))
        next(c for c in notebook["cells"] if c["cell_type"] == "code")["source"] = ["x = 2"]
        path.write_text(json.dumps(notebook))
        with self.assertRaisesRegex(ValueError, "Notebook code changed"):
            builder.build_blog(self.root)


if __name__ == "__main__":
    unittest.main()
