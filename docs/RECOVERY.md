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
