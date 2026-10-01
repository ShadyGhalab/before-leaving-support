# ReadyKin website: search, discovery and conversion

ReadyKin, formerly Before Leaving. Production origin: **https://beforeleaving.app**.

**Start with [START_HERE.md](START_HERE.md).** This package contains editable source, generated website files, tests and an opt-in GitHub Pages deployment workflow. It has not been deployed or submitted to a search engine.

## Preview and validate

Python **3.10 or newer**; no npm, Python package installation, paid service, database or API key is needed to build the website.

```bash
python3 scripts/build-site.py
python3 scripts/stage-site.py
python3 scripts/validate-site.py
python3 scripts/serve.py
```

Open `http://127.0.0.1:8765`. Stop with Control-C. Use the server, not a file:// URL: the site deliberately uses root-relative URLs and genuine 404 routing for existing app invitations.

## Edit here, then rebuild

| Change | Editable source |
|---|---|
| Name, App Store URL, support contact, verified release, optional verification tokens | `site-src/data/site.json` |
| Eight detailed feature landing pages | `site-src/data/landing-pages.json` |
| Support questions | `site-src/data/faqs.json` |
| Two practical browser checklists | `site-src/data/guides.json` |
| Existing homepage layout and product story | `site-src/templates/home.html` |
| Shared navigation, metadata, structured data and page layouts | `scripts/build-site.py` |
| Responsive discovery page styles | `discovery.css` |
| Progressive navigation | `readykin.js` |
| Checklists and local, non-transmitting attribution event | `discovery.js` |
| Legal policy bodies | `site-src/legal/` — owner review required before editing |

Generated HTML is included for convenient inspection. Edit the source files, not the generated output. The next build overwrites generated pages. `page-history.json` is generated state: commit it to preserve genuine sitemap change dates.

## Public output

22 generated HTML pages: 20 indexable pages plus a noindex invitation page and 404 page. `scripts/stage-site.py` creates `dist/` using an explicit public-file allowlist, including the Apple association file and app-ads.txt. Only publish **dist/**. Do not upload the whole source repository to a generic static host.

## Documentation

- [Deployment, owner review and account setup](START_HERE.md)
- [Implementation report](docs/IMPLEMENTATION_REPORT.md)
- [Feature verification checklist](docs/CONTENT_REVIEW.md)
- [Search Console verification](SEARCH_CONSOLE_VERIFICATION.md)
- [SEO, genuine App Store ASO and outreach](docs/SEO_ASO_PLAYBOOK.md)
- [Measuring referrals and recommendation visibility](docs/MEASUREMENT.md)
- [Separate ChatGPT integration plan](docs/CHATGPT_INTEGRATION_PLAN.md)
- [Primary technical sources](docs/SOURCES.md)
- [Official public links](OFFICIAL_LINKS.md)

## Optional checks

```bash
# Read-only HTTP checks: local by default; use --production only after deployment.
python3 scripts/check-live.py

# Review notification payload; does not contact any search engine.
python3 scripts/indexnow.py

# Optional browser test dependencies; not required to build or publish.
python3 -m pip install -r tests/requirements.txt
python3 -m playwright install chromium
# Keep the preview server running in another terminal:
python3 tests/browser-smoke.py --full
```

The browser report included with this delivery identifies the exact local rendering mode and limitations. This is not a Lighthouse result, a Safari certification or proof of indexing.

## Existing app integrations

Keep `.well-known/apple-app-site-association`, `app-ads.txt`, `CNAME`, the legacy `beforeleaving://` scheme, `/join/*` and `/travel/join/*`. Renaming the product does not mean renaming its bundle identifier or invitation scheme. Their protected file hashes are tested.

The original `scripts/sync-marketing-screenshots.sh` is retained. It imports assets from a sibling iOS repository. Re-review the affected images and regenerate intrinsic image dimensions when importing replacements. No fonts are bundled; the supplied social card is a rendered JPEG using owned screenshots and artwork.

Support: support@beforeleaving.app
