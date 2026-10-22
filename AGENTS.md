# For agents working this repository

This is iansolberg.us, Ian Solberg's personal site, served by GitHub Pages from
`main`. Change only what the task names.

Before opening a pull request:

1. If you edited any `.css` file or `assets/resume/ian-solberg-resume.pdf`, run
   `python3 tools/stamp-assets.py`.
2. Run `python3 tools/site-brand-check.py`. It must print PASS. When the task
   deliberately changes page copy, run it with `--content-pass` instead.
3. Never add or remove a page; the check fails on either.

Writing: no em dashes anywhere. Formal, professional tone, in the register of a
resume. No catchphrases and no casual phrasing.
