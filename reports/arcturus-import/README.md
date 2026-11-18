# Arcturus import and colour review

Adds **7,964 paints**, bringing the catalogue to **9,945 paints across 30 brands**. All **1,981 existing paint objects** are unchanged, including IDs, names, codes, barcodes, status, colour sources, hex values and gradients. Existing records without colours are also untouched. No existing colour is replaced or backfilled.

Source: [Arcturus5404/miniature-paints](https://github.com/Arcturus5404/miniature-paints/tree/22791a682e1d155da388f4f856cd7196cd9f2677), published by **Rick Fleuren and the Miniature Painter Pro team**, MIT © 2022 Rick Fleuren. Full notice: [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). The 32 hobby tables and licence are retained under `data/upstream/arcturus-22791a6/`; Pantone/RAL standards and logos are excluded. Every table matches the pinned Git blob hash; imported hex values are checked against upstream RGB.

## Matching and withheld rows

Match against the original catalogue by normalized manufacturer code first, then name and compatible range. Known range aliases and finish subranges are reconciled for matching only; Air, brush ranges and generations are kept distinct. Explicit Citadel Spray/historical ranges and Army Painter Air/original Speedpaint/Fanatic ranges may add a same-name product in a different generation or application range; ambiguous set labels remain withheld. Ben Kelly's package lineage is not treated as independent measurement evidence. The upstream `Creature` table identifies its rows as Monument Pro Acryl and is mapped to Monument Hobbies; `AKRC` is mapped to AK Interactive. Monument numeric/MPA-prefixed codes are compared consistently. Per-row original locators remain in the reports and snapshots.

**127 upstream rows are withheld** for conflicting code/name identities, unresolved existing-range matches or a missing name. **199 exact/repeated upstream identities are deduplicated**. See [decisions.json](decisions.json): every one of the 9,909 source rows has a recorded decision and immutable source URL. Conflicting upstream observations never overwrite existing paint records.

Unsupported chemistry/type is `other`, rather than guessed from colour or brand. Explicit range wording supplies types where available. No barcodes, gradients, pack sizes, finish or manufacturer colour families are invented. New IDs are left out per CONTRIBUTING.md. Status is `discontinued` where stated explicitly upstream; otherwise `current` is the required contribution default, not independently verified present-day availability.

## Reproduce and validate

```sh
python3 scripts/import-arcturus.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/import-arcturus.test.py
node scripts/validate.mjs --base cc6ddee
node --test scripts/*.test.mjs
```

The importer uses the pinned baseline `cc6ddee` to reproduce this one-time import and reports. It verifies the pinned source tables, refuses unrelated paint edits, and preserves baseline objects. It is not a general update/sync tool. Unknown or conflicting records remain available for separate review. No Stipplewise changes, deployment or automatic sync changes are included in this commit.

Detailed colour comparisons, unresolved identities and proposed replacements belong to the separate, stacked review PR. To regenerate the raw review reports before applying any replacement candidates, run `python3 scripts/import-arcturus.py --review-reports`.
