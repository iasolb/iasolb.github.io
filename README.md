# Personal Website Template
## GitHub Pages Assignment

### File Structure

```
iasolb.github.io/
│
├── index.html          ← Home page (required)
├── interests.html      ← Second page (required)
├── style.css           ← Shared stylesheet (required)
│
└── resources/             ← Create this folder and add your images
    ├── ProfilePic.jpg           (used in index.html hero)
    ├── jump.jpg        (used in index.html cards)
    ├── highlight2.jpg
    ├── highlight3.jpg
    ├── interest-main.jpg     (used in interests.html)
    └── interest-secondary.jpg
```

### Checklist — Requirements Covered

#### index.html (Home Page)
- [x] Main `<h1>` heading
- [x] Short introduction (≥200 words — fill in the placeholder paragraphs)
- [x] At least one image (hero photo + card images)
- [x] Navigation links to second page and contact section

#### interests.html (Second Page)
- [x] `<h2>` heading — smaller than the `<h1>` on the home page
- [x] Descriptive text (≥200 words — fill in the placeholder paragraphs)
- [x] At least one image (two image slots provided)
- [x] Ordered list (`<ol class="styled">`) of top picks
- [x] Navigation links back to home page

#### Contact Information
- [x] Email link (`mailto:`) on both pages
- [x] Social media links (LinkedIn, GitHub) on both pages

#### Navigation
- [x] Sticky nav bar on every page with links between pages

#### CSS Customisation (style.css)
- [x] Custom fonts — Playfair Display (display) + DM Sans (body) via Google Fonts
- [x] Cohesive color scheme via CSS variables (`--bg`, `--accent`, `--ink`, etc.)
- [x] Custom margins, padding, and layout (CSS Grid hero, card grid, media block)

---

### How to Personalise

1. **Replace all `Your Name`** occurrences with your actual name.
2. **Fill in 200+ words** in the placeholder paragraphs on both pages.
3. **Add your images** to the `images/` folder and update the `src` attributes.
4. **Update contact links** — swap in your real email, LinkedIn URL, and GitHub URL.
5. **Rename the topic** on interests.html to match your actual interest (photography, coding, hiking, etc.).
6. **Customise the colour scheme** in style.css by editing the `:root` CSS variables.

### Deploying to GitHub Pages

1. Create a GitHub repo named `<your-username>.github.io`
2. Push all files to the `main` branch
3. Go to Settings → Pages → set source to `main` / `root`
4. Your site will be live at `https://<your-username>.github.io`
