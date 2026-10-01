# Search Console and Bing verification

Verification proves ownership in your account. A website file by itself does not show that an account has completed verification.

## Google: choose one actual method

**Domain property:** enter `beforeleaving.app` in Search Console, use the TXT record Google gives you and add it at your DNS provider. This cannot be accomplished by adding an HTML meta tag. Existing domain verification can remain in place.

**URL-prefix / HTML file:** use the property for `https://beforeleaving.app/`, choose HTML file and download the actual file from your account. Google-file verification uses content such as:

```text
google-site-verification: google13c0e85923628e64.html
```

The package corrects the format of the filename already present in your repository. Confirm the exact downloaded filename and content in your account. When different, change `google_verification_file` in `site-src/data/site.json`, build and deploy the matching file. Remove an obsolete verification file only after checking whether another owner/account still depends on it.

**URL-prefix / HTML meta tag:** copy the actual content token from the tag Google provides into `google_verification_meta` in `site.json`. The builder adds the meta tag to the public page head. An HTML-file name without its extension is not a substitute for that meta token.

After deployment, open the file URL or inspect View Source for the chosen meta tag, then click Verify in Search Console. Keep the verified method in place. Use URL Inspection to identify robots, canonical, response-code and indexing issues.

## Bing

Use Bing Webmaster Tools to add/import the actual site and complete its offered verification flow. For HTML-meta verification, put the real token in `bing_verification_meta`, rebuild and redeploy. Do not use the Google token for Bing.

## Sitemap

After ownership is verified, submit:

```text
https://beforeleaving.app/sitemap.xml
```

The sitemap includes only canonical indexable pages. Invitation URLs, 404, source, docs, reports and assets are excluded. Search engines can ignore submitted URLs; check indexing reports rather than treating submission as completion.

## Important deployment detail

This is a static `.nojekyll` site built by Python. Jekyll front matter is not needed in a verification file and can corrupt its expected content. `_config.yml` does not protect source directories when Jekyll is bypassed; the supplied staging workflow does.

Official instructions: https://support.google.com/webmasters/answer/9008080 and https://www.bing.com/webmasters/help/add-and-verify-site-12184f8b.
