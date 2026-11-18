# Paint Commons catalog

An open, community-maintained catalog of miniature paints: brands, ranges, product codes, names, paint types, barcodes and approximate colours, each colour with its source.

- **10,060 paints** across 30 brands, including The Army Painter, Citadel, Vallejo, AK Interactive, Reaper, Scale75, Tamiya, Two Thin Coats and more
- **1,745 barcodes**, each marked calculated, published (with its source URL) or confirmed by scan
- **10,036 colours**, each linked to the chart, catalogue or method it came from

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

Paint Commons contributions to the data in this repository (`paints/`, `equivalents.json`, `sources.json`) are dedicated to the public domain under [CC0 1.0](LICENSE). Imported third-party data retain their original terms; the CC0 dedication does not replace those terms.

Data from [Arcturus5404/miniature-paints](https://github.com/Arcturus5404/miniature-paints), published by **Rick Fleuren and the Miniature Painter Pro team**, are under MIT, Copyright (c) 2022 Rick Fleuren. The direct import uses source `arcturus-miniature-paints-22791a6`; existing data imported through Ben Kelly’s package keep the `miniature-paints` source. **Retain the full [third-party notices](THIRD_PARTY_NOTICES.md) with copies or substantial portions of these data.**

The [Arcturus import report](reports/arcturus-import/README.md) documents the pinned revision, matching rules, withheld rows. Proposed colour replacements and conflict resolutions are reviewed in a separate PR. Existing records and their colours were preserved.

The [Two Thin Coats report](reports/two-thin-coats/README.md) documents the brand rename, manufacturer identifiers, name corrections and 39 additions. Existing colours retain their MIT provenance; 30 new Dark Arts paints use attributed GERInFact numeric values; the other nine additions have no colour.

Numeric swatches from [GERInFact’s TTC–Citadel Converter](https://github.com/GERInFact/ttc_citadel) are attributed separately in [third-party notices](THIRD_PARTY_NOTICES.md). No explicit upstream licence was found; these values are not represented as an MIT or CC0 import.

The scripts in `scripts/` are under the [MIT licence](scripts/LICENSE).

Paint and brand names are trademarks of their owners. Paint Commons isn't affiliated with or endorsed by any paint manufacturer.

## Contributing

Corrections and missing paints are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Merged changes also reach Stipplewise automatically.

Check your changes with:

```sh
node scripts/validate.mjs
```

This draft review branch also proposes 536 main-hex replacements, one metallic gradient proposal and 76 conflict additions. See [the joint comparison report](reports/arcturus-review/README.md), including a standalone HTML review of 180 existing Two Thin Coats colours. Existing colours are preserved in the clean TTC import PR; replacements here remain pending review.
