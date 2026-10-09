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


## Version 2.1 extension

Read [RESEARCH-WORKFLOW.md](RESEARCH-WORKFLOW.md) for the canonical staged research process, three-tier exploration, two additional helper CLIs, source/history limitations, curiosity feedback weighting and failed-source watch recovery. This extension supersedes conflicting earlier exploration-size defaults; the original mission and score definitions remain.
