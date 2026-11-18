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
