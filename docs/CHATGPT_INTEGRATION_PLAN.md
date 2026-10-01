# ReadyKin in ChatGPT: separate backend project

**Status: not implemented or published.** This source archive is a public static support/marketing site. It does not contain ReadyKin user accounts, a trusted reminders API, an OAuth authorization server or a production MCP service. A JSON manifest or SEO text cannot safely substitute for those systems.

Official current documentation: https://developers.openai.com/plugins/ and the authentication/review links in SOURCES.md. Recheck the documentation when starting implementation: naming, publishing surfaces and requirements can change.

## The useful first workflow

User asks to save a reviewed trip packing list into their own connected ReadyKin account. ChatGPT supplies the structured intent; an authenticated service writes it through the same authorized backend that the native app uses. General packing advice alone does not authorize creating or changing private account data.

Proposed small tool surface, names illustrative:

| Tool | Scope | Behavior |
|---|---|---|
| get_trip | trips:read | Read a specific authorized trip; return only needed fields. |
| create_trip | trips:write | Create one explicit user-requested trip; validate local dates/timezone. |
| save_packing_list | packing:write | Save reviewed items into an authorized trip; use an idempotency key. |
| create_reminder | reminders:write | Save a user-requested reminder with an explicit timezone and supported trigger. |
| list_upcoming | trips:read, reminders:read | Limited upcoming items, not the whole user's history by default. |

These scopes and names are a proposed ReadyKin design, not claimed OpenAI-reserved values. Avoid health, payment, contacts, home location and pet/plant records in the initial scope unless required by a separately designed workflow.

## Implementation order

1. Inspect the actual iOS data model, account identity and sync design. Do not assume Firebase is the app's primary writable database simply because its SDK exists. If data is iCloud-only, design a user-authorized bridge rather than claiming a generic web server can read every user's CloudKit data.
2. Build a production HTTPS API with per-user authorization, object ownership checks, input constraints, idempotent writes, auditability, revocation and bounded results. No credentials or secrets in this static repository.
3. Implement the currently supported MCP transport and OAuth flow according to the official documentation. Use individual user authorization and narrowly scoped access, not one global key. Validate token audience, issuer and scope server-side; do not treat a model-supplied user ID as authorization.
4. Treat trip names, checklist items and fetched content as untrusted data. Do not put instructions from user content into privileged tool metadata. Preview destructive changes and require clear user intent; omit deletion from the first release.
5. Test direct requests, context-dependent requests and negative cases. Test cross-account denial, expired/revoked auth, retry idempotency, daylight-saving changes and unavailable destination/timezone information.
6. Add public privacy/support details that accurately cover the new data flow, demonstrate the real service, complete current publisher verification and submission/review requirements.
7. Publish only after approval and test it with a real authorized account and native app sync. Directory placement or proactive suggestions are outside the developer's control.

## Example metadata direction

> Use this tool when the user wants to save a reviewed packing list to a specified trip in their connected ReadyKin account. Do not use it for general recommendations or when the user has not authorized saving. Return the saved list identifier and a confirmed app link supplied by the backend.

Do not invent an unregistered deep link. The existing `beforeleaving://join/` scheme only proves invitation handling, not an arbitrary `readykin://trip/` route.

## Completion boundary for this delivery

The website is now a better public discovery and conversion destination. A ChatGPT tool that actually operates ReadyKin remains a separate product/backend implementation requiring the real app's data model and authenticated infrastructure. No page claims a ReadyKin ChatGPT plugin already exists.
