#!/usr/bin/env python3
"""Gate for the iansolberg.us brand application (memory-bank order 90).

Run from the repository root:

    python3 tools/site-brand-check.py

Exits 0 only when every assertion below passes. Assertion numbering follows the
order's "Done when" section; 3b is an extra check that step 6 is actually
satisfied on every page.

The load-bearing one is 5. A brevity pass once deleted real copy while
reporting it had deleted nothing, so 5 does not merely compare word COUNTS: it
requires every word of the base branch to survive, in its original order, and
requires the additions to be exactly the ones the order authorises by name.
That catches a deletion, a reordering, and a silent reword, none of which a
count alone would see.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent

LANDING = "index.html"

MOTIFS = ("cosmos", "seedhead", "stem", "tulip")
MOTIF_DIR = "assets/img/botanical"
TOKENS_HREF = "/assets/css/tokens.css"
TOKENS_PATH = "assets/css/tokens.css"
PORTRAIT = "assets/img/ian-byline.jpg"

AVAILABILITY = "Open for the Fall 2027 co-op cycle"

# Every text addition this order permits, per page. Anything else appearing in a
# page's prose is a copy change and fails assertion 5.
ALLOWED_ADDITIONS: dict[str, list[tuple[str, str]]] = {
    LANDING: [
        (AVAILABILITY, "step 5, the availability line"),
    ],
}

# Assertion 1: the nine tokens, and the three hex values the order pins.
REQUIRED_TOKENS = (
    "--page",
    "--heading",
    "--body",
    "--meta",
    "--kicker",
    "--rule",
    "--brand",
    "--accent",
    "--on-brand",
)
DARK_SELECTOR = ':root, [data-theme="dark"]'
LIGHT_SELECTOR = '[data-theme="light"]'
PINNED = (
    (DARK_SELECTOR, "--brand", "#ff7a1a"),
    (DARK_SELECTOR, "--accent", "#ff7a1a"),
    (LIGHT_SELECTOR, "--brand", "#ff7a1a"),
    (LIGHT_SELECTOR, "--accent", "#bd4f00"),
)

HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")

failures: list[str] = []


def fail(assertion: str, detail: str) -> None:
    failures.append(f"[{assertion}] {detail}")


# --------------------------------------------------------------------------- #
# HTML reading
# --------------------------------------------------------------------------- #

SKIP_TEXT_IN = {"script", "style", "template"}


class PageParser(HTMLParser):
    """Pulls out the three things the gate needs: text, head stylesheets, styles."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text_parts: list[str] = []
        self.head_stylesheets: list[str] = []
        self.style_attrs: list[str] = []
        self.deco_motifs: list[str] = []
        self.copy_meta: dict[str, str] = {}
        self._in_title = False
        self._skip_depth = 0
        self._in_head = False
        self._deco_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: (v or "") for k, v in attrs}

        if tag == "head":
            self._in_head = True
        if tag in SKIP_TEXT_IN:
            self._skip_depth += 1

        if "style" in a:
            self.style_attrs.append(a["style"])

        if tag == "title":
            self._in_title = True

        # Copy that lives in an attribute rather than in the body, so it is
        # invisible to the word count but is still prose a brevity pass can gut.
        if tag == "meta":
            key = a.get("name") or a.get("property") or ""
            if "description" in key or key.endswith("title"):
                self.copy_meta[key] = a.get("content", "")

        if self._in_head and tag == "link":
            rels = a.get("rel", "").lower().split()
            if "stylesheet" in rels:
                self.head_stylesheets.append(a.get("href", ""))

        classes = a.get("class", "").split()
        if "deco" in classes or "deco--mark" in classes:
            self._deco_depth = max(self._deco_depth, 1)
            if tag not in ("img", "br", "hr", "input", "meta", "link"):
                self._deco_depth = 1

        if self._deco_depth and tag == "img":
            self.deco_motifs.append(a.get("src", ""))
        if self._deco_depth and tag == "svg":
            self.deco_motifs.append("<inline svg>")

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            self._in_head = False
        if tag in SKIP_TEXT_IN and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag == "span" or tag == "div":
            self._deco_depth = 0

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.copy_meta["<title>"] = self.copy_meta.get("<title>", "") + data
        if not self._skip_depth:
            self.text_parts.append(data)

    @property
    def words(self) -> list[str]:
        return words_of("".join(self.text_parts))


def words_of(text: str) -> list[str]:
    """Whitespace-separated tokens carrying at least one alphanumeric character.

    So "&" and "©" are punctuation, "2026" is a word, and "co-op" is one
    word: the availability line counts as the seven the order says it does.
    """
    return [t for t in text.split() if any(c.isalnum() for c in t)]


def parse_page(text: str) -> PageParser:
    p = PageParser()
    p.feed(text)
    p.close()
    return p


# --------------------------------------------------------------------------- #
# git
# --------------------------------------------------------------------------- #


def git(*args: str) -> str:
    return subprocess.run(
        ("git", *args), cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout


def base_pages(base: str) -> dict[str, str]:
    listing = git("ls-tree", "-r", "--name-only", base).splitlines()
    return {p: base for p in listing if p.endswith(".html")}


def base_text(base: str, path: str) -> str:
    return git("show", f"{base}:{path}")


# --------------------------------------------------------------------------- #
# assertion 1: tokens.css
# --------------------------------------------------------------------------- #


def css_blocks(css: str) -> dict[str, str]:
    """Selector -> body, for the top-level blocks the gate needs to inspect.

    Comments go first: they carry the contrast ratios, so they are full of the
    colons and hex values the declaration reader looks for.
    """
    css = re.sub(r"/\*.*?\*/", " ", css, flags=re.S)
    out: dict[str, str] = {}
    for m in re.finditer(r"([^{}@]+)\{([^{}]*)\}", css):
        selector = " ".join(m.group(1).split())
        out.setdefault(selector, m.group(2))
    return out


def declared(body: str, name: str) -> str | None:
    m = re.search(rf"{re.escape(name)}\s*:\s*([^;]+);", body)
    return m.group(1).split("/*")[0].strip() if m else None


def check_tokens() -> None:
    path = ROOT / TOKENS_PATH
    if not path.is_file():
        fail("1", f"{TOKENS_PATH} does not exist")
        return
    css = path.read_text()
    blocks = css_blocks(css)

    for selector in (DARK_SELECTOR, LIGHT_SELECTOR):
        if selector not in blocks:
            fail("1", f"{TOKENS_PATH} has no `{selector}` block")

    if not re.search(r"@media\s*\(\s*prefers-color-scheme\s*:\s*light\s*\)", css):
        fail("1", f"{TOKENS_PATH} has no `prefers-color-scheme: light` block")

    dark = blocks.get(DARK_SELECTOR, "")
    for name in REQUIRED_TOKENS:
        if declared(dark, name) is None:
            fail("1", f"`{name}` is not declared in the `{DARK_SELECTOR}` block")

    light = blocks.get(LIGHT_SELECTOR, "")
    for selector, name, want in PINNED:
        got = declared(blocks.get(selector, ""), name)
        if got != want:
            fail("1", f"{selector} {name}: expected {want}, found {got!r}")

    # The failure this whole design was built around.
    if declared(light, "--accent") == declared(dark, "--accent"):
        fail("1", "light mode reuses the dark accent; #ff7a1a is 2.42:1 on paper")


# --------------------------------------------------------------------------- #
# assertion 6: the portrait
# --------------------------------------------------------------------------- #


def jpeg_size(raw: bytes) -> tuple[int, int] | None:
    """Walk the JPEG segment chain to the frame header. None if unreadable."""
    if not raw.startswith(b"\xff\xd8"):
        return None
    i = 2
    n = len(raw)
    while i + 3 < n:
        if raw[i] != 0xFF:
            return None
        marker = raw[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = int.from_bytes(raw[i + 2 : i + 4], "big")
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            if i + 9 > n:
                return None
            h = int.from_bytes(raw[i + 5 : i + 7], "big")
            w = int.from_bytes(raw[i + 7 : i + 9], "big")
            return w, h
        i += 2 + length
    return None


def check_portrait() -> None:
    path = ROOT / PORTRAIT
    if not path.is_file():
        fail("6", f"{PORTRAIT} does not exist")
        return
    size = jpeg_size(path.read_bytes())
    if size is None:
        fail("6", f"{PORTRAIT} is not a readable JPEG")
    else:
        print(f"  portrait {PORTRAIT}: {size[0]}x{size[1]} JPEG")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="main", help="branch the copy is compared against")
    args = ap.parse_args()

    print(f"site-brand-check, base = {args.base}")

    check_tokens()
    check_portrait()

    live = sorted(
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*.html")
        if ".git" not in p.parts
    )
    base = sorted(base_pages(args.base))

    added = set(live) - set(base)
    removed = set(base) - set(live)
    if added:
        fail("scope", f"pages added, which the order forbids: {sorted(added)}")
    if removed:
        fail("scope", f"pages removed, which the order forbids: {sorted(removed)}")

    motif_refs: dict[str, int] = {m: 0 for m in MOTIFS}

    for rel in live:
        page = parse_page((ROOT / rel).read_text())

        # 2: tokens.css ahead of every other stylesheet.
        sheets = page.head_stylesheets
        if not sheets:
            fail("2", f"{rel}: no stylesheet in <head>")
        elif sheets[0] != TOKENS_HREF:
            fail("2", f"{rel}: first stylesheet is {sheets[0]!r}, not {TOKENS_HREF!r}")
        if sheets.count(TOKENS_HREF) != 1:
            fail("2", f"{rel}: links {TOKENS_HREF} {sheets.count(TOKENS_HREF)} times")

        # 3: count motif references.
        for m in MOTIFS:
            motif_refs[m] += len(
                re.findall(rf"{re.escape(MOTIF_DIR)}/{m}\.svg", (ROOT / rel).read_text())
            )

        # 3b: step 6 wants exactly one motif per page, inside a .deco element.
        decos = page.deco_motifs
        if len(decos) != 1:
            fail("3b", f"{rel}: {len(decos)} motifs inside a .deco element, want 1")
        elif not any(f"{MOTIF_DIR}/{m}.svg" in decos[0] for m in MOTIFS):
            fail("3b", f"{rel}: .deco holds {decos[0]!r}, not one of the four motifs")

        # 4: no hex colour in an inline style attribute.
        for attr in page.style_attrs:
            found = HEX.findall(attr)
            if found:
                fail("4", f"{rel}: hex {found} in inline style {attr!r}")

        # 5: the copy is untouched apart from the additions the order names.
        if rel in added:
            continue  # already reported as a scope violation; there is no base to diff
        base_page = parse_page(base_text(args.base, rel))
        base_words = words_of("".join(base_page.text_parts))
        new_words = page.words

        # 5b: the same discipline for copy that hides in attributes.
        for key in sorted(set(base_page.copy_meta) | set(page.copy_meta)):
            was = base_page.copy_meta.get(key)
            now = page.copy_meta.get(key)
            if was != now:
                fail("5b", f"{rel}: {key} copy changed\n        was: {was!r}\n        now: {now!r}")
        allowed = ALLOWED_ADDITIONS.get(rel, [])
        expected_extra: list[str] = []
        for phrase, _why in allowed:
            expected_extra += words_of(phrase)

        want_count = len(base_words) + len(expected_extra)
        if len(new_words) != want_count:
            fail(
                "5",
                f"{rel}: {len(new_words)} words, expected {want_count} "
                f"({len(base_words)} on {args.base} + {len(expected_extra)} authorised)",
            )

        # Stronger than the count: base copy must survive in order.
        leftover: list[str] = []
        it = iter(base_words)
        want = next(it, None)
        for w in new_words:
            if want is not None and w == want:
                want = next(it, None)
            else:
                leftover.append(w)
        if want is not None:
            fail("5", f"{rel}: base copy altered or deleted, first loss at {want!r}")
        if sorted(leftover) != sorted(expected_extra):
            fail(
                "5",
                f"{rel}: unauthorised words {sorted(set(leftover) - set(expected_extra))}"
                or f"{rel}: additions do not match",
            )

    # 3: every motif carries its weight.
    for m in MOTIFS:
        if not (ROOT / MOTIF_DIR / f"{m}.svg").is_file():
            fail("3", f"{MOTIF_DIR}/{m}.svg does not exist")
        elif motif_refs[m] == 0:
            fail("3", f"{MOTIF_DIR}/{m}.svg exists but no page references it")

    # 4b: the availability line, exactly as Ian corrected it.
    landing = (ROOT / LANDING).read_text()
    n = landing.count(AVAILABILITY)
    if n != 1:
        fail("4b", f"{LANDING} contains the availability line {n} times, want 1")
    for banned in ("internship", "Summer 2027"):
        if banned.lower() in landing.lower():
            fail("4b", f"{LANDING} contains {banned!r}")

    print(f"  pages checked: {len(live)}")
    print(f"  motif references: " + ", ".join(f"{m}={motif_refs[m]}" for m in MOTIFS))

    if failures:
        print(f"\nFAIL ({len(failures)})")
        for f in failures:
            print(f"  {f}")
        return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
