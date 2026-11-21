# Paint Commons catalog: agent instructions

Read `README.md`, `CONTRIBUTING.md`, `schema/paint.schema.json`, and `sources.json` before changing data. Check relevant import reports for provenance and preservation decisions. This repo owns the public catalog; the browser/shared grouping package lives in `paintcommons/website`, and private collection data lives in Stipplewise.

## Working with contributors

- Inspect `git status`, `git worktree list`, and branch history first. Use your own worktree and topic branch from `main` (Codex branches use `codex/<topic>`). Leave other contributors' branches and uncommitted files alone.
- Coordinate overlapping brand/range files with Jim. This repo has no `npm run wip`; check the Stipplewise board for tasks spanning both projects on Jim's Mac.
- Keep one source, range, or correction topic per pull request, with evidence URLs and the reason for every changed fact. Use plain, descriptive commits.
- Agents working for Jim use his configured human Git identity; human contributors use their own. Never add agent authors, co-authors, signatures, or generation credits. Do not bypass attribution hooks/checks.
- Use the Codex in-app browser for browser interactions unless Jim explicitly requests an exception.

## Data and provenance

- Keep existing IDs stable. Never delete a paint to retire it; mark it discontinued. Duplicate reconciliation needs reviewed direct redirects in `aliases.json`, preserving existing private references. Do not chain aliases or point them to missing paints.
- Preserve source metadata and licences. New colour sources require maintainer approval for publication; keep unsupported or uncleared colours absent/withheld. Imported records and colours must name their source, with required credits and notices in `THIRD_PARTY_NOTICES.md`.
- Do not copy data from Paint Vault, paintRack, Paintrack, Scalemates, or Cadetcraft. Do not fetch Vallejo's site with scripts; Jim supplies its publications manually. Keep manufacturer PDFs, chart images, photos, and artwork outside the public dataset.
- Capture supported names, ranges, codes, types, pack sizes, published barcodes, colour values, and provenance where the schema permits. Leave unknown optional facts absent; do not invent names, swatches, finishes, or manufacturer colour families.
- Published barcodes need their source URL; distinguish calculated, published, and scanned barcodes. Check digits are mandatory.
- Store only source-observed gradient stops, following `CONTRIBUTING.md`. Rendering effects and calculated colour families belong in consumers, not the public record. Lower-priority sources must not silently overwrite higher-priority colours; overrides need an explained maintainer review and the `colour-override` label.
- Never add Collection/Wishlist data, personal overrides, private scans, photos, account IDs, or submitter identities. Only approved public catalog information crosses the sync boundary.

## Validation and release

- Use Node.js 22, Python 3, and a checkout with full Git history. Run all four validation commands in README.md before review, including `node scripts/validate.mjs --base main` to detect removals. Check source notices and sort/file placement too.
- Preserve import/export compatibility with Stipplewise and older clients. Coordinate backend/schema changes in that repo first, then catalog workflow/validator changes. Do not weaken validation to silence a provenance or identity conflict.
- Imports and syncs are production writes. Test local diff/validation tools against fixtures or isolated files; do not use production sync credentials/endpoints as a test harness.
- Submit changes for maintainer review. Ask Jim before pushing `main` unless already authorized; that push triggers **Import into Stipplewise**. After an authorized release, monitor import/validation results and any conflict issue. Do not manually overwrite an hourly sync result; resolve the underlying conflict through a reviewed follow-up.
- Secret provisioning, deploy keys, branch rules, and backend administration require separate authorization. Never print secrets, put them in chat, or commit them.
