# Interoperability contract — schema 2

## One state, five modules

`private/memory.json` is the canonical shared state. All modules read it; only explicit feedback/statements and completed sessions/checks mutate it. Pass the identical `--state` path everywhere. The original scoring workbench uses `products[]` catalog records; its enriched JSON can be retained alongside state. Import analyst assessments through `memory import-items assessments FILE.json`. Owned/ordered/wanted/rejected/sold records use `memory import-items collection FILE.json`.

Routes:

| Trigger | Route | Shared result |
|---|---|---|
| Store link or catalog | Site registry → export → broad genre survey → assessment | Snapshot, coverage, exact listing IDs, evidence |
| Mood or desired experience | Session questions → exploration → sites/catalog → audition → feedback | Session and revisable tag hypotheses |
| Too expensive / unavailable release | Exact edition resolution → watch target → check | Condition/price constraints, observations and alerts |
| New retailer request | Query matrix → AI web search → evidence review → registry → adapter | Verified/candidate retailers, source coverage |
| Like/dislike/correction | Feedback or explicit preference → next session | Updated memory, revision and backups |
| Gift | Named recipient profile → catalog and condition review | Recipient-specific G score, no taste leakage |

## Data boundaries

Catalog JSON: `schema_version`, `source`, `currency`, `checked_at`, `coverage`, `products[]`. Existing v1 catalogs remain readable. CSV columns are stable in `vinyl_suite.FIELDS`; JSON is canonical for nested data. Available must be true/false/null; null stays outside buyable and sold-out lists. Price must be positive and denominated for a buying claim. Each product preserves raw variant data; chosen available variant is a representative row, not an exhaustive per-variant offer table. Verify an exact variant before recommendation.

Coverage: counts, pages, errors, repeated-page flags, pagination exhaustion, sitemap reconciliation. `complete=true` means the public extraction route was exhausted without observed gaps, not that all historic, private, deleted, or unpublished stock exists in the result. Sitemap-only reconciliation after failed pagination remains incomplete because sitemaps can omit sold-out/unpublished listings. Never promote sold-out rows into active recommendations. Search all full-catalog rows only when historical/sold-out research is requested.

State: `schema_version=2`, integer `revision`, UTC `updated_at`, arrays `preferences`, `feedback`, `sessions`, `collection`, `assessments`, `watchlist`, `sites`, `events`. See `templates/state-schema.json` for formal structure. The schema is a published contract; Python validates key invariants, not every possible custom field.

Preferences: stable ID, subject (`self`, `dad`, `mom`, or a separately named friend), key, value, source, status `confirmed`/`inferred`, active, timestamp. Same subject/key changes supersede the prior value rather than silently deleting it. Source must distinguish user statements from inference. Budget, destination, format, dislikes, explicit-content suitability, gift deadlines, artists, editions, and privacy constraints are keys, not assumptions.

Feedback: stable ID, subject, record reference, rating +1/-1, lowercase tags, reason, timestamp, active. Adaptation is tag-specific and recipient-specific. One disliked noisy pressing is not automatically a disliked genre: tag the reason carefully. AI proposes permanent changes only when warranted and labels inference; explicit statements can be saved directly.

Collection: stable ID, artist/title, edition identifiers, status `owned`/`ordered`/`wanted`/`rejected`/`sold`, reasons, dates, costs, source. Different pressings remain distinct. Suppress duplicate-owned recommendations unless a deliberate upgrade/completion case is stated. Collection suppression is an AI workflow requirement; the watch matcher does not automatically delete explicit watch targets for owned records.

Assessments: stable ID, record reference and snapshot timestamp, purpose, named recipient where applicable, `scores` L/G/C/A/R/U/I/V/Q (integer 1–5 or null), `evidence[]`, confidence, rationale, next verification. Market/objective scores require evidence; unknown stays null. Recipient G scores should be separate rows per recipient. Link rather than overwrite source observations.

Watch targets: stable ID, enabled, artist/title, optional exact catalog/label/format/year/product/variant constraints, ceiling, currency, basis `item`/`landed`, explicit shipping/tax assumptions, optional media floor, last checked, last qualifying signatures. Missing edition/currency/currentness prevents a qualified alert. Seller metadata is not copy-level authenticity proof. An item-price ceiling excludes shipping; landed mode uses supplied estimates, which must be rechecked. Reports contain all matches and lead reasons, even when no alert qualifies.

Sites: stable ID, URL, name, genres, adapter (`shopify` or `manual`), currency, evidence, verification state, timestamp. Registry admission does not imply credibility. Never guess a Storefront/Admin API credential or bypass a sign-in wall. Manual sources use authorized AI browsing/export.

## Merge and transport

1. Inventory files, schema versions, IDs, timestamps, coverage, and checksums; distinguish snapshots from current observations.
2. Use the latest explicitly selected memory as authoritative. Compare revision and content hash. Do not merge two diverged files by newest timestamp alone.
3. Merge stable IDs without discarding evidence/history; flag contradictory price/edition data. Same preference subject/key needs an explicit source precedence decision. Duplicate feedback must not be counted twice.
4. Work on a copy. The CLI serializes mutations with a lock, writes backup before replacement, and increments revision. Concurrent write conflicts must be retried only after inspecting current state.
5. Export updated state, catalog assessment ledger, and a short change log. Upload these into the next AI. Keep private copies outside the provider's transient workspace.
6. Unsupported future schema: stop writes, preserve original, perform a documented migration on a copy, validate, and retain old version. No silent schema downgrade.

## Capability tiers

- Text-only AI: read pasted protocol/manual and prepare plans; cannot claim file execution, live browsing, or scheduled checks.
- File-aware AI: read attached data and maintain downloadable state if file creation is supported.
- Python-enabled AI: run standard-library CLI, subject to its network policy.
- Web-enabled AI: run Site Finder and watch search queries with source/date evidence; no universal claim to scour the entire internet.
- Scheduler-enabled environment: run configured checks between chats. Requires durable state, available source access, and a configured delivery route if external notifications are desired.

Use any existing available tools appropriately (Spotify exports, authorized marketplace APIs, browsing, local catalogs, prior evidence), recording capability and coverage rather than inventing integrations.


## Version 2.1 extension

Read [RESEARCH-WORKFLOW.md](RESEARCH-WORKFLOW.md) for the canonical staged research process, three-tier exploration, two additional helper CLIs, source/history limitations, curiosity feedback weighting and failed-source watch recovery. This extension supersedes conflicting earlier exploration-size defaults; the original mission and score definitions remain.
