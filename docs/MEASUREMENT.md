# Measurement without invented results

## 1. Website referral and outbound click

OpenAI documents that ChatGPT Search referral links can include `utm_source=chatgpt.com`. The implementation classifies that source and a small hostname allowlist. It emits a local browser CustomEvent on App Store clicks:

```javascript
window.addEventListener('readykin:app-store-click', event => {
  console.log(event.detail);
  // After separately choosing/configuring a provider and reviewing privacy obligations,
  // map only these fixed fields into that provider's permitted event API.
});
```

Payload shape:

```json
{"event":"app_store_click","page":"/packing-list-app/","placement":"hero","source":"chatgpt","destination":"app_store"}
```

This is a schema example, not a recorded conversion. No automatic network transmission, analytics SDK, cookies, localStorage or sessionStorage are installed. No query text, email, invitation code or complete referring URL is sent in the event. There is no analytics dashboard collecting data yet.

Source classification is **page-level** and best effort. A user may lose the source classification after navigating internally. Do not label it cross-session attribution. Missing/referrer-suppressed traffic is `direct_or_unknown`, not proof of direct navigation. UTM parameters can be supplied by anyone and do not authenticate a human or referral source.

## 2. Optional Apple campaign links

Put your own numeric App Store Connect provider token into `app_store_provider_token` in `site-src/data/site.json`. The builder then produces App Store URLs with `pt`, a fixed page-specific `ct` value and `mt=8`. With null, it leaves the plain store URL. No fake token is used.

Use Apple's campaign reports for data they actually make available, including their attribution rules and privacy/volume limits. A website click is not an installation. Website query strings do not magically reveal the user's ChatGPT prompt, App Store search query or identity. Never promise one-to-one website-to-install attribution from this static site.

## 3. Search indexing and traffic

Check canonical indexing, impressions, clicks and landing pages in the verified Google/Bing accounts. Google says AI-feature reporting is included in its Web search reporting; do not claim it is a dedicated ChatGPT report. IndexNow accepted notifications are not indexed-page counts. Submitted sitemap URLs are not indexed-page counts.

## 4. Repeatable recommendation benchmark

`tests/visibility-prompts.json` contains 50 proposed prompts, not test results: 20 English unbranded, 20 German unbranded, five branded diagnostic and five deliberately poor-fit prompts. Keep branded, unbranded and poor-fit metrics separate. A name appearing because the prompt named it is not organic discovery.

Manually run each prompt in a fresh context without previous ReadyKin conversations, with the same selected model, search mode and locale. Do not use a personalized conversation full of your app's details as the baseline. Repeat a preselected subset rather than cherry-picking successful answers. Record the answer and cited URLs before scoring.

Create one JSON line per observed result:

```json
{"prompt_id":"en-01","run_id":"2026-10-01-run-1","surface":"ChatGPT web","model":"record actual model","search_enabled":true,"country":"DE","locale":"en","readykin_mentioned":false,"readykin_recommended":false,"cited_urls":[],"answer_file":"private/raw-answer.txt"}
```

The line above illustrates format only; do not count it as a measured result. Store raw responses privately and remove personal data before sharing.

Run `python3 scripts/visibility-report.py path/to/observed-results.jsonl` to summarize your actual observations. It rejects unknown prompts, duplicate run/prompt pairs, missing boolean fields and invalid recommended-without-mentioned combinations. It reports sample sizes and observed shares, not model probabilities, guaranteed rank or causal uplift.

Compare like-for-like cohorts and record website release dates. Search-provider changes, user context, sampling variance and app-market changes are confounders. The Responses API can be used for a separate future benchmark, but it is not identical to consumer ChatGPT sessions. No paid API benchmark, scheduled job, traffic collection or external monitoring has been activated here.
