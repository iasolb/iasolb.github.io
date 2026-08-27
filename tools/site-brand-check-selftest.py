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
    ("1  light accent reuses the dark orange", "1",
     lambda: edit_text("assets/css/tokens.css",
                       lambda t: t.replace("--accent:    #bd4f00;", "--accent:    #ff7a1a;"))),
    ("1  a token is missing", "1",
     lambda: edit_text("assets/css/tokens.css",
                       lambda t: t.replace("  --on-brand:  #100f0d;", "", 1))),
    ("1  no prefers-color-scheme block", "1",
     lambda: edit_text("assets/css/tokens.css",
                       lambda t: t.replace("@media (prefers-color-scheme: light)",
                                           "@media (min-width: 1px)", 1))),
    ("1  tokens.css deleted", "1",
     lambda: delete("assets/css/tokens.css")),

    # assertion 2
    ("2  stylesheet links reordered", "2",
     lambda: edit_text("about/index.html",
                       lambda t: t.replace(
                           '<link rel="stylesheet" href="/assets/css/tokens.css" />\n'
                           '<link rel="stylesheet" href="/assets/css/site.css" />',
                           '<link rel="stylesheet" href="/assets/css/site.css" />\n'
                           '<link rel="stylesheet" href="/assets/css/tokens.css" />'))),
    ("2  tokens.css link dropped from a page", "2",
     lambda: edit_text("writing/index.html",
                       lambda t: re.sub(
                           r'[ \t]*<link rel="stylesheet" href="/assets/css/tokens\.css" />\n',
                           "", t, count=1))),

    # assertion 3
    ("3  a motif file is deleted", "3",
     lambda: delete("assets/img/botanical/tulip.svg")),
    ("3  a motif exists but nothing references it", "3",
     lambda: edit_many(["projects/brain-chiari-dashboard/index.html",
                        "projects/financial-edge-connector/index.html",
                        "templates/media-page.html"],
                       lambda t: t.replace("botanical/tulip.svg", "botanical/cosmos.svg"))),

    # assertion 3b
    ("3b a page loses its motif", "3b",
     lambda: edit_text("404.html",
                       lambda t: re.sub(r'[ \t]*<span class="deco deco--foot">.*?</span>\n',
                                        "", t, count=1, flags=re.S))),

    # assertion 4
    ("4  a hex colour appears in an inline style", "4",
     lambda: edit_text("index.html",
                       lambda t: t.replace('style="width:22px;flex:0 0 22px"',
                                           'style="width:22px;flex:0 0 22px;color:#ff7a1a"'))),

    # assertion 4b
    ("4b co-op becomes internship", "4b",
     lambda: edit_text("index.html",
                       lambda t: t.replace("Fall 2027 co-op cycle",
                                           "Fall 2027 internship cycle"))),
    ("4b the availability line says Summer 2027", "4b",
     lambda: edit_text("index.html",
                       lambda t: t.replace("Open for the Fall 2027 co-op cycle",
                                           "Open for the Summer 2027 co-op cycle"))),

    # assertion 5
    ("5  one word changed in body copy", "5",
     lambda: edit_text("about/index.html",
                       lambda t: t.replace(
                           '<p class="lede muted">Data science and economics at Northeastern',
                           '<p class="lede muted">Data science and economics at Northwestern', 1))),
    ("5  a word is deleted from body copy", "5",
     lambda: edit_text("index.html",
                       lambda t: t.replace("<h2 id=\"work-heading\">Selected work</h2>",
                                           "<h2 id=\"work-heading\">Work</h2>", 1))),
    ("5  two words swapped, count unchanged", "5",
     lambda: edit_text("index.html",
                       lambda t: t.replace("Email is the best way to reach me.",
                                           "Email is the way best to reach me.", 1))),

    # assertion 5b
    ("5b a meta description is shortened", "5b",
     lambda: edit_text("about/index.html",
                       lambda t: t.replace(
                           "Ian Solberg is a data science and economics undergraduate at "
                           "Northeastern University, class of 2027, currently a marketing "
                           "analyst co-op at Wayfair and an undergraduate researcher in "
                           "the Loth Lab.",
                           "Ian Solberg.", 1))),
    ("5b the page title changes", "5b",
     lambda: edit_text("writing/index.html",
                       lambda t: re.sub(r"<title>[^<]*</title>", "<title>Blog</title>", t, count=1))),
    ("5  an unauthorised word is added", "5",
     lambda: edit_text("writing/index.html",
                       lambda t: t.replace("</main>", "<p>Bonus sentence.</p></main>", 1))),
    ("5  a whole sentence is silently dropped", "5",
     lambda: edit_text("index.html",
                       lambda t: t.replace(
                           "<div class=\"prose\"><p>Email is the best way to reach me.</p></div>",
                           "<div class=\"prose\"></div>", 1))),

    # assertion 6 has no case here: it is the order's outstanding blocker, so it
    # is already red at baseline and there is nothing to break. Do NOT add a
    # placeholder JPEG to make it green; substituting an asset is the exact
    # failure this order forbids.

    # scope
    ("sc a page is added", "scope",
     lambda: add_page("extra.html")),
]


def main() -> int:
    code, base_tags = run()
    base_tags = set(base_tags)
    if code == 0:
        print("baseline           exit=0  PASS, nothing outstanding\n")
    else:
        print(f"baseline           exit={code}  already red on {sorted(base_tags)}")
        print("                   (each case below must fire its own assertion "
              "ON TOP of those)\n")

    bad = 0
    for label, want_tag, mutate in CASES:
        restore = mutate()
        try:
            code, tags = run()
        finally:
            restore()
        tags = set(tags)
        fired = want_tag in tags and want_tag not in base_tags
        verdict = "RED " if fired else "MISS"
        bad += not fired
        extra = sorted(tags - base_tags - {want_tag})
        print(f"{verdict}  exit={code}  {label:52s} -> [{want_tag}]"
              + (f" +{extra}" if extra else ""))

    code, tags = run()
    same = set(tags) == base_tags
    print(f"\nrestored           exit={code}  "
          + ("back to baseline" if same else f"DRIFTED to {sorted(tags)}"))
    if not same:
        bad += 1
    if bad:
        print(f"\n{bad} case(s) did not behave")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
