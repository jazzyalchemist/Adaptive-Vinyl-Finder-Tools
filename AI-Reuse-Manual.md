# Adaptive Vinyl Finder — complete AI reuse manual

Canonical source documents follow in full. Read module boundaries and capabilities honestly.



---

Source: README.md

# Adaptive Vinyl Finder Tools — 2.0

Five interoperable tools for lifelong listening, discovery, gifts, bargains, and evidence-backed collector research. Python 3.10+; no third-party Python packages or paid API required. AI browsing depends on the capabilities of the AI you use.

| Tool | What runs locally | What an AI adds |
|---|---|---|
| Catalog Exporter | Compatible public Shopify feed scan; optional public sitemap reconciliation; active CSV, full catalog JSON, sold-out CSV, unknown-stock CSV, coverage manifest | Non-Shopify extraction, edition research, completeness comparison |
| Memory Matrix | Persistent preferences, recipient profiles, collection dispositions, assessments, feedback, interpretable adaptation, backups | Careful interpretation, explicit-versus-inferred distinctions |
| Experience Explorer | Mood questionnaire, session plan, broad style heuristics, feedback modifiers | New artists/releases, listening references, catalog matching, evidence-based shortlists |
| Record Watchlist | Edition constraints, condition floor, item/landed ceiling, refreshed source checks, change alerts and deduplication | Wider web searches for missing records and manual-site verification |
| Site Finder | Broad and niche search query matrix, retailer registry, reachability probe | Actual internet search, retailer assessment, genre/region coverage |

These are downloadable code and AI workflows, not tools automatically installed into every AI. File upload does not execute code, grant web access, persist memory across chats, or create a background service. Use the same `private/memory.json` across modules and carry it between chats. Keep a copy outside temporary AI sandboxes.

## Start in any AI chat

1. Download the ZIP, attach it, and paste `prompts/BOOTSTRAP.md` (also available as `AI-Start-Here.md`). Attach your latest memory and catalog files if you have them.
2. Ask the AI to inventory/read actual files and describe its available file, Python, web-search, browsing, and scheduling capabilities.
3. If it has Python, it can run the commands below. If it cannot unzip, attach `AI-Reuse-Manual.md` and your data separately. If it cannot browse, it can analyze supplied data and prepare queries; it must report that limitation.
4. Download the updated memory file after a session. Upload it to the next chat. Never assume chat memory is your canonical database.

## Run locally

Unzip and open a terminal in this directory. Use `python` instead of `python3` where your installation requires it.

```sh
python3 vinyl_suite.py memory init
python3 vinyl_suite.py export --url https://recordselectorlv.com/ --currency USD --sitemap --out private/record-selector
python3 vinyl_suite.py memory set currency USD --source 'Explicit user instruction'
python3 vinyl_suite.py memory set favorite_experience 'Atmospheric, emotional musical journeys' --source 'Explicit user instruction'
python3 vinyl_suite.py explore --mood reflective --experience 'immersive journey' --energy low --lyrics either --novelty high
python3 vinyl_suite.py memory feedback 'artist / exact release' --rating 1 --tags 'spacious,ambient' --reason 'Loved the textures'
python3 vinyl_suite.py sites queries --genre 'spiritual jazz' --region 'ships to USA'
python3 vinyl_suite.py sites add https://recordselectorlv.com/ --name 'Record Selector' --adapter shopify --currency USD --evidence 'User-supplied store; verify policies'
python3 vinyl_suite.py watch add --artist 'Jean-Michel Jarre' --title 'Oxygène' --cat 'EXACT-CATALOG-NUMBER' --format 'LP' --ceiling 25 --currency USD --media-min 'VG+'
python3 vinyl_suite.py watch check --refresh
```

The watch example is a configuration illustration: replace catalog number/format with verified seller metadata, and set your actual ceiling. Accents and spelling differences need identity review; the matcher is intentionally conservative.

Existing snapshot conversion (no network call):

```sh
python3 vinyl_suite.py export --input Record-Selector-Catalog.json --out private/record-selector
```

This preserves original timestamps and coverage; it does not refresh old stock. The earlier October 8, 2026 snapshot contained 25,000 products, including 8,862 available, against a store-advertised 25,001. Never label that snapshot complete. This repository contains no live store inventory.

Individual launchers: `catalog_export.py`, `memory_matrix.py`, `experience_explorer.py`, `record_watchlist.py`, `site_finder.py`. They invoke the same core. Example: `python3 catalog_export.py --input catalog.json`; `python3 memory_matrix.py view`. Add `--state /path/to/memory.json` to select a shared database. The all-in-one CLI requires global `--state` before the module name.

## What to open

- `Control-Hub.html`: offline launch/reference hub, state inspection and reusable prompts. It downloads a memory copy when you explicitly edit it. It does not run Python or scour websites in the browser.
- `legacy/Vinyl-Scout.html`: original scoring workbench, still available for catalog import and manual evidence-backed assessments.
- `docs/PROTOCOL.md`: whole vinyl research protocol and scoring rules.
- `docs/INTEROPERABILITY.md`: canonical formats, module routing, merge rules, and memory handoff.
- `docs/OPERATIONS.md`: command reference, scheduling, checkpoints, and limitations.
- `docs/RECOVERY.md`: known error handling and safe recovery paths.
- `docs/OUTPUT-FORMAT.md`: consistent research tables and ledgers.
- `prompts/`: bootstrap and all five AI operating prompts.
- `templates/`: empty shared memory, schema descriptions, and data examples.

## Watch scheduling

Watch checks are read-only. Configure exact targets and retailers, test one check, then use your OS scheduler to invoke `watch check --refresh` daily. `docs/OPERATIONS.md` has Linux/macOS and Windows examples. Alerts are written to `private/watch-report.json`; external email/push delivery is not configured. An AI with a scheduling feature may instead use `prompts/WATCH.md` and a durable copy of your target configuration. No watch is running merely because this ZIP was downloaded.

## Memory and learning

Explicit preferences outrank inferred patterns. Feedback contributes a transparent smoothed weight `(likes − dislikes)/(feedback count + 3)` for each user-supplied tag. It is a revisable taste hypothesis, not a trained recommender, probability, or permanent identity. Session mood stays session-scoped. Recipients have separate subjects. No Spotify inventory is invented; import an actual export if your connector cannot enumerate it.

`memory forget ID` deactivates a preference/feedback entry and recomputes learning. It does not erase audit history or backups. For complete deletion, remove the entry and its historical copies deliberately; see recovery guidance. `memory restore BACKUP` restores data while retaining a new audit event and backing up current state.

## Privacy, testing, reuse

The repository is public. Personal memory, collection data, catalog snapshots, reports, credentials, and logs belong under ignored `private/`. Packaging uses an explicit source allowlist and excludes private state. Blank templates are public. The original protocol's artist examples are retained; the collector name and destination are replaced with configurable placeholders.

Run `python3 -m unittest discover -s tests -v`. Run `python3 build_packages.py` to rebuild complete and individual ZIPs plus the single-file AI manual. GitHub Actions runs tests on pushes and pull requests. Local mocked tests do not certify a live retailer, current stock, exhaustive internet coverage, or OS scheduler delivery.

Source code and original documentation are available for unlimited reuse under the MIT license. Provider limits, retailer access rules, and third-party catalog rights still apply. No purchase, seller message, account modification, login, or payment occurs.


---

Source: docs/INTEROPERABILITY.md

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


---

Source: docs/OPERATIONS.md

# Operations and scheduling

## Commands

`python3 vinyl_suite.py --help` and each subcommand's `--help` list every argument. Use absolute paths in scheduled jobs. Python has no third-party runtime dependencies.

- Export: `export --url HTTPS --currency USD --sitemap --max-pages 100 --max-products 5000 --out DIR`. Compatible public Shopify endpoints only. `--sitemap` traverses public product sitemaps, fetches missing listed products up to the cap, and records gaps. Request timeout 30s; transient 429/5xx/network retries twice with bounded backoff; inter-request pause .3s. Large sites can take hours. No claim to recover unpublished inventory. A pagination ceiling remains a coverage warning even if sitemaps recover an extra product.
- Offline conversion: `export --input catalog.json --out DIR`. CSV input has unknown overall coverage; it cannot recreate sold-out records absent from that CSV. Input timestamp is preserved.
- Memory: `memory init`, `memory view`, `memory set KEY VALUE --subject self --source TEXT [--inferred]`, `memory feedback RECORD --rating 1 --tags TAG,TAG --reason TEXT`, `memory forget ID`, `memory restore BACKUP`, `memory import-items collection FILE`, `memory import-items assessments FILE`.
- Exploration: `explore` prints the questionnaire; fill `--mood`, `--experience`, `--energy`, `--lyrics`, `--novelty`. Results are stored in sessions plus an output JSON. The CLI creates a heuristic plan; AI listening research determines actual artist/release fits and explicit preferences.
- Watch: `watch add`, `watch list`, `watch pause ID`, `watch resume ID`, `watch check --catalog FILE [--catalog OTHER]` or `watch check --refresh`. Refresh scans each registered compatible store once. `--max-pages` can cap work but gaps remain explicit. Check reports are snapshots. Each change/restock/price signature alerts once while it remains qualified; a missing/failed snapshot can reset qualification and cause a later repeated alert, so verify coverage.
- Sites: `sites queries --genre TEXT --region TEXT`, `sites add URL --name TEXT --adapter manual|shopify --currency USD --evidence TEXT`, `sites list`, `sites probe URL`. Query generation is offline; actual internet search is an AI task. Probe checks homepage/robots reachability and reports raw robots content for operator review; it is not a robots-policy interpreter or legitimacy validator.

No tool purchases, sends messages, enters credentials, or modifies external accounts. Public GET extraction respects reasonable limits; inspect source terms/robots and use an authorized export when extraction is disallowed or blocked. Do not evade blocks.

## Set up a watch

1. Resolve artist, recording/version, edition identifiers, format and acceptable condition. Name-only ambiguous targets stay research leads.
2. Set item versus landed price ceiling and currency. Landed mode requires shipping/tax estimates; these are assumptions, not a checkout quotation.
3. Add retailers and adapter/currency. Verify each is useful and legitimate. Manual sites are not fetched by the CLI; AI search covers those separately.
4. Run `watch check --refresh` once and inspect report coverage, errors, matching metadata and prices. A fresh timestamp is under 24 hours; future/naive timestamps need correction.
5. Choose scheduler below. A sleeping laptop or disabled scheduler cannot check stock. No external notification channel is installed. Review new alerts in the report or connect a delivery mechanism deliberately.

## Linux/macOS daily job

Example paths below are placeholders. Use `crontab -e`; replace paths with your actual Python and extracted toolkit paths:

```cron
0 9 * * * /usr/bin/python3 /absolute/path/vinyl_suite.py --state /absolute/path/private/memory.json watch check --refresh --out /absolute/path/private/watch-report.json >> /absolute/path/private/watch.log 2>&1
```

Cron uses the host's configured timezone. Set the host to your intended timezone (America/Denver for this collector). Do not run parallel jobs against one state file. Ensure the first check completes within the chosen interval.

## Windows Task Scheduler

Create a daily task. Program: actual full `python.exe` path. Arguments:

```text
"C:\path\vinyl_suite.py" --state "C:\path\private\memory.json" watch check --refresh --out "C:\path\private\watch-report.json"
```

Set “Start in” to the extracted directory; use the machine's desired timezone; configure the task to avoid overlapping instances. Test using “Run” and inspect the report. Standard output is not a push notification.

## AI scheduled task

Use `prompts/WATCH.md` with explicit target constraints, price ceilings, a cadence, durable state access and desired delivery. Test harmless access to required connectors first. A provider must actually confirm task creation. If the provider has no scheduler, use the OS schedule; never promise background work from a prompt alone. A scheduled AI search may use credits/provider limits.

## Checkpoints and export failure

The scanner finishes a partial result when a page fails. `export_catalog` writes full JSON before CSV and manifest; interrupted export can leave an incomplete output directory. A valid manifest hashes every expected file. Re-run from full JSON to repair CSV/manifest. Scanning itself has no on-disk page-by-page resume checkpoint in v2: if the process is killed before `scan` returns, redo the scan or use your prior snapshot. Do not pretend interrupted data was saved. Keep large seller exports separately.

## Package and GitHub

`build_packages.py` creates six ZIPs, each individual ZIP carrying the whole shared implementation, documentation and original workbench so it works alone without missing cross-module links. The individual filenames identify entry points; the complete ZIP is the recommended single download. The single-file AI manual concatenates the actual protocol/contracts/prompts, not a shortened description. Build output is reproducible from repository sources and contains SHA-256 inventories. No private state or live catalog is packaged. GitHub “Code → Download ZIP” also downloads source. CI runs tests but does not schedule a watch or publish your personal memory.

## Provider-neutral reuse

Keep toolkit + latest memory + source catalog + report/evidence ledger together. AI providers differ in ZIP/file/Python/network/scheduling support. Select the capability tier honestly. An uploaded ZIP does not install a connector. A prompt can route available tools; it cannot manufacture missing tools. The protocol is usable by text-only AI through the combined manual, while code execution requires Python. Same output structure across providers keeps data portable.


---

Source: docs/OUTPUT-FORMAT.md

# Standard output

Lead with practical priorities and the coverage limit. Default to available stock; show sold-out research separately when requested.

Genre coverage table: genre/subgenre, retrieved count, available count, assessed count, unmapped ambiguity, most promising research leads. Preserve genre overlap; explain that overlapping counts cannot be added to total unique records. Show zero matches.

Recommendation table: artist/release, exact edition/format/catalog number, media/sleeve, current item price/currency and timestamp, purpose/recipient, L/G/C/A/R/U/I/V/Q, evidence confidence, short reason, direct listing link, verification needed. Unknown is an em dash. Keep personal, gifts, objective merit, resale research, affordable discoveries, avoid-at-this-price, and sold-out watchlists separate. Do not mix asking-price bargains with verified below-market value.

Evidence ledger: assessment ID, listing ID/variant/release ID, claim, source URL, accessed date, seller versus independent evidence, asking versus completed sale, sale date/grade/edition/currency/fees, contradictions and confidence. Save as JSON/CSV. A search snippet is a lead, not verification of a page's full contents.

Resale worksheet: item + incoming shipping + tax + cleaning/insurance; credible conservative sold-price scenario; actual or disclosed assumed fees; outgoing subsidy + packaging; net proceeds; profit; break-even; inflation/opportunity-cost assumptions; liquidity; repress/substitute risk; falsifiable thesis. No 50–60-year price promise.

Discovery output: session intent, 3–5 style pathways (familiar/adjacent/stretch/wildcard), specific artists/releases, why each fits, documented listening references, accessible auditions, matching stock if available, and 1–3 feedback questions. Admit unlistened audio. Record reaction after audition.

Watch output: check timestamp, sources successfully checked plus failures/limits, target-by-target matches, exact identity constraints, price basis, currentness, lead/qualified status, new alerts, prior alert deduplication, and queued broader web queries. No match means only no match in checked sources.

Site output: broad/niche coverage, retailer URL/location/specialty, why useful, source evidence, destination shipping status/cost, grading/returns, authenticity/identity concerns, stock freshness, usable extraction adapter and next action. Reachable does not mean reputable.

Session handoff: memory revision, confirmed changes, inferred hypotheses, newly owned/ordered records, rejected suggestions and reasons, unresolved identities/market claims, watch/source changes, files to retain. Export a full data ledger even when readable report is batched; report exactly which rows were screened versus deeply verified.


---

Source: docs/PROTOCOL.md

# Vinyl Scout — standard protocol, v1.0 (preserved)
Use this protocol for every record-store, seller, marketplace, catalog, or individual-release link supplied in this conversation. Research only; do not purchase or message sellers without explicit instructions. Updated October 8, 2026.

## Objective scope and listener profiles
Survey ALL major music categories before personalization. Find records that earn their place through repeated listening, musical/cultural influence, meaningful gifting, unusual artistic interest, collector interest, or defensible net resale economics. Keep those purposes separate. Currency USD; shipped destination configured in private memory. Prefer great copies of great music over superficially scarce records. Prioritize low-cost discovery because funds are constrained; ask budget and gift deadlines when an actual purchase basket depends on them, without delaying research.

Example collector: emotional, atmospheric, transportive electronic journeys; melodic bass/dubstep, euphoric trance/progressive, melodic/deep house, cinematic downtempo, experimental bass, IDM/electro. Known affinity: Seven Lions, Porter Robinson, Above & Beyond, Lane 8, Kasbo, older Illenium, deadmau5, Eric Prydz, Afterlife, CharlestheFirst, Of The Trees, Liquid Stranger, Nora En Pure, Spencer Brown. Specific interest: Jean-Michel Jarre Oxygène, THISISRULES / RULES; Compact Demons EP with Legowelt remix. An artist spelling or same-name artist is not an identity match.
Dad: Boston, Rush, Phil Keaggy; America is an additional artist watch target (recipient not yet specified); adjacent prog and musicianship as tentative exploration, not established favorites.
Mom: Steely Dan, Journey, Keith Green; adjacent jazz-rock, sophisticated pop and Christian singer-songwriter as tentative exploration.
Friends: separate classic hip-hop (Biggie, Mobb Deep), contemporary R&B (Chris Brown, Jhené Aiko), and John Mayer/singer-songwriter preferences. Do not assign every artist to every friend. Explicit-content suitability is recipient-specific.

## Workflow / reusable research prompt
1. Resolve source, seller location, catalog scope, availability, and shipping destination. Capture an ISO timestamp, extraction route, pages and counts; exclude sold-out products from buyable recommendations. Keep them in a clearly separate watchlist. If an extraction hits a limit, report the gap. Never turn collection membership or a search result into a complete Spotify inventory.
2. Taste inventory: use authorized Spotify tools for saved tracks, albums, followed artists and playlists. Record actual item coverage and denominator. If enumeration is unsupported, say so. Accept a user export and deduplicate by track ID; classify primary genres plus secondary styles with confidence and unmapped rows. Artist genre is a proxy, not track-level truth. Do not invent counts, percentages or listening-history metrics. A favorites list supports provisional matching, not a statistical genre analysis.
3. Normalize every item: artist, title, format (LP/12-inch/7-inch/CD), version/remixes, label/catalog number, country, pressing year versus original album year, identifiers, runout, media grade, sleeve grade, comments, current price, availability and direct URL. Parse the description when the display title omits the artist. Keep originals, reissues, remixes and same-name artists distinct. Treat stock photos, incomplete tracklists, $0 listings and contradictory metadata as verification flags.
4. First cover Electronic (trance/progressive, house/deep/melodic, techno/acid, ambient/downtempo, IDM/electro, breaks, bass/dubstep, drum & bass/jungle, disco/experimental), Jazz (traditional, bebop, modal, fusion, spiritual, free), Rock (classic, prog/art, psychedelic, alternative/indie, punk), Metal (heavy, thrash, doom, black/death, experimental), Hip-hop, Soul/R&B/Funk, Pop, Country, Folk/Americana, Blues, Reggae/Dub/Ska, Classical, Gospel/Christian, World/International, Soundtracks/Library and Odd/Experimental/Spoken word. Genres overlap. Show zero matches and unmapped records; do not force uncertain styles into one genre. Then categorize comprehensively: personal core; personal exploration; Dad; Mom; classic hip-hop friends; contemporary R&B friends; singer-songwriter friends; collector/resale research; inexpensive curiosities; avoid at this price; sold-out watchlist; requested artists not found. Allow overlap. Include mainstream affordable gems as well as obscure finds.
5. Evaluate musical fit from supplied tastes, actual tracks/remixes and credible listening references. Describe why the exact release fits. Never claim to have listened to unavailable audio. Identify which single version the user wants and whether the vinyl contains it.
6. Verify collector candidates: use exact Discogs release identifiers and runouts; recent completed sales of comparable grade/edition; at least two independent evidence chains when a substantial purchase depends on value. Count records sold, dates, condition and fees. Asking prices are not sold prices; median aggregates are not condition-adjusted valuations. A promo, autograph, colored vinyl, age, low seller stock or low pressing count does not independently establish rarity or demand. Artist/label sources establish edition claims; signatures need provenance and photos.
7. Score transparently, keeping unknowns blank. Sort differently for each purpose. Report base observations separately from judgments and forecasts. Avoid decimal precision. Use a purpose-specific weighted score only when all required inputs are available; missing inputs must not silently get zero or average.
8. Predictive assessment: if a sufficient exact-edition sales time series exists, analyze repeat sales, grade-adjusted median trend, sales frequency, realized spread, available supply, repress history and demand proxies. Validate on held-out dates before describing a model as predictive analytics. Otherwise give scenario analysis and a hypothesis, not a trained forecast or numerical probability. Consider artist/label longevity, genuine musical relevance, playable condition, substitute reissues and buyer liquidity. Explicitly state what would disprove the thesis.
9. Cost and resale: landed cost = item + allocated incoming shipping + tax + insurance/cleaning. Net proceeds = sale price × (1 − total platform/payment fee rate) − outgoing postage subsidy − packaging − other costs. Break-even price = (landed cost + sale-side fixed costs)/(1 − fee rate). Adjust future net proceeds for inflation and opportunity cost. Use actual platform rates when acting; user-editable rates are assumptions. Do not fabricate 50–60-year prices. Musical and emotional value may remain even if financial value falls.
10. Output: short buying priorities; category tables with individual scores and edition/condition; fuller searchable inventory; market evidence ledger; missing targets; seller questions; proposed baskets with explicit pre-shipping totals and no implied reservation. Recommend only what the evidence supports. Preserve protocol and profile for subsequent links in this conversation.

## Multi-score rubric (1–5; — means unknown)
L, listening fit: 5 explicit target/very close taste; 4 strong adjacent fit; 3 credible exploration; 2 weak; 1 mismatch. Curatorial judgment, not a measured probability.
G, recipient fit: same scale, evaluated for a named recipient. A family gift should ideally be VG+ or better media and a presentable sleeve; downgrade gift recommendation for damaged sleeves even if musical fit remains high.
C, playback-condition proxy: M/NM=5, VG+=4, VG=3, G+=2, G/F/P=1. Seller-reported visual grade, not a playback test. Sleeve grade is displayed separately. Generic sleeves are ordinary for some DJ singles and should not automatically penalize them.
A, affordability: ≤$5=5, ≤$10=4, ≤$20=3, ≤$35=2, >$35=1. This is a budget score, not evidence of a below-market bargain. $0 is invalid until confirmed.
R, scarcity: 5 documented hard-to-source exact edition with persistent demand; 4 verified limited edition with market scarcity; 3 distinctive edition, availability unresolved; 2 widely obtainable; 1 abundant. Limited run alone supports an edition signal, not a scarcity score. Leave R blank without evidence.
U, resale underwriting: 5 multiple recent exact-edition sold comps, conservative net margin and healthy liquidity; 4 good evidence with one modest uncertainty; 3 thin but credible comps; 2 no defensible margin; 1 poor economics. Leave U blank where evidence is insufficient. No candidates in the initial scan qualify as a fully underwritten investment.
Evidence: A=copy-level verification + corroborated edition; B=seller metadata plus independent edition evidence; C=seller metadata only; D=unresolved or conflicting. Confidence is not a numeric probability.

Suggested weighted selection once inputs are known: personal 50% L + 30% C + 20% A; gifts 50% G + 25% media condition + 25% sleeve/presentation; resale 40% U + 25% liquidity + 20% scarcity + 15% condition. Do not use the resale formula with missing inputs. There is no all-purpose 'best record' score.

## Long-horizon collection practice
Keep clean playback copies and protective sleeves; handle at edges, store upright in a stable dry indoor environment away from heat/sunlight; retain inserts, hype stickers and receipts. Do not use speculative scarcity to justify a record you would regret owning if its resale price halves. Ask for play grading when surface noise could spoil quiet ambient music. A 60-year horizon increases uncertainty rather than guaranteeing appreciation.

## Objective merit and market scoring additions
I, influence/artistic significance (1–5): evaluate documented musical influence, compositional/performance distinction, or release importance across its own genre. A 5 needs specific evidence, not fame alone. Unknown stays blank. V, price value (1–5): exact-edition, condition-adjusted price versus credible market evidence; ≤$5 is affordability, not a value score. Q, liquidity (1–5): frequency of comparable completed sales; high wantlist counts alone do not establish liquidity. Add research leads for all genres, even those outside personal taste. Odd/experimental includes sound collage, musique concrète, field recordings, free improvisation, outsider art, library music and spoken word; novelty is not automatically musical merit.

## Implementation contract
The delivered tool is a portable research workbench plus a standard-library Python catalog scanner, not an installed MCP connector or an autonomous browsing service. The browser workbench imports catalog JSON or CSV and exports enriched JSON; the Python scanner reads compatible Shopify catalogs. Non-Shopify sources require authorized browsing or a source-specific adapter. Source-link prompt generation prepares the research task but does not secretly perform it. Music merit, personal/gift fit, verified scarcity, price value, underwriting and liquidity are analyst-entered evidence-backed scores. Only condition and affordability are mechanically scored. There is no complete Spotify saved-track enumeration in the present connector result. Do not invent one.


## Toolkit v2 integration and overrides
The preceding full v1 research method is preserved. The five-module v2 toolkit extends its implementation contract; read INTEROPERABILITY.md, OPERATIONS.md, RECOVERY.md, OUTPUT-FORMAT.md and all module prompts. The artist lists above are examples; actual user preferences, budgets, destination and recipients come from private canonical memory. Do not treat examples as an exhaustive taste inventory or activate watches without configured editions/ceilings. Active-stock search remains default. Broader full-catalog and sold-out research is separate and expands only when requested.

Memory keeps explicit statements, inferred hypotheses, session moods, recipient subjects, collection statuses, evidence, source registry and watch constraints separate. Changes are auditable and reversible. Adaptation uses interpretable feedback weights, not a trained model. Exploration may introduce any genre and should use auditions and specific reactions. Site Finder uses actual available search/browsing tools; the local query generator does not perform internet search. Watch checks run only when invoked or scheduled in a configured environment; price ceilings, condition, currentness, currency and exact edition constraints matter.

Use UTC timestamps in files and user-local timezone for schedules. Output uncertainty, count gaps and unavailable capabilities plainly. A finite tool cannot guarantee exhaustive historical/private inventory, full-internet coverage, universal AI compatibility or all possible future error recovery. Preserve raw inputs and use documented fallback mechanisms. Private memory stays out of public repository/package artifacts.


---

Source: docs/RECOVERY.md

# Recovery guide

Known failure paths and checks are below. No finite document can guarantee recovery from every future website, provider or OS change. Preserve raw inputs and state before adapting an unsupported source.

| Symptom | Meaning | Safe next step |
|---|---|---|
| File not found / ZIP inaccessible | AI cannot access attachment or path | Inventory actual files. Reattach core/manual and data separately; never claim it read missing files. |
| No Python / unzip tools | Provider cannot execute scripts | Use combined AI manual and attach JSON/CSV directly. Run CLI on a Python-enabled computer. |
| No web/network capability | Query generation works; live search does not | Use supplied snapshot; mark stale stock; run Site Finder/Watch prompts in web-enabled AI. |
| HTTP 401/403/CAPTCHA | Access/auth restriction | Stop; use public browsing or authorized seller export. No retry evasion or guessed credentials. |
| HTTP 404 products.json / HTML instead of JSON | Source is incompatible or feed absent | Use manual adapter and source-specific authorized extraction. Empty response is not an empty catalog. |
| HTTP 400 at deep page | Pagination limit or invalid route | Save partial output. Try public sitemap reconciliation/export. Compare counts; keep incomplete status. |
| HTTP 429 / 5xx / timeout | Rate limit/transient issue | Built-in bounded retries; reduce frequency, wait, retry later. Do not launch aggressive parallel scans. |
| Same products on later pages | Pagination ignored/repeated | Stop with `repeated_page`; inspect source, use export/sitemap. |
| Short final page | Feed exhausted | Complete only for that public route, absent observed gaps. Compare advertised count if known. |
| Sitemap empty/fails/capped | Reconciliation incomplete | Preserve gap; do not infer missing records are sold out. Manual source count/export. |
| Missing/deleted/unpublished record | Cannot be enumerated through public feed | Historical evidence/watch queries; never promise full private catalog. |
| Product has multiple variants | Representative row might be another edition/copy | Inspect raw variants; require exact variant/format/price before buying alert. |
| Missing stock/price/currency or price $0 | Unsupported buying evidence | Keep unknown-stock rows separate; lead only. Verify denomination; no FX conversion without dated rate. |
| Old snapshot | Availability may have changed | Refresh leading candidates; old catalog conversion does not refresh timestamp. |
| Accented titles / aliases / spelling variations | Conservative watch identity matcher can miss | Resolve aliases manually, add alternate watch or exact ID. Do not weaken exact-edition constraints silently. |
| Claimed signed/promo/limited edition | Collector marketing may not establish rarity/value | Obtain provenance/photos/edition evidence/sold comps before R/V/U score. |
| CSV spreadsheet formula prefixes | Potential executable cell text | Exporter prefixes risky text; full JSON retains original. Recheck text when importing back. |
| CSV lacks unavailable rows | Active-only input | Supply original full JSON; cannot infer historic stock from available CSV. |
| Corrupt JSON / unsupported schema | State cannot be safely read | Preserve original; restore known-good backup or migrate a copy. No silent reset. |
| `memory init` file exists | Existing state protected | Use view, not init. Rename only if deliberately starting a separate database. |
| State locked | Another mutation or stale lock | Check PID in `.lock`; wait for active process. Remove lock only when process is confirmed stopped. |
| Conflicting state copies | Diverged histories/revisions | Compare IDs and evidence on copies; explicit merge, not last-write-wins. |
| Lost preference / undesired learning | Mistagged feedback or superseded statement | Deactivate by ID; confirm source; restore backup if needed. Inferences never replace explicit preferences. |
| Want complete data deletion | Deactivation retains history | Remove matching data from state, backups, exported copies and AI uploads deliberately. Audit what remains. |
| Watch no match | Limited checked-source result | Inspect coverage, identity and manual-site queries; not proof of worldwide unavailability. |
| Duplicate/restock alert | Failed source or stock transition reset signature | Check report coverage; investigate actual live listing before treating it as new inventory. |
| No notifications | No scheduler/delivery configured | Confirm job exists and runs; inspect logs/report. Set delivery separately. |
| Partial export directory | Interrupted write or storage failure | Verify manifest hashes; re-export existing full JSON to a new directory. |
| AI context limit / long catalog | Partial read or report truncation | Batch deterministically by stable IDs. Preserve full row ledger with screened/researched status and resume checkpoint. |
| AI fabricated execution or research | Capability/evidence mismatch | Require actual files/counts/tool results and source timestamps; discard unsupported claims. |
| GitHub permission/branch conflict | Cannot safely publish over current head | Inspect current ref, preserve work, use new branch/PR if needed. Never force-push blindly. |

State writes use a same-directory temporary file and atomic replacement. A disk-full/permissions failure may prevent backup/export; retain existing files and repair storage before retrying. The CLI returns exit 2 for handled validation/input errors; unexpected exceptions are not converted into a success.

Meaningful verification: mock feed limits and errors, strict stock/price handling, variant selection, CSV safety, state lock/backups, feedback reversibility, exact watch constraints, stale/currency gates, alert transitions, and package privacy allowlist. Test a real source after adapter changes. Local tests cannot certify website completeness or market value.


---

Source: prompts/BOOTSTRAP.md

# Paste this to start

Use the attached Adaptive Vinyl Finder toolkit as my portable vinyl research system. Inventory and extract actual attachments if supported. Read README, docs/PROTOCOL.md, INTEROPERABILITY.md, OPERATIONS.md, RECOVERY.md, OUTPUT-FORMAT.md, and the relevant module prompts. If ZIP extraction is unavailable, read AI-Reuse-Manual.md and ask for only the inaccessible required data. Do not claim missing files were read or scripts were run.

My latest explicitly selected memory.json is canonical. Read actual records, schema, revision, subjects, explicit preferences versus hypotheses, collection statuses, watch targets and source registry. Read catalog timestamps, counts, stock fields and coverage; a preview is not a full parse. Preserve my other-chat handoff as sourced context, without narrowing the objective genre survey.

State your available file-reading, Python, web-search/browsing, music/marketplace connector and scheduling capabilities. Run standard-library scripts only where available and authorized; no installation/MCP or always-on monitoring is implied. Use existing appropriate tools, and record access limitations. Any AI provider may follow the text protocol, but missing capabilities need honest fallback.

Route requests: retailer/catalog links → exporter + genre survey; mood/experience → exploration questions and style/artist research; explicit reactions → memory; expensive/unavailable exact releases → watch configuration/check; retailer discovery → Site Finder. Reuse source snapshots and state across modules. Active stock is the default; sold-out/historic research remains separate and only expands when requested. Survey all major categories plus Odd/Experimental before personalization.

Keep musical significance, personal fit, gifting, affordability, verified market value, exact-edition scarcity and net resale economics separate. Unknown scores remain blank. Verify source claims, live leading stock/price, edition and sold comps appropriately. Do not invent listening, Spotify inventory, sales evidence, predictive models, trained personalization, or internet completeness. No purchases, seller messages or account changes.

Save source/evidence ledger and updated memory, revision and concise change log. Return downloadable updated files when supported; otherwise give explicit portable JSON/text. Keep private state local; do not publish it. Read-only research may proceed autonomously. At setup, confirm files/actual counts/capabilities/material gaps, then await my research request unless I supplied one.


---

Source: prompts/EXPLORE.md

# Experience Explorer

Read explicit preferences, feedback hypotheses, collection and current catalog/source coverage. First ask up to three easy questions covering (1) mood and desired experience, (2) energy and lyrics/instrumental, (3) familiar/adjacent/adventurous exploration. Use session defaults from current context if supplied. Budget/format matter when making a purchase basket; do useful research while gathering them.

Translate answers into musical attributes: texture, space, rhythm, harmonic color, vocals, complexity, intensity, emotional arc and production era. Use existing available music tools, actual listening references, credible genre/artist sources and web searches. The CLI explore plan is a heuristic starting point, not final artist truth. Mood synonyms, contradictory goals and negative constraints need human/AI interpretation rather than forced tagging.

Offer 3–5 pathways spanning familiar, adjacent, stretch and wildcard styles. Stay open across electronic subgenres, jazz, rock, metal, pop, country, folk, soul/R&B/funk, hip-hop, blues, reggae, classical, regional/world traditions, gospel, soundtrack/library and experimental. For each pathway provide 2–4 artists or exact releases, why they fit, accessible audition references, and relevant available vinyl where possible. Tell me when stock/edition has not been checked and do not claim to have listened to unavailable audio. Include non-buyable discovery leads separately.

Apply the same evidence/scoring discipline. Ask which aspect worked or failed after audition; record precise feedback, adapt the next round and save the session. Keep artistic merit separate from personal affinity. Route unavailable/over-budget desired exact releases to Watch; unexplored sources to Site Finder. Export updated memory and findings.


---

Source: prompts/EXPORT.md

# Catalog Exporter

Apply the whole protocol. For this retailer, first identify extraction route and scope. If compatible public Shopify feed access is permitted and Python/network are available, run catalog_export.py or vinyl_suite.py export, optionally reconcile product sitemaps. Otherwise use authorized browsing/source-specific extraction or request a seller export. Do not invent commands, credentials, undocumented bypasses or complete stock coverage.

Output active.csv, full-catalog.json, sold-out.csv, unknown-availability.csv and manifest.json. Preserve source timestamps, variant metadata, exact IDs, provenance, failed pages, repeated pages, count mismatches and limits. A full JSON means the entire retrieved public dataset, not guaranteed complete private/historical inventory. Confirm actual parsed row counts and reconcile advertised source counts if available. Existing JSON conversion preserves old timestamps. Active-only CSV cannot recreate unavailable records.

Default analysis is active-only. Use full JSON for sold-out research when requested and keep results separate. Refresh leading prices/availability; never equate feed claims with reserved stock. Preserve unmapped genres and all major categories. Connect findings to assessments, collection dispositions, watch targets and source registry using stable identifiers.


---

Source: prompts/MEMORY.md

# Memory Matrix

Use memory.json as portable canonical state; keep a local backup, revisions and changes. Extract preferences, constraints, desired experiences, named-recipient tastes, budgets/deadlines, formats/pressings, owned/ordered/wanted/rejected/sold items, recommendations/evidence, sources and watch targets from actual statements/results. Attribute each to its source and date. Do not infer purchase or ownership from a positive reaction. Keep different friends separate.

Explicit user corrections supersede previous values for the same subject/key. Hypotheses stay labeled inferred and never replace explicit statements. Mood applies to this session unless the user says it is persistent. Record positive/negative feedback with record identity, specific tags and reason; dislike of a pressing's noise does not prove dislike of its genre. Use the CLI's interpretable smoothed tag weights only as provisional clues, not a trained model or probability.

After each meaningful research/audition session, summarize confirmed changes, inferred patterns and unresolved conflicts; write updated memory with audit history and download link if supported. Avoid repetitive questions already answered. Ask a short discriminating question when uncertainty would change the next choice. Collection duplicate suppression and recipient-specific scoring are required before final recommendations. Deactivate mistaken feedback/preferences by ID; restore backups deliberately. Never claim a provider automatically persisted my state across chats.


---

Source: prompts/SITES.md

# Site Finder

Search the internet when I request record sources, either broadly or by genre/region/edition. Read memory constraints and existing source registry, then generate/run a diverse query matrix rather than repeatedly recommending only famous marketplaces. Use available web/search tools, record-store directories, label/distributor artist pages, independent specialist shops, local stores with mailorder, Bandcamp label stores, and reputable authorized marketplaces. Include niche regional-language searches where useful. Existing tools and knowledge are leads; verify current sources.

Cover general used/new, electronic subgenres, jazz, classic/prog/indie rock, metal, hip-hop/R&B/soul/funk, pop, country/folk/Americana, blues, reggae/dub, classical/gospel, regional/world traditions, soundtracks/library and odd/experimental as appropriate. Personal favorites do not cap scope. If I request one genre, deepen that area while offering a few useful adjacent specialist leads.

For each useful site, open primary pages for identity/location, inventory specialty, shipping destination, grading/returns, stock freshness and extraction route. Corroborate dubious or material claims. Distinguish candidates from verified useful sources; reachability and low prices do not establish legitimacy. Do not invent current shipping prices, reliability ratings or that the entire internet was scoured. Cite dated evidence and summarize where coverage is thin.

Register relevant sources with adapter manual/shopify, currency, specialty and verification evidence. Reuse catalogs rather than fetching redundantly. Forward source results to Exporter/Explorer/Watch as relevant. Return a broad/niche shortlist with direct links and what each adds. No accounts, messages or purchases without explicit instructions.


---

Source: prompts/WATCH.md

# Record Watchlist

Read enabled exact targets in durable memory.json: artist/recording/version, edition/catalog/release/variant identifiers, format, condition, destination, ceiling/currency and item versus landed basis. Resolve ambiguous targets before claiming a buyable match. If no targets or ceilings are configured, collect them; do not invent a watch for an example artist.

For one check, refresh compatible registered feeds once each if supported. Run public web searches for missing targets, alternate spellings and authorized marketplace/retailer listings. Use Site Finder for specialist/label/mailorder leads. Read actual listing pages; verify edition, current stock, currency, grade and shipping estimates. Sold-out entries and over-ceiling records remain separate leads. Inspect false positives, aliases, reissues, promos, remixes, CDs and unrelated same-name artists.

Report qualifying new listings, meaningful price drops/restocks and unresolved research leads, with direct links, timestamp, checked sources/failures/coverage and total-cost assumptions. No match means only no match in the checked sources. Persist observations and alert deduplication. Alerts are seller claims pending checkout/copy-level verification; no purchases or seller messages.

Background checks require an actually configured scheduler, durable state and source access. If requested and supported, configure a practical cadence using the provider scheduler after testing required app access; otherwise give the OS command. State what delivery exists. A prompt/ZIP alone does not monitor between chats. If run as a scheduled task, notify only about meaningful newly qualifying findings; remain quiet for unchanged/no matches, while preserving diagnostics where supported.
