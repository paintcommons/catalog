# Draft Arcturus replacements and conflict resolutions

Stacked on the TTC import PR #4, commit `df41f4fd93363ae9ce7cf80a31d6defc621e1397`, which follows clean import PR #2. **Not approved for merging.**

- Proposes 370 existing colour replacements from 392 substantial disagreement observations. Existing names, IDs, codes, barcodes and status are unchanged.
- Proposes 76 candidate additions from the 127 withheld source rows; competing alternatives remain in the review ledger, and the empty-name row remains unresolved.
- [Colour review with rendered swatches](colour-review.md): current colour on the left, proposed colour on the right.
- [Conflict review with rendered swatches](conflict-review.md): each upstream candidate and any selected competing colour.
- Full before/after records and alternative source observations: `colour-proposals.json`, `conflict-proposals.json`.

Selections are deterministic starting points, not endorsements of Arcturus over manufacturer swatches. Reviewers should edit or reject individual changes. This PR clears gradients only on the proposed colour replacements because upstream publishes a single hex. All original colours and gradients are retained in the before/after ledger.

Validate with `node scripts/validate.mjs --base df41f4fd93363ae9ce7cf80a31d6defc621e1397` and `PYTHONDONTWRITEBYTECODE=1 python3 scripts/import-arcturus.test.py`. The one-time proposal script defaults to a dry run; `--apply` refuses any tree already changed from its clean baseline. Do not rerun the clean importer over accepted review edits.

## GERInFact / Two Thin Coats comparison

The clean TTC import preserves all 180 existing colours and fills only the 30 new Dark Arts colours. This draft additionally compares GERInFact values for **all 180 existing TTC paints**, with **167 proposed replacements**, **23 substantial differences** (Euclidean OKLab ≥ 0.08), and 13 identical hex values. Together with the 370 Arcturus replacements, this branch proposes **537 colour replacements** and 76 candidate additions. Total catalogue: 10,060 paints and 1,745 barcodes.

- [TTC comparison with CSS-rendered colours](ttc-colour-review.html): standalone HTML, no image files, searchable and filterable by substantial difference or identity review.
- [Full comparison ledger](ttc-colour-comparisons.json): all current/proposed colours, full before/after records, source names and pinned links.
- [TTC comparison summary](ttc-colour-summary.json).
- Numeric source: [GERInFact’s TTC–Citadel Converter](https://gerinfact.github.io/ttc_citadel/), [pinned colors.json](https://github.com/GERInFact/ttc_citadel/blob/235dc3f5fda248a2499d68098cbc000e232f413a/colors.json); see the attribution and rights disclosure in [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). No upstream open licence is asserted.

Five source-name differences are explicit aliases: Emperor Red → Emporer Red; Emperor’s Purple → Emporer's Purple; Bitz O’ Tin → Bits O' Tin; Sorcerer’s Cloak → Sorceror's Cloak; and **Ray Gun Glow → Ray Gun Blue**, which is flagged for identity review. These source-name differences do not rename catalogue paints. Neither numeric source is presumed better; even small differences remain reviewable. Identical hex values keep their original provenance unchanged. Existing ids, names, types, ranges, SKUs, barcodes and status are preserved by every replacement.

Reproduce TTC comparisons with `python3 scripts/propose-ttc-review.py --apply`. It refuses to overwrite TTC records edited away from the pinned baseline or the generated proposals. The TTC import tests check the pinned #4 baseline in this draft; the review invariant tests separately check every current record and all 537 proposed replacements against it. Do not rerun the clean importer over review edits.

Merge after #4, then rebase onto synchronized ids before final review/merge if catalogue sync has assigned them. This branch remains a draft for joint review.

## Official chart reference and Dragon’s Gold review decision

The 180 TTC comparisons now include a **reference-only** numeric sample of the official Wave 1/2 conversion PDFs and Wave 3 comparison PDF. No PDF artwork is committed, and these samples do not populate catalogue swatches. [Reference samples and distances](ttc-chart-references.json) disclose chart URLs, SHA-256 hashes, grid positions, native image coordinates, sampling masks, and RGB/lightness statistics. Reproduce with `python3 scripts/compare-ttc-chart-reference.py --evidence-dir <local-PDF-directory>` (requires pypdf and Pillow), then regenerate the HTML with the TTC review script.

The chart column uses the per-channel median of the circular interior (radius ≤ 0.85) and actual pixels at the 10th/50th/90th OKLab-lightness percentiles. Wave 1/2 central badges are excluded. This describes an illustration rather than measured paint; gradient percentiles are not manufacturer-specified stops.

**Dragon’s Gold, Wave 1, SKU 10044:** retain Arcturus’s **#CDA24E** as the main colour and bright stop; use GERInFact’s **#4F442C** as the dark stop. The proposed gradient is **[#4F442C, #CDA24E]**. Type is corrected from `other` to `metallic`, as documented in the manufacturer product guide. This is the only non-colour field changed by a TTC review proposal.

The official chart’s interior median is #A78644: OKLab distance 0.100046 from Arcturus and 0.251843 from GERInFact. However, both candidates closely match different portions of its illustrated gradient: nearest chart pixels are #CCA24E (distance 0.001596, radius 0.5088) and #50442C (distance 0.001787, radius 0.9305), respectively. Those radii are fractions of the illustrated swatch radius, not paint measurements. This supports the interpretation of the two candidates as brighter and shadow tones. The proposed endpoints come from the attributed existing numeric datasets, not PDF extraction.

The composite source entry preserves both upstream attributions and distinguishes the PDF’s reference role. The clean TTC import remains unchanged. There are still 167 TTC colour proposals, now comprising **166 main-hex replacements and one metallic gradient**; all 180 alternative-source differences remain visible for comparison. Total joint colour proposals remain 537.
