# assets/media/

Where audio, video, images, and downloadable files live. This directory exists
so the site can grow into hosting media without a restructure.

## How to add an audio piece

1. Drop the file here, for example `assets/media/some-recording.mp3`.
2. Copy `templates/media-page.html` to `media/index.html` (first time only) or
   add another `.media-item` block to the existing page.
3. Add the page to `sitemap.xml` and to the nav in each page's header if you
   want it linked.

The stylesheet already carries a `.media-item` component with a styled
`<audio>` and `<video>` player, so no CSS work is needed.

## Size limits, verified against GitHub's own docs 2026-08-13

Source: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits

- **Published site: 1 GB maximum.** This is the real constraint. It covers
  everything served, media included.
- **Bandwidth: 100 GB per month, soft limit.**
- **Builds: 10 per hour, soft limit.**
- GitHub also states Pages "is not intended for or allowed to be used as a free
  web-hosting service to run your online business", and suggests putting a
  third-party CDN in front of a site that outgrows the quotas.

Practical read: a handful of recordings is completely fine. A music library is
not. If this directory ever approaches a few hundred megabytes, move media to
object storage (Cloudflare R2, Backblaze B2) or an embed, and keep the site
itself as the index.

**Do not assume Git LFS solves this.** Whether GitHub Pages serves LFS-tracked
files is UNVERIFIED, and the limits page above does not address it. Test with
one file before committing a workflow to it.
