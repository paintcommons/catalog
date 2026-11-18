# Two Thin Coats manufacturer enrichment

Reviewed 2026-11-18. Based on catalogue commit `6bf3e7ebaa8d6b6e591c79f769844b4594f13138` (the clean Arcturus import, PR #2). This is separate from the proposed Arcturus colour/conflict replacements in PR #3.

## Result

- Rename the existing 180 **Duncan Rhodes** records to **Two Thin Coats**, retaining Wave 1, Wave 2 and Wave 3.
- Add manufacturer SKUs and published EAN-13 barcodes to all 180. No codes or check digits were inferred. Each barcode links to the [Trans Atlantis Games product guide](https://transatlantisgames.com/product-list/).
- Match 167 names by normalised exact spelling, and 13 through the explicit alias table below. Manufacturer spelling also changes punctuation/case on four other records, for 17 changed names overall.
- Preserve every existing colour object (hex, gradient and source), type, range, status and any id. All unrelated paint records are identical to the pinned base.
- Add 30 **Dark Arts** paints (21 acrylics, three metallics, six inks), eight effects and **Spirit Medium**: **219 TTC paints** total. The effects and medium use the official shop collection name, Effects Paints.
- All 39 additions have unknown product codes (`null`) and no barcodes. The 30 Dark Arts paints receive exact-name GERInFact numeric hex values, with source `gerinfact-ttc-235dc3f`. The other nine additions have no colour object. The schema represents unknown colours by omitting `colour`, rather than JSON `null`. Set identifiers are not individual-bottle identifiers and are not assigned to paints.
- Catalogue totals: 9,984 paints, 1,745 barcodes, 9,960 colours. Thirty new swatches were added; no existing swatch values were replaced.

## Evidence and reproduction

| File | Purpose |
|---|---|
| [Manufacturer products](../../data/sources/ttc-manufacturer-products.json) | 180 factual name/SKU/category/EAN rows, each with primary source URL |
| [Additions](../../data/sources/ttc-additions.json) | 39 names, types, ranges and primary source URLs; no swatch values |
| [Existing record changes](existing-record-changes.json) | Full before/after pairs, including all preserved colours and the matching method |
| [Summary](summary.json) | Counts and pinned baseline |
| [Numeric source](../../data/upstream/gerinfact-235dc3f/SOURCE.json) | GERInFact attribution, pinned revision, transformation and integrity hashes |
| [Swatch clearance](swatch-clearance.json) | Candidates, scope, terms and unresolved reuse questions |
| [Permission request](permission-request.md) | Unsent draft covering numeric data and artwork separately |

Primary sources: [TAG product guide](https://transatlantisgames.com/product-list/), [TAG Dark Arts announcement](https://transatlantisgames.com/two-thin-coats/darkarts/), its [named paint graphic](https://i0.wp.com/transatlantisgames.com/wp-content/uploads/2025/09/Dark-Arts-Sir-Coats-Swatch.png?resize=644%2C1024&ssl=1), [official effects collection](https://store.duncanrhodes.com/collections/effects-paints), and [Spirit Medium product page](https://store.duncanrhodes.com/products/spirit-medium). The eight effects are individual paints; the collection's bundle is excluded.

The published factual product attributes are used to identify paints. This does not assert an open licence over the manufacturer's website, artwork, descriptions, charts or database. Those assets are not copied into this repository. Existing Arcturus swatches remain under MIT, attributed to Rick Fleuren and Miniature Painter Pro in [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

Reproduce offline with `python3 scripts/import-ttc.py`. It reads the pinned base and checked-in factual inputs and pinned numeric swatches, refuses unexpected edits in the affected directories, and rewrites only TTC files and the two generated reports. Run `python3 scripts/import-ttc.test.py` and `node scripts/validate.mjs --base pr/arcturus-clean-imports` to check preservation, provenance, uniqueness and GTIN check digits. The Arcturus tests continue to check all 1,981 original records unchanged, with the TTC additions covered separately.

## Explicit aliases

These correct apparent upstream transcription errors using the manufacturer's product guide and visual checks of the official Wave 1–3 charts. They identify existing records rather than create duplicates.

| Imported name | Manufacturer product-guide name |
|---|---|
| Keleton Legion | Skeleton Legion |
| Merald Green | Emerald Green |
| RC Flesh Wash | Orc Flesh Wash |
| Sorceror's Cloak | Sorcerer’s Cloak |
| Ur Cloak | Fur Cloak |
| Batle Axe Brass | Battle Axe Brass |
| Helion Red Wash | Hellion Red Wash |
| Death Metal | Doom Metal |
| Elder Robe | Eldar Robe |
| Matt Varnish | Satin Varnish |
| Ritz O'Tin | Bitz O’ Tin |
| Septric Green | Septic Green |
| Von Evile Pimple | Von Evile Purple |

The Wave 3 chart labels **Satin Varnish**, so it is a correction to the existing Matt Varnish record, not a 40th addition. The chart spells **Bits O' Tin**, while the product guide spells **Bitz O’ Tin**; this import uses the guide's spelling alongside its SKU/EAN. These identities deserve explicit reviewer attention. Their existing approximate colour values are preserved, including varnishes; this PR does not claim that those values are good swatches.

## Downloadable charts and numeric values

The user supplied the [Academy paint page](https://www.duncanrhodes.com/ttc-paints/). Its direct downloads include [Wave 1](https://www.duncanrhodes.com/wp-content/uploads/2023/08/Colour-Wheel-Wave-1_2023_01.pdf), [Wave 2](https://www.duncanrhodes.com/wp-content/uploads/2023/08/Colour-Wheel-Wave-2_2023_01.pdf) and [Wave 3](https://www.duncanrhodes.com/wp-content/uploads/2025/10/Wave-3-Colour-Chart_2024.pdf). These were visually inspected for names and range membership. Copyright notices are present. [Academy terms](https://www.duncanrhodes.com/terms-and-conditions/) restrict reproduction/distribution and commercial use without permission. Download access does not itself establish an open redistribution grant for chart artwork. PDFs and extracted swatch graphics are not distributed here.

**Numeric hex values are a separate question.** The [GERInFact converter](https://gerinfact.github.io/ttc_citadel/) has a [public JSON dataset](https://github.com/GERInFact/ttc_citadel/blob/235dc3f5fda248a2499d68098cbc000e232f413a/colors.json) with 210 numeric swatches, including all 30 Dark Arts names. The repository has no licence file or other verified permission statement at the reviewed revision. Absence of a licence does not establish copyright in individual hex codes: [US Copyright Office guidance](https://www.copyright.gov/comp3/chap300/ch300-copyrightable-authorship.pdf) distinguishes unprotectable facts/colour from copyrightable expression. Potential [UK/EU database rights](https://www.gov.uk/guidance/sui-generis-database-rights), applicability of any terms, and the provenance of the compiled values remain separate questions. We have not established that these rights apply to this particular dataset, nor that reuse is prohibited. The maintainer has directed publication of the numeric values with attribution, treating the individual numbers as factual data. This records the publication decision and remaining provenance limits; it does not claim an open licence or verified upstream permission.

The converter's image credits refer to manufacturer logos in its UI, which does not establish where its hex values came from. The Academy links to the converter; that endorsement alone does not specify downstream data reuse rights. This PR imports the 30 Dark Arts numeric values with full GERInFact attribution and pinned links; no Citadel equivalences, code or images are imported. All existing colours remain unchanged. The draft conflict comparison PR separately reviews differences for the existing 180 TTC paints. Nine effects/medium colours remain absent.

A [2022 Reddit discussion](https://www.reddit.com/r/minipainting/comments/yei5jm/two_thin_coats_on_paintrack/) contains comments from the paintRACK developer describing manufacturer-supplied target-colour spreadsheets alongside painted samples and website swatches. They also said they had received TTC information for an upcoming update; they did not specify that TTC supplied a spreadsheet. This is a lead to ask TAG/DRPA for an existing numeric table, not a reuse grant or proof of any particular source's accuracy. No paintRACK data were copied.

## Review and merge sequencing

This PR is stacked on the clean import (#2), and should merge after it. The 180 imported TTC records do not yet have assigned catalogue ids. If merging #2 causes ids or other fields to be written back before this PR merges, rebase this change onto that synchronized state and carry those ids forward through the rename. Do not merge a stale no-id rename after ids have appeared. The before/after report provides the full identity mapping; no live application changes are included here.
