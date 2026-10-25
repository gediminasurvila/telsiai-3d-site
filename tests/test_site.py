import json
from pathlib import Path
import runpy
import tempfile
import unittest

CHECKS = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/check_site.py"))


class SiteChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        links = [CHECKS["DOWNLOAD"] + name for name in CHECKS["PACKAGES"]]
        self.html = "".join(f'<a href="{link}">Download</a>' for link in links)
        (self.root / "index.html").write_text(self.html)
        play = self.root / "play"
        play.mkdir()
        (play / "index.pck").write_bytes(b"pck")
        (play / "index.wasm").write_bytes(b"wasm")
        config = {"fileSizes": {"index.pck": 3, "index.wasm": 4}}
        (play / "index.html").write_text(f"const GODOT_CONFIG = {json.dumps(config)};")

    def test_valid_site(self):
        CHECKS["check_site"](self.root)

    def test_wrong_town_download_rejected(self):
        (self.root / "index.html").write_text(self.html.replace("Telsiai-linux", "Kedainiai-linux"))
        with self.assertRaisesRegex(ValueError, "Download links"):
            CHECKS["check_site"](self.root)

    def test_missing_image_rejected(self):
        (self.root / "index.html").write_text(self.html + '<img src="missing.png">')
        with self.assertRaisesRegex(ValueError, "Missing local resource"):
            CHECKS["check_site"](self.root)

    def test_stale_browser_config_rejected(self):
        (self.root / "play/index.pck").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "file size mismatch"):
            CHECKS["check_site"](self.root)

    def test_partial_release_rejected(self):
        event = {"release": {"draft": False, "assets": [
            {"name": name, "size": 123} for name in CHECKS["PACKAGES"] | {"SHA256SUMS.txt"}]}}
        CHECKS["check_release"](event)
        event["release"]["assets"].pop()
        with self.assertRaisesRegex(ValueError, "all three archives"):
            CHECKS["check_release"](event)
