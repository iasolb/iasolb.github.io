#!/usr/bin/env python3
"""Stamp every page's stylesheet and PDF links with the file's own content hash.

Run from the repository root:

    python3 tools/stamp-assets.py           # rewrite every stale stamp in place
    python3 tools/stamp-assets.py --check   # name each stale link, write nothing

WHY. Cloudflare and every browser keep /assets/* for four hours
(`Cache-Control: max-age=14400`, read off the live site 2026-10-22). That
evening a desktop browser drew the new homepage with the old site.css, so the
Worked for row came out as bare, full-size logos, while a phone that had never
cached the sheet looked right. A link ending `?v=<hash of the file>` changes
exactly when the file does, so a new sheet or a new resume is a new URL that no
cache holds. site-brand-check.py fails any page whose stamp is stale, so an edit
that skips this tool cannot pass the gate.

Supersedes the hand-bumped `?v=2026-10-22` resume links, which needed someone
to remember a date and covered the PDF only.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# A site-absolute asset link inside an attribute, with any stamp it already has.
LINK = re.compile(r'(/assets/[A-Za-z0-9_./-]+\.(?:css|pdf))(\?v=[0-9A-Za-z-]*)?(?=")')

# A page model, not a served page: its placeholder links (/assets/media/example.pdf)
# name files that exist only once the model is copied, so a missing file there
# is the template working, not a broken link.
TEMPLATES = "templates/"


def pages(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(p for p in root.rglob("*.html") if ".git" not in p.parts)


def stamp(root: pathlib.Path, href: str) -> str | None:
    """The `?v=` a link to `href` should carry, or None when the file is missing.

    CSS is hashed with CRLF read as LF, so a Windows checkout and a Mac checkout
    of the same commit agree on the stamp. A PDF is hashed as raw bytes."""
    path = root / href.lstrip("/")
    if not path.is_file():
        return None
    raw = path.read_bytes()
    if path.suffix == ".css":
        raw = raw.replace(b"\r\n", b"\n")
    return "?v=" + hashlib.sha256(raw).hexdigest()[:10]


def stale(root: pathlib.Path = ROOT) -> list[tuple[str, str, str]]:
    """Every link whose stamp is wrong: (page, link as written, what it should
    read). A link to a file that does not exist reads `MISSING FILE`."""
    out = []
    for page in pages(root):
        rel = page.relative_to(root).as_posix()
        text = page.read_bytes().decode("utf-8")
        for m in LINK.finditer(text):
            want = stamp(root, m.group(1))
            have = m.group(2) or ""
            if want is None:
                if not rel.startswith(TEMPLATES):
                    out.append((rel, m.group(0), "MISSING FILE"))
            elif have != want:
                out.append((rel, m.group(0), m.group(1) + want))
    return out


def rewrite(root: pathlib.Path = ROOT) -> int:
    """Stamp every link in place, keeping each page's bytes otherwise verbatim
    (line endings included). Returns how many links changed."""
    changed = 0
    for page in pages(root):
        text = page.read_bytes().decode("utf-8")

        def fix(m: re.Match) -> str:
            nonlocal changed
            want = stamp(root, m.group(1))
            if want is None or (m.group(2) or "") == want:
                return m.group(0)
            changed += 1
            return m.group(1) + want

        new = LINK.sub(fix, text)
        if new != text:
            page.write_bytes(new.encode("utf-8"))
    return changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report stale stamps and exit 1 if any, writing nothing")
    args = ap.parse_args()

    if not args.check:
        print(f"stamp-assets: {rewrite()} link(s) restamped")
    bad = stale()
    for page, link, want in bad:
        print(f"  STALE {page}: {link} -> {want}")
    if bad:
        print(f"FAIL: {len(bad)} stale asset link(s)")
        return 1
    print("PASS: every stylesheet and PDF link carries its file's hash")
    return 0


if __name__ == "__main__":
    sys.exit(main())
