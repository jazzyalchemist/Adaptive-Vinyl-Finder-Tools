# Evolution roadmap — preserve the collector's mission

Design goal: help someone collect music for a lifetime, give thoughtful records, discover unfamiliar traditions, spot fairly priced interesting copies, and test credible collector/resale theses. Scarcity is one dimension; replacement availability, sound, condition, fit and total cost still matter. A long holding period increases forecast uncertainty. Success is a collection worth living with, plus decisions that can be explained and corrected.

## What exists in 2.1

Seven portable local tools/workflows; active/full/sold-out catalog exports; durable user-managed JSON memory; reversible tag feedback; exact watch constraints; site search plans; catalog issue triage and unchanged-metadata comparison; multi-year listening-history import; three-tier discovery defaults; original evidence/scoring protocol. Current routing is heuristic, not a trained recommendation model. No server, scheduler, notification delivery or checkout automation is running just because files exist.

## Next tools, in dependency order

| Priority | Tool/addition | Decision it improves | Acceptance criterion |
|---|---|---|---|
| 1 | Recording → release → pressing → copy → offer resolver | Is this actually the desired music/version and physical edition? | Never merges CD, remix, pressing variant or differently graded copies solely by title/catalog number; unresolved matches stay explicit |
| 1 | Taste/recipient compiler | Which records suit me or this named person? | Combines explicit preferences, measured history, unfamiliarity and audition feedback with source/confidence; keeps recipients separate |
| 1 | Multi-retailer offer registry | Where is the exact acceptable copy available? | Same-edition offers remain separate; verified currency, timestamps, stock, grades and source failures survive updates |
| 2 | Landed-cart optimizer | Which store combination costs least for the desired records? | Computes real destination shipping/thresholds, taxes/fees and acceptable substitutions; reports optimality scope and unknown costs |
| 2 | Urgency evaluator | Buy now, investigate promptly, watch, or wait? | Urgent label has exact identity, fresh stock, acceptable condition, budget/landed ceiling and documented scarcity/replacement evidence; shows contradictory evidence |
| 2 | Inventory/price/repress observatory | Is scarcity changing or only a seller's claim? | Repeated dated observations distinguish missing/failed feed from sold out, replenishment, deletion and announced repress |
| 2 | Durable watcher and alert delivery | Can a valuable new offer be noticed reliably? | Survives restart, deduplicates alert events, exposes source failures, tests chosen delivery channel, never purchases automatically |
| 3 | Copy-quality and lifetime-care assistant | Will I enjoy this copy for decades? | Quiet-music play-grade needs, sleeve/inserts, cleaning/setup/storage and replacement choices considered separately from monetary rarity |
| 3 | Collector-thesis lab | Does a resale hypothesis hold up? | Exact-edition comparable data, net economics, repress/substitute risk and out-of-time validation; no numeric forecast without sufficient evidence |
| 3 | Coverage/diversity auditor | What would personalized ranking hide? | Maintains genre breadth, minority styles, affordable curiosities and independent artistic merit; reports thin/no-match areas |
| 3 | Feedback experiment designer | What small listening comparison teaches us most? | A short contrasting pair tests one uncertain attribute; curiosity isn't treated as a favorite or purchase |

## Cart optimization: make the promise precise

Each desired release has a set of acceptable pressings/copies and a maximum landed willingness to pay; a gift can require a better sleeve than a personal DJ single. Let x choose one acceptable offer per required item, and y indicate use of a store. Minimize items + each store's actual shipping function + destination taxes/fixed fees, subject to availability, grade, edition, currency, budget and deadline constraints. Compare normalized money using a dated FX source only when currencies differ. Do not mix assumed fee/tax estimates with confirmed checkout totals.

For five to twenty items and a small offer set, enumerate feasible baskets or use a mixed-integer solver with proven termination/bounds. If search is truncated, call the result the best tested basket, not a global optimum. Output the next-best feasible basket, savings, unknown charges and sensitivity: a different shipping estimate or one sold-out copy may change the winner.

Illustration only: Store A sells X=$20 and Y=$20 with $8 shipping, Store B sells Y=$15 and Z=$25 with $8 shipping. Buying X at A and Y/Z at B totals $76; X/Y at A and Z at B totals $81. This is not a current merchant quote. Thresholds/taxes can reverse the choice.

Then evaluate optional cart additions **after** satisfying the requested items. Marginal landed cost = optimized basket with extra item minus baseline basket. An addition can reduce shipping, but increases item spending. Offer it only if it earns its place for musical/collector reasons and respects discretionary budget. Show total outlay and savings explicitly; never imply free shipping makes unnecessary records free. Suppress already owned/ordered copies unless an intentional upgrade/gift is selected.

## Urgency without empty FOMO

Use four actions: **investigate immediately**, **ready for user's buy decision**, **watch**, **wait**. The first is allowed when a promising candidate needs urgent verification; it is not permission to call an unverified offer a bargain. A user-defined emergency threshold can notify about a verified scarce exact edition at or below the ceiling, with fresh stock and acceptable grade. The alert must say what was checked, when, what remains uncertain and why delay may matter.

A single low-stock count, promo stamp, autograph, old release date, colored vinyl or sold-out page does not prove market rarity or urgency. Account for replenishment, equivalent good reissues, repress announcements, actual repeated sale frequency, new supply and personal price ceiling. Keep urgency separate from U, which remains **resale underwriting** in the original score system. No purchase without explicit authorization.

## Lower recurring cost and better reliability

Deterministic parsing, filtering, IDs, scoring eligibility and shipping arithmetic should run in code. Reserve AI work for musical interpretation, ambiguous identity, claims needing research and concise explanation. Cache original source documents and evidence dates; invalidate price/stock quickly and edition metadata more slowly. Reuse unchanged catalog rows instead of resummarizing the entire store for every watch. Source feeds may still require a full retrieval; do not claim a server-side delta API where none exists.

Maintain per-source freshness and failure budgets, conditional requests where supported, adaptive polling, timeouts/backoff and checkpoints. Use a complete slower catalog sweep plus focused checks of high-priority targets between sweeps, subject to retailer access policies. A source failure should produce diagnostics, not a sold-out event. Notifications need a persistent queue/outbox and idempotent event IDs. Test the chosen route before claiming alerts are active. High-frequency polling should be justified by store behavior and actual quotas, not the word “always.”

Track system quality: edition-match precision on a manually reviewed sample; live verification coverage for actionable offers; audition acceptance by tier and recipient; unknown-genre minutes; missed/suppressed alert events; false restocks; measured cart savings; research time per useful decision. Record rejections and reasons, including noise, wrong version, already owned and too expensive. Do not train popularity or investment claims from a small personal sample.

## Future Taskade app: proposed architecture, not deployed

Use Taskade for intent forms/checklists, named-recipient selection, review queues and readable results. An external service can keep the canonical catalog/offer/evidence database, perform code-based research stages, optimize carts and run durable checks. This division is a recommendation based on data volume and reliability needs, not a claim that Taskade cannot do those jobs.

Official Taskade documentation describes API/webhook integration and scheduled triggers. Its September 2, 2026 schedule guide lists 5–30-minute and longer intervals, while an older Help Center page lists hourly and longer. Verify the actual account's plan, quotas, trigger options and delivery latency before promising emergency timing. Schedule frequency is not guaranteed instant detection. Use official docs when implementing, and test one end-to-end job before scaling.

Sources checked October 9, 2026: [Taskade API](https://help.taskade.com/en/articles/8958531-taskade-developer-api), [inbound webhooks](https://developers.taskade.com/docs/api/agents/inbound-webhooks), [current schedule guide](https://www.taskade.com/learn/automation/schedule), [older schedule help](https://help.taskade.com/en/articles/10477405-schedule-automation-trigger). No Taskade resources were created or connected in this update.

Intent checklist: personal collection / named gift / objective collector merit / resale research / exploration / price watch; genres open or constrained; desired recording and acceptable editions; budget and discretionary add-ons; condition floors; destination; deadline; familiarity; owned/ordered exclusions; source scope; urgency threshold. Defaults come from explicit memory, with session overrides. Do not make the user complete every field for an ordinary broad research request.

Data entities: Person, Preference, FeedbackEvent, Recording, Release, Pressing, Copy, Offer, Retailer, Snapshot, EvidenceClaim, Assessment, WatchTarget, ObservationEvent, Alert, Basket, JobRun. Store input hashes and schema/tool versions to reproduce decisions. Use private credentials and scoped tokens; never upload raw listening IP/device history or private recipient data to the public repository.

Proposed sequence: intent → cached catalogs/current offer checks → identity resolution → objective genre/merit screen → purpose-specific views and three-tier discovery → needed evidence → basket comparison → user review; observation events route desired missing/over-budget records to Watch. The next app increment should implement one complete end-to-end retailer/recipient/basket/watch flow with tests before adding many agents or sources.
