#!/usr/bin/env python3
"""Proof that site-brand-check.py actually runs: break each assertion, watch it go red.

    python3 tools/site-brand-check-selftest.py

Mutates the working tree one assertion at a time, runs the gate, restores, and
requires a non-zero exit every time. An assertion only ever seen passing is not
known to run at all, so this is the gate's own gate. Exits 0 only when every
case went red AND the tree came back green.

Run it on a clean tree: a mutation that cannot apply is a hard error, and
uncommitted edits are what make one stop applying.
"""
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GATE = ("python3", "tools/site-brand-check.py")


def run():
    p = subprocess.run(GATE, cwd=ROOT, capture_output=True, text=True)
    tags = sorted(set(re.findall(r"^\s*\[([^\]]+)\]", p.stdout, re.M)))
    return p.returncode, tags


def edit_text(rel, fn):
    path = ROOT / rel
    original = path.read_bytes()
    mutated = fn(original.decode())
    assert mutated.encode() != original, f"mutation for {rel} changed nothing"
    path.write_text(mutated)
    return lambda: path.write_bytes(original)


def edit_many(rels, fn):
    restores = [edit_text(rel, fn) for rel in rels]
    return lambda: [r() for r in restores]


def delete(rel):
    path = ROOT / rel
    original = path.read_bytes()
    path.unlink()
    return lambda: path.write_bytes(original)


def corrupt(rel):
    path = ROOT / rel
    original = path.read_bytes()
    path.write_bytes(b"not a jpeg at all")
    return lambda: path.write_bytes(original)


def add_page(rel):
    path = ROOT / rel
    path.write_text("<!DOCTYPE html><html><head></head><body></body></html>")
    return path.unlink


CASES = [
    # assertion 1
    ("1  light accent reuses the dark orange",
     lambda: edit_text("assets/css/tokens.css",
                       lambda t: t.replace("--accent:    #bd4f00;", "--accent:    #ff7a1a;"))),
    ("1  a token is missing",
     lambda: edit_text("assets/css/tokens.css",
                       lambda t: t.replace("  --on-brand:  #100f0d;", "", 1))),
    ("1  no prefers-color-scheme block",
     lambda: edit_text("assets/css/tokens.css",
                       lambda t: t.replace("@media (prefers-color-scheme: light)",
                                           "@media (min-width: 1px)", 1))),
    ("1  tokens.css deleted",
     lambda: delete("assets/css/tokens.css")),

    # assertion 2
    ("2  stylesheet links reordered",
     lambda: edit_text("about/index.html",
                       lambda t: t.replace(
                           '<link rel="stylesheet" href="/assets/css/tokens.css" />\n'
                           '<link rel="stylesheet" href="/assets/css/site.css" />',
                           '<link rel="stylesheet" href="/assets/css/site.css" />\n'
                           '<link rel="stylesheet" href="/assets/css/tokens.css" />'))),
    ("2  tokens.css link dropped from a page",
     lambda: edit_text("writing/index.html",
                       lambda t: re.sub(
                           r'[ \t]*<link rel="stylesheet" href="/assets/css/tokens\.css" />\n',
                           "", t, count=1))),

    # assertion 3
    ("3  a motif file is deleted",
     lambda: delete("assets/img/botanical/tulip.svg")),
    ("3  a motif exists but nothing references it",
     lambda: edit_many(["projects/brain-chiari-dashboard/index.html",
                        "projects/financial-edge-connector/index.html",
                        "templates/media-page.html"],
                       lambda t: t.replace("botanical/tulip.svg", "botanical/cosmos.svg"))),

    # assertion 3b
    ("3b a page loses its motif",
     lambda: edit_text("404.html",
                       lambda t: re.sub(r'[ \t]*<span class="deco deco--foot">.*?</span>\n',
                                        "", t, count=1, flags=re.S))),

    # assertion 4
    ("4  a hex colour appears in an inline style",
     lambda: edit_text("index.html",
                       lambda t: t.replace('style="width:22px;flex:0 0 22px"',
                                           'style="width:22px;flex:0 0 22px;color:#ff7a1a"'))),

    # assertion 4b
    ("4b co-op becomes internship",
     lambda: edit_text("index.html",
                       lambda t: t.replace("Fall 2027 co-op cycle",
                                           "Fall 2027 internship cycle"))),
    ("4b the availability line says Summer 2027",
     lambda: edit_text("index.html",
                       lambda t: t.replace("Open for the Fall 2027 co-op cycle",
                                           "Open for the Summer 2027 co-op cycle"))),

    # assertion 5
    ("5  one word changed in body copy",
     lambda: edit_text("about/index.html",
                       lambda t: t.replace(
                           '<p class="lede muted">Data science and economics at Northeastern',
                           '<p class="lede muted">Data science and economics at Northwestern', 1))),
    ("5  a word is deleted from body copy",
     lambda: edit_text("index.html",
                       lambda t: t.replace("<h2 id=\"work-heading\">Selected work</h2>",
                                           "<h2 id=\"work-heading\">Work</h2>", 1))),
    ("5  two words swapped, count unchanged",
     lambda: edit_text("index.html",
                       lambda t: t.replace("Email is the best way to reach me.",
                                           "Email is the way best to reach me.", 1))),

    # assertion 5b
    ("5b a meta description is shortened",
     lambda: edit_text("about/index.html",
                       lambda t: t.replace(
                           "Ian Solberg is a data science and economics undergraduate at "
                           "Northeastern University, class of 2027, currently a marketing "
                           "analyst co-op at Wayfair and an undergraduate researcher in "
                           "the Loth Lab.",
                           "Ian Solberg.", 1))),
    ("5b the page title changes",
     lambda: edit_text("writing/index.html",
                       lambda t: re.sub(r"<title>[^<]*</title>", "<title>Blog</title>", t, count=1))),
    ("5  an unauthorised word is added",
     lambda: edit_text("writing/index.html",
                       lambda t: t.replace("</main>", "<p>Bonus sentence.</p></main>", 1))),
    ("5  a whole sentence is silently dropped",
     lambda: edit_text("index.html",
                       lambda t: t.replace(
                           "<div class=\"prose\"><p>Email is the best way to reach me.</p></div>",
                           "<div class=\"prose\"></div>", 1))),

    # assertion 6
    ("6  the portrait is deleted",
     lambda: delete("assets/img/ian-byline.jpg")),
    ("6  the portrait is not a JPEG",
     lambda: corrupt("assets/img/ian-byline.jpg")),

    # scope
    ("sc a page is added",
     lambda: add_page("extra.html")),
]


def main() -> int:
    code, tags = run()
    if code != 0:
        print(f"baseline is not green (exit {code}, {tags}); aborting")
        return 1
    print(f"baseline           exit=0  PASS\n")

    bad = 0
    for label, mutate in CASES:
        restore = mutate()
        try:
            code, tags = run()
        finally:
            restore()
        ok = code != 0
        bad += not ok
        print(f"{'RED ' if ok else 'MISS'}  exit={code}  {label:52s} -> {tags}")

    code, tags = run()
    print(f"\nrestored           exit={code}  {'PASS' if code == 0 else 'FAIL ' + str(tags)}")
    if code != 0:
        bad += 1
    if bad:
        print(f"\n{bad} case(s) did not behave")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
