# Paint Commons catalog

An open, community-maintained catalog of miniature paints: brands, ranges, product codes, names, paint types, barcodes and approximate colours, each colour with its source.

- **9,370 paints** across 25 brands, including The Army Painter, Citadel, Vallejo, AK Interactive, Reaper and Scale75
- **1,565 barcodes**, each marked calculated, published (with its source URL) or confirmed by scan
- **9,355 colours**, each linked to its source

Paint Commons is inspired by the commons ethos of Wikipedia and Creative Commons, with no affiliation to either. The catalog is kept in sync with [Stipplewise](https://stipplewise.com), a paint collection app that contributes reviewed corrections and reads the catalog back.

## Files

| Path | What it holds |
|---|---|
| `paints/<brand>/<range>.json` | One file per range: an array of paints, sorted by product code then name |
| `sources.json` | Every colour and barcode source: name, URL, how values were obtained, and whether colours from it are published |
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

The scripts in `scripts/` are under the [MIT licence](scripts/LICENSE).

Paint and brand names are trademarks of their owners. Paint Commons isn't affiliated with or endorsed by any paint manufacturer.

## Contributing

Corrections and missing paints are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Merged changes also reach Stipplewise automatically.

Check your changes with:

```sh
node scripts/validate.mjs
```

The [scoped Arcturus import](reports/arcturus-import/README.md) adds 7,389 paints from the MIT-licensed miniature-paints project, credited to Rick Fleuren and Miniature Painter Pro. Every imported record and colour cites `arcturus-miniature-paints`; existing records and manufacturer colours are preserved. The pinned snapshot and full MIT notice are distributed with the data. Identity conflicts are documented separately in the import report; colour/gradient enrichments remain a separate review.
