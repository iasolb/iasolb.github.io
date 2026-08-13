# iansolberg.us

Static personal site. Hand-written HTML and one stylesheet, no build step, no
dependencies, no JavaScript. Every page is plain HTML you can edit directly.

Dark by default on purpose, using GitHub's own dark palette (Primer), which is
already contrast-checked.

## Structure

```
index.html                     landing page
about/index.html               fuller bio, experience, tools (also prints as a resume)
projects/index.html            all work, grouped
projects/<slug>/index.html     one page per project
404.html                       custom not-found page
assets/css/site.css            the entire design system, one file
assets/favicon.svg             monogram favicon
assets/social-card.svg         source for the link-preview image (needs a PNG, see below)
assets/media/                  audio, video, downloads (has its own README on size limits)
templates/media-page.html      copy this to media/index.html when you want a media section
CNAME                          the custom domain, required by GitHub Pages
.nojekyll                      serve files as-is, skip Jekyll processing
robots.txt, sitemap.xml        search engines
```

There is no shared template system, which is the one real cost of the no-build
approach: the header and footer are copied into each page. Nine pages is well
inside the range where that is cheaper than a static site generator. If it grows
past roughly twenty, revisit.

## Editing

Open the file, change the text, commit. To preview locally:

```
python3 -m http.server 8000 --directory .
```

Then visit `http://localhost:8000`. Use a server rather than opening the file
directly, because all links and asset paths are absolute (`/assets/...`), which
is what makes them work identically on every page.

### Adding a project

1. Copy an existing directory under `projects/`, for example
   `projects/edgewater-farm/`.
2. Replace the content. Keep the `<title>`, `description`, canonical URL, and
   Open Graph tags in sync with the new page, they are per-page for a reason.
3. Add a card to `projects/index.html` and, if it belongs there, to the
   "Selected work" grid on `index.html`.
4. Add the URL to `sitemap.xml`.

## Deploying to GitHub Pages

The site is the repository root, so no build configuration is needed.

**Ian's call, 2026-08-13:** the old Pages site "should be wired into this new one
and then we'll get rid of the old one at the end". So this site takes over the
existing Pages repository and domain wiring rather than living somewhere new, and
the old content is only deleted once the new site is confirmed working on
iansolberg.us. Do not remove the old site in the same pass that publishes this
one; that ordering is the whole point of "at the end".

1. Put these files at the root of the Pages repository. A user site
   (`iasolb.github.io`) is simplest, since it serves from the root by default.
   A project repository works too, it just needs Pages switched on.
   Keep the old files in git history (they are recoverable) but move them out of
   the served root, so there is never a moment with two versions of the site
   reachable at once.
2. In the repository, go to **Settings, Pages** and set the source to deploy
   from the `main` branch, root folder.
3. Set the custom domain to `iansolberg.us`. The `CNAME` file in this repo
   already declares it, so this should match rather than conflict.
4. Wait for the certificate, then tick **Enforce HTTPS**. GitHub's docs say
   that option can take up to 24 hours to become available, so it not being
   there immediately is normal, not a misconfiguration.

## DNS at the registrar

Verified against GitHub's docs on 2026-08-13:
https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site

For the apex domain `iansolberg.us`, four `A` records:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

And four `AAAA` records, which GitHub recommends adding in addition to, never
instead of, the `A` records:

```
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

For `www`, one `CNAME` record pointing at `<username>.github.io` (the account's
default Pages domain, with no repository name on the end).

## Before publishing

Exactly ONE broken link remains, and it is item 1.

1. **Add the resume PDF. This one is Ian's own** (2026-08-13: "resume just needs
   Wayfair stuff added but I'll probably do that"), so it is not an outstanding
   task for a session. The site links to
   `assets/resume/ian-solberg-resume.pdf` from the header nav, the footer, and
   two buttons, and that file does not exist yet, so every one of those links
   404s until he drops it in. See `assets/resume/README.md`. It is the only
   broken link on the site and the one reason not to publish yet.
2. **Make a PNG social card.** `assets/social-card.svg` is the design, but link
   previews need a raster image at `assets/social-card.png` (1200x630). Every
   page already points at that path. Until the PNG exists, links unfurl without
   an image, which is cosmetic and not a broken page.
3. **Read the About page in your own voice.** The copy is written from what is
   on file about you, in a deliberately factual register (Ian, 2026-08-13: no
   catchphrases, "stick my identity only", "should read closer to my resume").
   It should still sound like you rather than a careful description of you.
4. **Optional: the remaining repository links.** Three are already direct, taken
   from his public GitHub profile on 2026-08-13 where they are pinned and public:
   ResearchFramework, FRED_Loader and Census_Loader. The other project pages link
   to the profile rather than a repository, because the farm app and the school
   budget app hold real operational data and are very likely private. Only swap
   those if the repository is genuinely public.

### Settled, no action needed

- **Contact.** Business is `ian@solbergmail.com` (his Proton address, registered
  2026-08-13) and it is the PRIMARY contact: the footer's single Email link and
  the About page's Email button both point at it. Personal
  (`ianspraguesolberg@gmail.com`) and School (`solberg.i@northeastern.edu`) are
  listed beneath it in the labelled contact block on the landing and About pages.
- **LinkedIn** is `https://www.linkedin.com/in/iansolberg`, which matches the link
  on his own GitHub profile.
- **No Instagram.** He asked for it earlier the same evening and then removed it
  ("remove the instagram link it's out of place"), so all 13 links are gone. Do
  not re-add it, even though his GitHub profile still lists the handle.
- **The tagline is his own sentence**, given verbatim on 2026-08-13: "helping
  people interact with the data they create in the way they want to". It replaced
  a line he disliked. Do not reword it.

One smaller gap: the Dartmouth internship entry is a single line because that is
all there is on file.
