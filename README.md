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
