# Arcturus tonal-stop and colour review

Draft stacked directly on revised import PR #2, commit `12a3154807c3708ca169e2cd095528f504776404`. This review is Arcturus-only; TTC / GERInFact work remains separate in PR #4 and its retained review evidence. **No existing main hex is replaced.**

[Open the CSS-rendered review](colour-review.html): 373 unique paints / 395 substantial source observations, with search and disposition filters. [Full before/after ledger](colour-proposals.json) and [per-range review](per-range-review.json) retain every observation and alternate source. Attribution: Rick Fleuren / Miniature Painter Pro, MIT; stable source `arcturus-miniature-paints`, full licence in [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

## Proposed and preserved outcomes

- **49 matching-name, darker transparent observations** propose `[Arcturus pooled candidate, retained current hex, null]`. These cover speedpaints/washes; the thinned position is unknown and left null. Existing names, ids, types, ranges, codes, barcodes, status and main hexes are preserved. Per-stop provenance identifies both Arcturus and the retained source. The darker-tone interpretation follows the approved stop convention; neither numeric observation is a laboratory measurement.
- **Two manual overrides** remain exactly unchanged, including Vallejo Blacks 70.950 and 71.057.
- **27 metallic observations near existing gradients** remain unchanged. The classification uses nearest distance to a straight polyline between existing OKLab stops, with threshold 0.04. This is a review heuristic, not proof that a value is physically inside a metallic gamut; it differs from the earlier comment’s counts.
- **25 metallic observations outside that threshold** remain unchanged for manual review.
- **51 missing metallic gradients** (including all 34 Turbo Dork cases) remain unchanged pending sampling from approved source images. No single upstream hex replaces them.
- **195 other colour differences** remain unchanged for per-range spot checks. No bulk override is proposed.
- **16 lighter transparent observations** remain unchanged until their pooled/true/thinned role is established. Brightness alone does not establish dilution.
- **Eight identity/name mismatches** remain unchanged for identity review.

The 49 actual stop enrichments cite community priority 40, below their existing manufacturer sources. They require `colour-override` **after joint review**, rather than disguising imported stops as manufacturer values. No such label is added automatically. The original source and main hex remain explicitly recorded in each before/after pair and stop-provenance list.

## Identity candidates are part of the import review

All 127 original identity observations moved to [PR #2’s conflict review](../arcturus-import/conflict-review.json), including 76 prior selected candidates. The revised import admits three normalized identities, collapses two spelling aliases, excludes 38 selected rows by scope, and withholds 33 selected identities. This PR adds no paints and restores none of the excluded ranges.

## Reproduction and checks

`python3 scripts/propose-arcturus-review.py` prints the summary; `--apply` generates the proposals, HTML and paint changes. It refuses records edited away from the pinned baseline or its own previous ledger. Do not rerun the clean importer over review edits.

Validation: `python3 scripts/import-arcturus.test.py`, `python3 scripts/arcturus-review.test.py`, `node --test scripts/*.test.mjs`, and `node scripts/validate.mjs --base pr/arcturus-clean-imports`. Tests compare every record against the revised baseline and its explicit proposal, require exact main-hex preservation, prohibit manual override edits, and validate true-colour stop position and source attribution. Counts remain 8,268 paints, 1,565 barcodes and seven equivalents.

The baseline incorporates the formal review corrections: craft/artist brands deferred, Citadel and Fanatic spelling aliases matched, Fanatic placements corrected with manufacturer evidence, legacy status flags and supported acrylic classifications corrected. No retired records or excluded brands are restored by this review.
