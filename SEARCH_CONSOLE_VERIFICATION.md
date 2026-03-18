# Google Search Console — HTML file verification

Per Google’s guide: **[Verify your site ownership → HTML file upload](https://support.google.com/webmasters/answer/9008080#html_verification&zippy=%2Chtml-file-upload)**

## Why verification failed

> **Your verification file has the wrong content**  
> The verification file that Search Console provides must be used **exactly as provided**, without modifying the **file name** or **content** of the file.

We previously set `content="google13c0e85923628e64"` because that matched the **file name**. Google’s real token inside the downloaded file is **different** and is unique to your account.

## Fix (do this once)

1. Open [Google Search Console](https://search.google.com/search-console) → your property (`https://beforeleaving.app/`).
2. Go to **Settings** → **Ownership verification** (or add property → **HTML file**).
3. Click **Download** next to the HTML verification file.
4. Open the downloaded file in a text editor (TextEdit, VS Code, etc.).  
   You will see the real HTML, for example:
   ```html
   <meta name="google-site-verification" content="AbCdEfGhIj...actual_token..." />
   ```
5. **Replace the file in this repo** with Google’s file:
   - If the downloaded name is `google13c0e85923628e64.html`, **overwrite** `google13c0e85923628e64.html` with the **entire** contents of the download (byte-for-byte).  
   - If Google gives a **different** file name (e.g. `google1234567890.html`), add that file to the repo root with **that exact name** and the **exact** contents from the download. You can remove the old wrong file if the name changed.
6. **Do not** edit the file after download (no extra spaces, no changing the `content` value).
7. Commit, push, wait for the site to deploy (~1–2 minutes).
8. In a private window, open:  
   `https://beforeleaving.app/<exact-filename-from-google>.html`  
   → **View Page Source** and confirm the meta tag matches the download.
9. In Search Console, click **VERIFY**.

## Alternative: HTML tag method

If file upload keeps failing, use **[HTML tag](https://support.google.com/webmasters/answer/9008080#meta_tag_verification)** instead: copy the `<meta name="google-site-verification" content="..." />` Search Console gives you and paste it into the `<head>` of **`index.html`** on this site, then deploy and verify.
