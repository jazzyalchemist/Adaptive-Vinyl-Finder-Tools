# Catalog Exporter

Apply the whole protocol. For this retailer, first identify extraction route and scope. If compatible public Shopify feed access is permitted and Python/network are available, run catalog_export.py or vinyl_suite.py export, optionally reconcile product sitemaps. Otherwise use authorized browsing/source-specific extraction or request a seller export. Do not invent commands, credentials, undocumented bypasses or complete stock coverage.

Output active.csv, full-catalog.json, sold-out.csv, unknown-availability.csv and manifest.json. Preserve source timestamps, variant metadata, exact IDs, provenance, failed pages, repeated pages, count mismatches and limits. A full JSON means the entire retrieved public dataset, not guaranteed complete private/historical inventory. Confirm actual parsed row counts and reconcile advertised source counts if available. Existing JSON conversion preserves old timestamps. Active-only CSV cannot recreate unavailable records.

Default analysis is active-only. Use full JSON for sold-out research when requested and keep results separate. Refresh leading prices/availability; never equate feed claims with reserved stock. Preserve unmapped genres and all major categories. Connect findings to assessments, collection dispositions, watch targets and source registry using stable identifiers.
