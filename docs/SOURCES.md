# Primary technical references

Reviewed 1 October 2026. These inform implementation decisions, not a guarantee of rankings. Recheck account UI and publishing requirements when deploying.

| Source | Relevant implementation |
|---|---|
| [OpenAI publishers/developers FAQ](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq) | OAI-SearchBot access, crawlable noindex and ChatGPT referral UTM |
| [OpenAI crawler overview](https://developers.openai.com/api/docs/bots) | Search crawler distinct from GPTBot training controls |
| [Google AI features and your website](https://developers.google.com/search/docs/appearance/ai-features) | Helpful crawlable text, internal links, matching structured data; no special AI file/schema required |
| [Google sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) | Canonical URLs and genuine lastmod, not fabricated daily freshness |
| [Google canonical URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) | Consistent production canonical paths |
| [Schema.org MobileApplication](https://schema.org/MobileApplication) | Software identity and app fields |
| [Google software-app structured data](https://developers.google.com/search/docs/appearance/structured-data/software-app) | Semantic schema is not automatic rich-result eligibility; no invented offers/reviews |
| [IndexNow protocol](https://www.indexnow.org/documentation) | Public ownership key, HTTPS notification payload, batch limits and accepted status handling |
| [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) | Explicit Pages build artifact and deployment permissions |
| [GitHub Python workflow](https://docs.github.com/en/actions/tutorials/build-and-test-code/python) | Python setup in validation workflow |
| [Apple App Store product-page guidance](https://developer.apple.com/app-store/product-page/) | App naming, subtitle, keywords, screenshots and testing distinct from website SEO |
| [Apple App Store information reference](https://developer.apple.com/help/app-store-connect/reference/app-information/app-information) | Name/subtitle length and editable account fields |
| [Apple campaign links](https://developer.apple.com/help/app-store-connect-analytics/acquisition/campaign-links) | Optional real account provider/campaign parameters |
| [OpenAI authenticated MCP](https://developers.openai.com/plugins/build/auth) | Future backend authorization requirements; not implemented in static site |
| [OpenAI MCP review](https://developers.openai.com/plugins/deploy/app-review) | Future public service review and publishing |
| [OpenAI plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines) | Real utility and distribution limits; no guaranteed proactive suggestion |

The site's product copy is based on the supplied repository and owned screenshots, not independently verified clinical, performance, pricing or recommendation claims. See CONTENT_REVIEW.md for the unresolved product facts.
