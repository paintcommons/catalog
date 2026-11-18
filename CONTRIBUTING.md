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

By contributing your own work you agree to dedicate your contribution to the public domain under CC0 1.0. Approved third-party imports retain their upstream licence, and must include the full applicable notice in THIRD_PARTY_NOTICES.md, an attributed source entry, and provenance. Do not represent upstream MIT data as notice-free CC0.
