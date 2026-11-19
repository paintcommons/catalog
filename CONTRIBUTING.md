# Contributing to Paint Commons

Thanks for helping. Every change is a pull request, checked automatically and reviewed by a maintainer before it's merged. Merged changes flow into [Stipplewise](https://stipplewise.com) on their own.

When a pull request is merged, each changed field is sent to Stipplewise and applied only if Stipplewise still has the value your change started from. If someone changed the same field there in the meantime, Stipplewise keeps its value, the hourly sync writes it back here, and an issue lists what wasn't applied.

## What makes a good change

- **One topic per pull request**: a range's new paints, a batch of barcode fixes, one corrected colour.
- **Evidence**: link to where the information comes from (the manufacturer's product page, catalogue or chart, or a photo of the bottle and label) in the pull request description.
- **Facts only**: codes, names, types, barcodes and colours. No prices, stock levels or reviews.

## Common changes

**Fix a name, code or type.** Edit the paint in its range file. Keep its `id`.

**Add a missing paint.** Add it to `paints/<brand>/<range>.json` (create the file if the range is new; names use lowercase words joined by hyphens, like `warpaints-fanatic.json`). Leave out `id`; it's assigned when the paint is imported and written back by the next sync. Set `"barcodes": []` if you don't have one and `"status": "current"`.

**Add a barcode.** Add `{ "ean": "…", "source": "published", "source_url": "https://…" }` with the page that shows it, or describe the bottle you scanned in the pull request and use `"source": "scan"`.

**Add or correct a colour.** A colour needs a source in `sources.json` with `"status": "published"`. If your source is new, add it to `colour_sources` (name, URL, how you got the value) and explain in the pull request why it can be published. Don't copy from sites whose terms forbid it (for example Paint Vault, paintRack, Scalemates and Cadetcraft).

**A paint was discontinued.** Set `"status": "discontinued"`. Never delete a paint: other people's collections point at it.

## Rules the checks enforce

- Required fields, and no fields outside the schema.
- No duplicate ids, brand+code pairs, brand+range+name combinations or barcodes.
- Barcode check digits must be valid; published barcodes need a `source_url`.
- Colours are uppercase `#RRGGBB` and name a published source.
- Each paint sits in the file named after its brand and range.
- Paints that existed before can't be removed.

Run them yourself with `node scripts/validate.mjs` (Node 20 or later).

## Licence of contributions

By contributing your own work you agree that it's dedicated to the public domain under CC0 1.0.

### Gradients

Record only colours a source shows. Metallics and colour-shift paints: two or more stops sampled across the swatch; apps draw them dark to light and add a very light end when the source's lightest point isn't near white. Speedpaints (Contrast, Speedpaint, Xpress and the like), washes and glazes: up to three stops in the order pooled, true colour, thinned, where the true colour is the paint's `hex`; put `null` in a position the source doesn't show (for example `[null, "#080605", "#838282"]` when there's no pooled colour) and apps will generate it. Apps draw speedpaints as bands and washes and glazes as a smooth blend, without a metallic's shine. When two sources show different points of the same paint, keep both as stops rather than choosing one.

### Importing from another project

Data from another open project keeps its licence. To import some:

1. Add the project to `sources.json` (`colour_sources`) with an `id`, `name`, `url`, `method`, `status` (`published`), `licence` (an SPDX id: `CC0-1.0`, `CC-BY-4.0`, `MIT`, `BSD-2-Clause`, `BSD-3-Clause` or `ISC`, or `LicenseRef-facts` for factual values such as names and approximate colours from a source that states no licence; anything else can only be `withheld`) and `priority` (community projects 40; manufacturer publications 80). Licences that ask for credit also need an `attribution` and a `notice` pointing at its full text in `THIRD_PARTY_NOTICES.md`.
2. Mark each imported paint with `"source": "<id>"`, and each colour from it with `"colour": {…, "source": "<id>"}`.
3. A colour from a lower-priority source can't replace one from a higher-priority source. If the evidence says it should, explain why in the pull request and ask for the `colour-override` label.

The same pull request can add the source and the paints that cite it. Big imports are fine: they reach Stipplewise in batches. If Stipplewise refuses any new paint, the import job opens an issue and the hourly sync pauses until a follow-up pull request fixes it.

### Duplicate identities

Do not delete an ID to merge duplicates. A reviewed `aliases.json` entry maps the retired ID to an existing canonical paint. The backend retains old IDs and private collection references; public exports omit the duplicate. Aliases cannot point to another alias or to a missing paint. The validator permits removing an existing public record only when its ID has such a redirect.
