"""Check local site resources, release download URLs and published release asset names."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

REPOSITORY = "gediminasurvila/telsiai-3d-site"
PACKAGES = {f"Telsiai-{platform}.zip" for platform in ["linux", "windows", "macos"]}
DOWNLOAD = f"https://github.com/{REPOSITORY}/releases/latest/download/"


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        self.urls.extend(value for name, value in attrs if name in {"src", "href"} and value)


def check_site(root: Path) -> None:
    for page in [root / "index.html", root / "play/index.html"]:
        html = page.read_text(encoding="utf-8")
        parser = Resources()
        parser.feed(html)
        urls = parser.urls + re.findall(r"url\(['\"]?([^)'\"]+)", html)
        for url in urls:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            target = (page.parent / unquote(parts.path)).resolve()
            if target.is_dir():
                target /= "index.html"
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                raise ValueError(f"Missing local resource in {page.name}: {url}")
        if page == root / "index.html":
            downloads = {url for url in urls if "/releases/latest/download/" in url}
            if downloads != {DOWNLOAD + name for name in PACKAGES}:
                raise ValueError("Download links must match the three Telšiai release archives")
        else:
            config = json.loads(re.search(r"const GODOT_CONFIG = (.*);", html)[1])
            for name, size in config["fileSizes"].items():
                resource = (page.parent / name).resolve()
                if not resource.is_relative_to(root.resolve()) or resource.stat().st_size != size:
                    raise ValueError(f"Browser engine file size mismatch: {name}")
            if (page.parent / "index.pck").stat().st_size >= 100_000_000:
                raise ValueError("Browser data exceeds the 100 MB project budget")


def check_release(event: dict) -> None:
    release = event["release"]
    if release["draft"]:
        raise ValueError("Expected a published release event")
    assets = release["assets"]
    names = [asset["name"] for asset in assets]
    required = PACKAGES | {"SHA256SUMS.txt"}
    if any(names.count(name) != 1 for name in required):
        raise ValueError("Release requires all three archives and SHA256SUMS.txt exactly once")
    if any(asset["size"] <= 0 for asset in assets if asset["name"] in required):
        raise ValueError("Release assets must not be empty")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-event", type=Path)
    args = parser.parse_args()
    check_site(Path(__file__).resolve().parents[1])
    if args.release_event:
        check_release(json.loads(args.release_event.read_text(encoding="utf-8")))
    print("SITE CHECKS: PASS")
