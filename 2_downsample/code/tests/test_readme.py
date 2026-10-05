"""Keep the graph-only README consistent with verified notebook results."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "2_downsample"


class ReadmeTests(unittest.TestCase):
    def test_readme_uses_verified_plots_without_audio_embeds(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        manifest = json.loads((EXPERIMENT / "output/results.json").read_text())
        self.assertTrue(manifest["verified"])
        plots = re.findall(r"!\[[^\]]+\]\(([^)]+)\)", readme)
        self.assertEqual(len(plots), 6)
        self.assertNotRegex(readme, r"(?i)<audio\b|\]\([^)]*\.wav\)")
        for name in ("original", "unfiltered", "filtered"):
            for domain in ("waveform", "fft"):
                artifact = manifest["artifacts"][f"{name}_{domain}"]
                self.assertIn("2_downsample/" + artifact["path"], plots)
                self.assertEqual(hashlib.sha256((EXPERIMENT / artifact["path"]).read_bytes()).hexdigest(), artifact["sha256"])
        measured = manifest["measurements"]["alias_reduction_db"]
        self.assertIn(f"**{measured:.2f} dB**", readme)
        self.assertIn("**1 kHz: |31 − 32| = 1 kHz**", readme)


if __name__ == "__main__":
    unittest.main()
