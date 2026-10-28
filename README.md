# Telšiai 3D — website

Website of **Telšiai 3D**: drive the real Telšiai — seven hills, Lake Mastis, the cathedral and every street — in Samogitian. Free.
Hosted on GitHub Pages: https://gediminasurvila.github.io/telsiai-3d-site/

Game downloads (Windows, macOS, Linux) are the releases of this repository; `play/` is the browser version.

- `index.html` — the page (Samogitian by default; Lithuanian and English switch)
- `img/` — in-game screenshots

Game by Gediminas Survila. Map data © OpenStreetMap contributors (ODbL).

## Automated desktop releases

The game repository's **Desktop build and release** workflow regenerates the town, tests it and builds
`Telsiai-linux.zip`, `Telsiai-windows.zip`, `Telsiai-macos.zip` and `SHA256SUMS.txt`. Its upload job creates
releases here. The game repository needs `SITE_RELEASE_TOKEN`, a fine-grained token limited to this
repository with **Contents: read and write**. Never store a token in this repository or in workflow inputs.

Game PRs only retain build artifacts. Game version tags upload draft releases; manual runs can deliberately
publish a fresh version. Review the draft and its source-commit notes before publishing. The existing
`releases/latest/download/Telsiai-*.zip` links automatically use the latest published stable release;
drafts and prereleases do not replace those downloads. Existing releases are never overwritten.

The site's workflow checks local links, download filenames, browser pack/engine sizes and the language
switch on PRs and pushes.
On future release publication it also checks that all three packages and the checksum manifest exist and
are nonempty. This is a post-publication check, not an approval gate or a verification of package hashes;
the game workflow verifies hashes before upload. Run locally with:

```bash
python3 -I scripts/check_site.py
python3 -I -m unittest discover -s tests -v
node --test tests/language.test.mjs
```

GitHub Pages continues to serve `main` from the repository root. Uploading a desktop release does not
replace `play/`, screenshots or site HTML. Browser builds and native graphical/controller testing remain
separate. The current macOS build uses an ad-hoc signature; public Developer ID signing/notarisation is
not supplied by the release workflow.
