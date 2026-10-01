# Feature evidence and owner sign-off

Scope: supplied website archive and its owned screenshots. The running iOS binary and private App Store Connect metadata were not provided. Live current App Store details could not be independently confirmed during implementation. This table makes the remaining product checks explicit.

| Area | Evidence in supplied code | Implementation decision / owner check |
|---|---|---|
| ReadyKin / previous name | Homepage and existing app material | Current name ReadyKin; Before Leaving is an alternate/historical name. Old domain and app identifiers unchanged. |
| Timed and recurring reminders | Homepage, FAQ and reminder screenshots | Described normally; no guarantee of delivery or safety-critical use. |
| Arrival / departure reminders | Homepage and FAQ | Detailed landing page; explains location/notification permissions and that timing is not exact. Confirm actual permission UI. |
| Packing / trip checklists | Homepage, travel screenshots | Dedicated pages, practical examples and reviewable checklists. |
| Shared trips and family use | Homepage, group screenshots | Shared planning and progress described; no invented enterprise roles, subscription prices or unlimited-user promise. |
| AI-assisted packing | Homepage, assistant screenshot | In-app assistant only, suggested items require review. No claim that the website runs AI or that a public ChatGPT integration exists. |
| Weather suggestions | Homepage and FAQ | Weather-aware suggestions described conservatively. No claim of automatic destination-forecast monitoring, guaranteed predictions or autonomous list updates. Confirm actual source/location behavior before strengthening copy. |
| Apple Watch / iPad / Mac | Homepage and press material | Device support retained with current compatibility referred to the App Store. Exact versions and watch-only capability were not invented. Resolve any remaining platform discrepancy against shipping builds. |
| Languages | FAQ said seven; press had a different list/count | Exact counts removed; App Store listing is the current availability reference. No translated website pages or fictitious hreflang alternates added. |
| Sync and backup | Existing pages made conflicting automatic-sync and local-data assertions | FAQ avoids universal lossless-sync/backup assurances; owner should provide specific current rules. |
| Version / price / rating | Stale changelog; no independently verified current listing | No invented current version, price, star rating, review count or install count. Archived release notes labeled historical. |
| Developer and email | Original website identifies Shady Ghalab and support@beforeleaving.app | Used those source facts, not an unverified company identity from earlier chat. Confirm the preferred public legal/developer name. |
| Legal disclosures | Original privacy and terms bodies | Body text preserved. Review whether on-device AI, Firebase/AdMob, data processing and subscription claims still match the current app. This is not a legal certification. |
| Web analytics | No confirmed analytics account/provider supplied | No new collector, cookies or persistence. Local opt-in integration event only. |
| Invitation links | Existing join.html, 404.html and association file | Same native schemes and paths; noindex/no-referrer on utility pages. No invitation code enters the attribution event. |

## Before the release

Review the eight new landing pages in the browser against the actual app. Verify the screenshot shown on each page is a fair illustration of its topic. Confirm store/paywall and device limitations. Keep legal disclosures accurate. Only then enable deployment.

The new browser checklists do not save into ReadyKin, call an AI, know live weather or synchronize users. Their copy explicitly says they are local, temporary checklists and offers copy/print. This is an intentional honest boundary, not a hidden unfinished feature.
