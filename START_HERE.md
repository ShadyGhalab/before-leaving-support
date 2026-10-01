# Publish the implemented ReadyKin website

## 1. Preserve your existing repository

Extract `ReadyKin-SEO-GEO-Implemented.zip`. The archive contains a `readykin-support/` folder without .git, macOS metadata or credentials. Copy its contents, including dotfolders such as `.github` and `.well-known`, into your existing website working copy. Keep your existing `.git` directory. Review the diff before committing. Do not replace the iOS app repository.

The separate `ReadyKin-Website-Deploy.zip` contains only prebuilt public files. It is suitable for a static host, but it is not the editable source package. Retain the source package for future updates.

## 2. Complete the content review before publishing

Open `docs/CONTENT_REVIEW.md`. In particular:

- Confirm the current app still supports shared trips, location reminders, weather suggestions and the advertised Apple-device experiences.
- The original FAQ contradicted other pages about Mac, OS versions, languages and sync. Specific stale numbers were removed rather than guessed. Current compatibility, price and availability are delegated to the App Store listing.
- The original privacy policy was preserved, including its on-device AI statements. Confirm those statements still match the released app before publishing. Website SEO changes do not certify the app's privacy or legal disclosures.
- Confirm the developer display name and support email in `site-src/data/site.json`.
- The old January 2026 v2.0 changelog is now an archive, not a claimed latest release. Add reviewed current notes only when you have the source.

Do not add unverified ratings, install totals, medical benefits, prices or automatic destination-weather monitoring claims to the schema or copy.

## 3. Build and preview locally

From the website repository root, with Python 3.10+:

```bash
python3 scripts/build-site.py
python3 scripts/stage-site.py
python3 scripts/validate-site.py
python3 scripts/serve.py
```

Visit `http://127.0.0.1:8765` and review the homepage, feature pages, FAQ and both checklist guides. Test `/travel/join/TEST123` and `/join/TEST123` without actually accepting a fake invitation in the iOS app. Run `python3 scripts/check-live.py` in another terminal. Control-C stops the server.

For browser tests, follow README's optional commands. The test suite covers the responsive pages and common interactions but does not replace testing on a real iPhone and Apple Watch.

## 4. Publish with GitHub Pages

The included `.github/workflows/pages.yml` always builds and validates on pushes and pull requests. **Deployment through this workflow is disabled until you explicitly enable it.** This guard does not disable an existing branch-based Pages publisher: switch Pages to GitHub Actions before the first push of the new source, so the whole source directory is not accidentally published.

1. In the repository, open **Settings → Pages** and choose **GitHub Actions** as the source. Keep the custom domain `beforeleaving.app` and verify that HTTPS is enabled. Do not create or change DNS records blindly: retain the working custom-domain setup.
2. Review the `github-pages` environment's allowed deployment branches in GitHub. Only your intended default branch should deploy.
3. In **Settings → Secrets and variables → Actions → Variables**, add `ENABLE_PAGES_DEPLOY` with value `true` when you are ready.
4. Push the reviewed changes to the default branch, or run the workflow manually on that branch. The job publishes **dist/**, not source files.
5. Optional: add `ENABLE_INDEXNOW` with value `true` only when you also want automatic notifications after successful deployment. Leave unset for the first deployment; verify the site first.

The workflow uses GitHub's Pages actions and its repository-provided token. No personal token needs to be embedded. Nothing has been pushed, activated or deployed from this delivery.

A static-host alternative is to upload the contents of `dist/` and configure the host to serve `404.html` with actual HTTP 404 status for unknown paths. Preserve `.well-known/apple-app-site-association` with an application/json-compatible response and no authentication. Existing invitation paths depend on the original 404 fallback. Disable any catch-all rule that turns every unknown URL into a 200 homepage.

## 5. Check the live deployment

```bash
python3 scripts/check-live.py --production
```

This is a read-only check. It checks public pages, crawler files, image files, content type and content hashes for the existing app association and ads files, utility noindex, and real 404 behavior. It is not a Google/OpenAI crawl and cannot confirm indexing or recommendations. Check the output rather than assuming success. Test actual Universal Links on your iPhone as well; Apple's associated-domain cache is outside this website test.

The canonical domain intentionally remains `https://beforeleaving.app`. No new readykin.app domain is assumed to exist. Hosting the same output on a temporary preview domain will still point canonicals at production; protect private previews with your host's access controls.

## 6. Verify Google and Bing, then submit the sitemap

Follow `SEARCH_CONSOLE_VERIFICATION.md`. The old Google verification file was not valid HTML-file verification. This package uses the conventional `google-site-verification: FILENAME.html` content for the existing filename. **Confirm that exact downloaded file belongs to your current Search Console property**; we cannot verify that from the repository.

Google or Bing account tokens remain null in `site.json` unless you supply real ones. Do not paste a guessed token. Rebuild and redeploy after changing verification settings.

Submit `https://beforeleaving.app/sitemap.xml` in the relevant webmaster accounts. Inspect the homepage and the four main intent pages: packing, location reminders, family packing and AI packing. Read the rendered page and indexing diagnostics. Submission is a request, not approval or a ranking signal guarantee.

## 7. Send IndexNow notifications after deployment

```bash
# First inspect the exact payload. No network request:
python3 scripts/indexnow.py

# After the live key file and new pages are available:
python3 scripts/indexnow.py --submit
```

The generated ownership key is public by design. The script checks its live content before posting to IndexNow. A 200 or 202 response accepts the notification; it does not prove the URLs were indexed. IndexNow serves participating search engines, not a private ChatGPT submission API and not Google's Indexing API. No IndexNow requests were submitted during implementation.

Use `--changed-only` immediately after a content-changing build when useful. A second unchanged build correctly reports no changed URLs; use the full sitemap after a first deployment. Deploy before notifying.

## 8. Measure and maintain

`discovery.js` emits a local `readykin:app-store-click` event. It does not send anything to an analytics service. No new tracker or consent banner is installed. Read `docs/MEASUREMENT.md` before wiring your selected analytics provider.

Optional Apple campaign links require your real App Store Connect provider token in `app_store_provider_token`. There is no invented token, automatic install attribution or query-level ChatGPT reporting.

Use the 50-prompt English/German test set in `tests/visibility-prompts.json` for consistent, unbranded discovery checks. Record actual results; no visibility outcomes have been fabricated or measured in this delivery.

For each content release: edit source → build → stage → validate → review → deploy → check live → notify. Commit `site-src/data/page-history.json` so unchanged pages keep their previous sitemap dates.

## What this package does not change

It does not change your App Store Connect name, subtitle, keywords, screenshots, product-page tests or account settings; publish a ChatGPT plugin; create a backend; buy links; submit reviews; or guarantee that an AI will recommend the app. Concrete plans for the remaining account/backend work are included in `docs/`.
