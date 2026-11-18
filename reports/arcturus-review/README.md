# Draft Arcturus replacements and conflict resolutions

Stacked on the clean import commit `ddcd495b55ef3e1611a9886affcfa47eaad5092c`. **Not approved for merging.**

- Proposes 370 existing colour replacements from 392 substantial disagreement observations. Existing names, IDs, codes, barcodes and status are unchanged.
- Proposes 76 candidate additions from the 127 withheld source rows; competing alternatives remain in the review ledger, and the empty-name row remains unresolved.
- [Colour review with rendered swatches](colour-review.md): current colour on the left, proposed colour on the right.
- [Conflict review with rendered swatches](conflict-review.md): each upstream candidate and any selected competing colour.
- Full before/after records and alternative source observations: `colour-proposals.json`, `conflict-proposals.json`.

Selections are deterministic starting points, not endorsements of Arcturus over manufacturer swatches. Reviewers should edit or reject individual changes. This PR clears gradients only on the proposed colour replacements because upstream publishes a single hex. All original colours and gradients are retained in the before/after ledger.

Validate with `node scripts/validate.mjs --base ddcd495b55ef3e1611a9886affcfa47eaad5092c` and `PYTHONDONTWRITEBYTECODE=1 python3 scripts/import-arcturus.test.py`. The one-time proposal script defaults to a dry run; `--apply` refuses any tree already changed from its clean baseline. Do not rerun the clean importer over accepted review edits.
