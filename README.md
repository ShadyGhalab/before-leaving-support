# Before Leaving - Support Website

Support and documentation website for the **Before Leaving** iOS app.

🔗 **Live Site:** [https://beforeleaving.app](https://beforeleaving.app) (custom domain)

**Official URLs** (OAuth, App Store, legal): see **[OFFICIAL_LINKS.md](./OFFICIAL_LINKS.md)** — homepage, privacy, terms, FAQ, press, changelog.

## Pages

- **Home** - App overview and features
- **FAQ** - Frequently asked questions
- **Privacy Policy** - How we handle your data
- **Terms of Service** - Usage terms

## Marketing assets

The homepage uses the English iPhone and iPad marketing renders and the current App Store icon from the iOS app repository. After regenerating screenshots or changing the app icon, refresh the website copies with:

```bash
./scripts/sync-marketing-screenshots.sh
```

The script reads screenshots from `../Before-Leaving/Screenshots/Rendered/default` and the icon from the iOS asset catalog by default. It validates all nine required scenes, writes full-resolution WebP screenshots to `images/marketing`, and regenerates the 1024 px press icon, 180 px website and Apple touch icons, and PNG/ICO favicons. Pass a different rendered screenshot root as the first argument or set `APP_ICON_SOURCE` when the repositories are stored elsewhere.

## Google Search Console (site verification)

The file `google13c0e85923628e64.html` is served at:

`https://beforeleaving.app/google13c0e85923628e64.html`

It uses Jekyll front matter (`layout: null`, `permalink`) so GitHub Pages keeps the exact URL (not “pretty” permalinks).

**If verification fails:** Your Desktop file was only a one-line DNS-style string, not the real HTML. In Search Console → **HTML file** → **Download** again, open the file, copy the **`content="..."`** value from the `<meta name="google-site-verification"` tag, and paste it into `google13c0e85923628e64.html` replacing the current `content="google13c0e85923628e64"` value. Push, then click **VERIFY**.

## Contact

For support inquiries: [support@beforeleaving.app](mailto:support@beforeleaving.app)

---

© 2013-2026 Shady Ghalab. All rights reserved.







