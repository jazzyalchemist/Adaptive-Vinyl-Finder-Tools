# Research workflow — 2.1

## Keep the original mission

Broad objective coverage comes first: electronic subgenres, jazz, rock, metal, pop, country, folk/Americana, soul/R&B/funk, hip-hop, blues, reggae/dub/ska, classical, gospel/Christian, regional traditions, soundtracks/library, spoken/non-music and Odd/Experimental. Multiple categories may apply. Personal taste guides the personal/discovery view, not the whole survey. Separate personal lifelong listening, named-recipient gifts, affordable finds, collectible/rarity leads and evidence-backed resale theses. Artist examples are seeds, never an exhaustive filter.

## Do work once, deepen it when a decision needs it

1. Parse the supplied catalog once. Record source, original observation timestamp, exact scope, stock unknowns and pagination failures. Reuse that snapshot across modules. An active CSV cannot reconstruct sold-out inventory.
2. Use stable source/listing IDs and metadata fingerprints. Compare against the prior research ledger; reuse assessments only for unchanged metadata, with their original evidence dates. A local delta comparison saves processing; it does not magically obtain a retailer delta feed or refresh evidence. Changed price/copy/variant reopens the decision.
3. Treat overlapping genres as annotations. Route missing identity, bad prices, unresolved styles and condition caveats to an exception queue. Repair high-impact candidate issues first; do not resolve every low-priority metadata gap before presenting useful findings.
4. Separate stages: mechanically screened → editorial lead → auditioned/recipient-assessed → exact-edition and current-offer checked → market-underwritten where relevant. Full row coverage is not a claim of full musical review. Tool-generated candidates are not curated purchase recommendations.
5. Create one canonical record/offer card. Refer to it from genre, personal, gift, bargain, exploration and resale views using purpose tags. Different copies/pressings remain separate offers. Avoid repeating long descriptions and all scores in every view.
6. Verify the candidates that can change a near-term decision first. Stop or route to Watch when exact-edition/grade evidence is inaccessible. Old, overseas, differently graded or unknown accepted-offer sales are context, not interchangeable exact sold comps. Do not search endlessly to fill a score.
7. Show coverage, meaningful gaps, next verification action and score confidence. Cite claim-specific pages. Avoid decorative thumbnails unless they depict the exact item; a similar album cover can be misleading.

## Scoring remains multi-dimensional

Keep the original L/G/C/A/I/R/V/Q/U definitions in PROTOCOL.md. Scores are independent ordinal 1–5 assessments, not probabilities. Unknown is blank, never zero. C (seller-stated media grade) and A (item-price bracket in the configured currency) are mechanical aids; neither certifies playback quality or landed value. Default A USD brackets: ≤5=5; ≤10=4; ≤20=3; ≤35=2; >35=1. Other currencies need explicit locally configured brackets, not silent FX conversion.

Attach score basis, evidence date and evidence confidence separately. L is personal expected listening value, not general artistic merit; an unauditioned genre match is only a fit hypothesis. G must name the recipient and have a separate assessment for each recipient. I requires a defensible musical/cultural significance argument. R needs exact pressing and current supply evidence; Q needs comparable completed-sale frequency. V needs comparable current market evidence. U (resale underwriting) needs net proceeds after fees, packing, shipping, tax assumptions, condition/return risk and currency effects. Buying urgency is a separate decision field, not U. It needs evidence for both the reason to act and the cost of being wrong; sales velocity estimates need time series, not a single sold-out label.

Never assign a composite investment score merely because a record is cheap or old. Show objective collector merit alongside personal appeal. Maintain contradictory evidence (repress announced, plentiful substitutes, seller stock unknown) next to scarcity claims. No automatic purchases.

## Three exploration tiers

Default: 12 distinct release leads per tier, 36 total; configurable up/down on request. At most two releases per artist per tier by default; avoid duplicate offers and recycle only deliberate reference anchors. Report a quota shortfall instead of adding unrelated stock. Familiar releases can be calibration anchors, but are not automatically new discoveries. Discovery can reach outside this retailer; distinguish audition-only leads from seller-matched offers.

- **1 — Closest:** progressive house, deep/melodic house, ambient/dub techno and Anjunadeep-like territory, based on explicit private taste/history.
- **2 — Adjacent:** preserve emotional development, atmosphere, texture or hypnotic repetition while shifting rhythm, instrumentation or production language.
- **3 — Furthest, with a clear connection:** jazz, post-rock, modern/minimal classical, electroacoustic and regional traditions where a specific bridge justifies the suggestion. Any genre can qualify with evidence and a useful explanation.

For each release: artist/title, curatorial connection, what changes, audition entry point, unfamiliarity status, catalog offer if present, snapshot versus current stock status, edition/grade caveats, and next action. Tier placement is an explained curatorial judgment, not a measured distance or proof of fit. A metadata rule does not override explicit exclusions or listening feedback; the AI must check both before recommending.

## History and adaptive feedback

Spotify connector samples are samples unless counts, dates, coverage and meaning are actually returned. Saved tracks, current top affinity and repeated plays are different datasets. The Web API long_term is approximately one year, not a measured 2–3-year history. Use listening_history.py with the account's **Extended Streaming History** JSON for dated multi-year events. Basic one-year history is rejected by this importer. Importing tracks does not supply genre labels; optional sourced track mappings or marked artist proxies report mapped versus unknown listening minutes.

A curious reaction is stage `interested` (weight .25); an explicit listened/owned reaction uses weight 1. Existing v2 feedback without stage retains weight 1 for compatibility. Learning is `(positive_mass − negative_mass)/(total_mass + 3)`, tag-level, subject-specific and reversible. It is a heuristic hypothesis, not trained predictive analytics. Owned status never follows merely from a positive reaction. Avoid learning a genre aversion from surface noise or a bad pressing. Optional short question after audition: what worked — rhythm, texture, emotion, vocals, energy — and what failed? Never force a questionnaire when context already answers it.

## Executable helpers

```sh
python3 research_engine.py --catalog private/catalog/active.csv --out private/research
python3 research_engine.py --catalog private/catalog/active.csv --previous private/previous/research-ledger.json --per-tier 12 --out private/research-next
python3 listening_history.py --input private/spotify-history --from 2023-10-09 --through 2026-10-09 --timezone America/Denver --out private/listening
python3 vinyl_suite.py memory feedback 'Artist / release' --rating 1 --stage interested --tags 'spacious,transforming' --reason 'Curious; not yet a confirmed favorite'
```

Keep previous output in a different directory. Research output: canonical research-ledger.json, coverage-ledger.csv, data-issues.csv, exploration-candidates.json, audit-summary.json. Legacy scores remain in JSON for audit; the CSV displays only renewed mechanical C/A and unknown unverified scores. Metadata candidates are a queue for an AI/person, not a final recommendation list. The genre profile is editable and public example data; actual private exclusions/preferences must also be read.

History outputs: listening-profile.json, top-tracks.csv, top-artists.csv. Dates are inclusive in the chosen timezone; rankings use total observed milliseconds, with recorded-event and ≥30-second meaningful-event counts separately. Do not describe these as Spotify's official play counts. Full listening minutes include short/skipped events. Privacy outputs omit IP, username and device fields; raw history stays private. File hashes, time bounds and unknown completeness remain. Windows without timezone database may need timezone support installed; UTC is an honest fallback only with its date-boundary difference disclosed.

## Recovery additions

Unknown/missing timestamps remain unknown on offline imports. Failed/partial watch sources do not reset previous stock observations or create false restock alerts. Fresh complete source absence or fresh explicit sold-out observation can reset an alert; stale snapshots cannot. Watch freshness is currently ≤24 hours and is an operational gate, not a reservation. Migrated v2 watch signatures survive failed checks. Report retailer failures and check final checkout/copy details manually.

For missing history: continue from explicit taste, disclose unmeasured coverage, and request Extended Streaming History only when historical ranking matters. For conflicting genres: preserve multiple tags; do not pick one for convenience. For insufficient exact comps: leave value/resale/urgency unknown and identify what evidence would change the conclusion. For sparse tier stock: offer sourced external audition leads and label them accordingly.
