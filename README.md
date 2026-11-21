# Paint Commons catalog

An open, community-maintained catalog of miniature paints: brands, ranges, product codes, names, paint types, barcodes and approximate colours, each colour with its source.

The files on `main` are the current dataset. Counts change as approved contributions and hourly syncs arrive; import reports describe their own snapshots rather than a live total. Browse the data at [paintcommons.org/catalogue/](https://paintcommons.org/catalogue/).

Paint Commons is inspired by the commons ethos of Wikipedia and Creative Commons, with no affiliation to either. The catalog is kept in sync with [Stipplewise](https://stipplewise.com), a paint collection app that contributes reviewed corrections and reads the catalog back.

## Files

| Path | What it holds |
|---|---|
| `paints/<brand>/<range>.json` | One file per range: an array of paints, sorted by product code then name |
| `sources.json` | Every colour and barcode source: name, URL, how values were obtained, and whether colours from it are published |
| `aliases.json` | Direct redirects from retired duplicate IDs to canonical paints |
| `equivalents.json` | Declared same-colour pairs across brands, by paint id |
| `schema/paint.schema.json` | JSON Schema for a range file |
| `scripts/validate.mjs` | Checks every file: fields, duplicates, barcode check digits, sources, file placement |

A paint:

```json
{
  "id": "4c0d2e7a-…",
  "brand": "The Army Painter",
  "range": "Warpaints Fanatic",
  "code": "WP3001",
  "name": "Matt Black",
  "type": "acrylic",
  "barcodes": [{ "ean": "5713799300108", "source": "calculated" }],
  "colour": { "hex": "#0B0B0B", "gradient": null, "source": "army-painter-fanatic-chart" },
  "status": "current"
}
```

- `id` never changes. Use it to link to a paint.
- `colour` is left out when there's no colour, or when its source isn't cleared for publication (see `sources.json`).
- `gradient` lists stops for metallics and colour-shift paints, where one hex can't describe the paint.
- `finish` and `manufacturer_colour_family` are optional, source-supported product attributes. Leave them out when unknown. Manufacturer families retain the manufacturer’s published names; calculated display runs are separate. Existing records will be filled in during a later batch review.
- `status` is `current` or `discontinued`. Paints are never removed.

## About the colours

Every colour is an approximation of paint in the pot, taken from printed or rendered swatches, product photos or manufacturer charts. None are lab measurements. Metallics, washes, contrast paints and colour-shift paints are especially rough, and screens vary. `sources.json` says how each source's colours were obtained.

## Licence

The data in this repository (`paints/`, `equivalents.json`, `sources.json`) is dedicated to the public domain under [CC0 1.0](LICENSE), except records that cite a source with its own licence. Every colour names its source (`colour.source`), and a paint imported from another project names it too (`source`). [sources.json](sources.json) lists each source with its licence, credit (`attribution`) and where its full notice lives; [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) holds those notices. If you reuse records from an MIT- or CC-BY-licensed source, keep its credit and notice with them. Credit for the rest is appreciated but not required.

Colours from sources marked `CC0-1.0` were measured by Paint Commons maintainers from manufacturers' published charts and swatches. They're approximate facts about each paint: one number sampled per swatch. The CC0 dedication covers our measurements and the way we put the catalog together. It doesn't claim rights in the manufacturers' own charts, artwork, photos or descriptions, none of which are copied here, and manufacturers keep whatever rights they have in their publications. Names, product codes and barcodes are facts published to identify products.

If you make paints and object to how your information appears here, open an issue or write to hello@stipplewise.com and we'll look at it promptly.

The scripts in `scripts/` are under the [MIT licence](scripts/LICENSE).

Paint and brand names are trademarks of their owners. Paint Commons isn't affiliated with or endorsed by any paint manufacturer.

## Contributing

Corrections and missing paints are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Merged changes also reach Stipplewise automatically.

## Development and review

Read [CONTRIBUTING.md](CONTRIBUTING.md) for record edits, source approval, gradients, and imports, and [AGENTS.md](AGENTS.md) for agent coordination. Use Node.js 22 (matching CI), Python 3 for import checks, and Git with full history for tests that inspect earlier commits. There are no npm dependencies to install.

Start a topic branch or separate worktree from `main`, keep one topic per pull request, and retain stable paint IDs. New paints may omit `id`; the import assigns it and a later sync writes it back. Existing paints are discontinued or given reviewed alias redirects rather than deleted.

Run the same checks as `.github/workflows/validate.yml`:

```sh
node --test scripts/*.test.mjs
PYTHONDONTWRITEBYTECODE=1 python3 scripts/import-arcturus.test.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/import-ttc.test.py
node scripts/validate.mjs --base main
```

The base comparison detects removal of existing records; CI compares pull requests with their target branch. Tests inspect historical commits, so a shallow clone may need its history fetched. At the documentation refresh (November 21, 2026, `main` at `2fd5889`), data validation passes but historical import tests still compare the growing dataset against fixed counts or whole-dataset snapshots. Fixture-pinning fixes exist on `kimera-kolors`; they are not part of `main`. If you encounter these failures, distinguish them from regressions in your change and coordinate the fixture correction rather than weakening data checks.

Python import scripts are maintenance tools, not required setup commands. Check their output in an isolated worktree before proposing data changes.

## Sync and publication

- **Import into Stipplewise** processes changes pushed to `main`, excluding the hourly sync bot's own commits. Changes apply field by field only while the backend still matches the previous value. Rejected changes are reported in an issue.
- **Sync from Stipplewise** runs hourly at minute 17 and on demand. It exports approved public data and commits updates. It waits for the latest human change to import; refused new paints pause export so they cannot disappear in a later sync.
- **Validate** checks pull requests and pushes to `main`. A maintainer reviews contributions before merge. Publishing to `main` is a live backend change, even though this repository has no application deployment.

No account collections, private corrections, photos, or submitter identities belong in this repository. Do not call production sync endpoints or use sync credentials for local tests. Backend/schema changes must reach Stipplewise through its release process before a catalog contribution requires them. Source approval, licence priority, conflict handling, and IDs must work for existing consumers.

## Import history

The [scoped Arcturus import](reports/arcturus-import/README.md) adds 6,287 paints from the MIT-licensed miniature-paints project, credited to Rick Fleuren and Miniature Painter Pro. Every imported record and colour cites `arcturus-miniature-paints`; existing records and manufacturer colours are preserved. The pinned snapshot and full MIT notice are distributed with the data. Identity conflicts are documented separately in the import report; colour/gradient enrichments remain a separate review.

The separate [Two Thin Coats import](reports/two-thin-coats/README.md) preserves existing colours, adds identifiers and 39 paints. Its approved GERInFact numeric values use credited `LicenseRef-facts` under the catalog’s source convention. Future source or format extensions still require a compatible downstream release before merge.

`aliases.json` preserves retired duplicate IDs as direct redirects to canonical paints. The 180 former Duncan Rhodes identities resolve to the enriched Two Thin Coats records; private collection references remain valid in Stipplewise.
