# Scoped Arcturus import

Based on merged catalogue conventions at `86b53a219983f6a3b73587345bdf0732ce4379dc`. Upstream: [Rick Fleuren / Miniature Painter Pro miniature-paints](https://github.com/Arcturus5404/miniature-paints/tree/22791a682e1d155da388f4f856cd7196cd9f2677), MIT. Stable record/colour source: `arcturus-miniature-paints`; priority 40; full credit and licence in [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

## Import result

6,284 unambiguous additions remain after 1,673 scope exclusions. Three normalized conflict identities are also admitted, for **6,287 additions / 8,268 total paints / 21 brands**. Every one of the 1,981 records on the merged main baseline is preserved exactly, including all colours, manual overrides, ids and barcodes. Imported records and their colours both cite the MIT source.

Excluded: five brands with fewer than 100 paints; Citadel Foundation/old Foundation Wash/Primer entries; listed box/set pseudo-ranges; new ranges with fewer than five paints. The full [decisions ledger](decisions.json) retains every one of the 9,909 upstream hobby rows and the exclusion reasons. The five proposed non-spray Citadel additions were spelling aliases of existing paints; they now match and preserve those existing records instead of creating duplicates. D&D Nolzur’s main bottle-labelled range remains; its separately split sub-five wash/primer fragments are deferred under the same small-range rule.

Reaper’s documented acrylic ranges and Scale75 Artist, Fantasy & Games, Scale Color and Warfront are classified as acrylic. Scale75 Instant Colors is speedpaint and Metal N Alchemy is metallic; other unsupported classifications are not invented. AK 3rd Gen was already classified.

## Identity-conflict review moved from PR #3

[conflict-review.json](conflict-review.json) retains all 127 source observations and their dispositions. The original proposal inputs are pinned in `data/sources/arcturus-conflict-review.json`; no competing evidence is discarded.

Of the previous 76 provisional selected additions: 38 are outside the approved scope; 33 still need identity clarification (20 same-name/multiple-code cases, eight different-name/same-code cases, five existing-range ambiguities); two are normalized spelling aliases, not additional paints. Three unique identities can be admitted without choosing between different codes or paint names:

- Mission Models Grey Blue Cockpit / Camo Modern Russian Jets, MMP-096 (spacing variants collapse).
- P3 'Jack Bone (apostrophe variant collapses).
- P3 Battle Dress Green (spacing variant collapses).

For those three, the first pinned upstream colour observation is used as an approximate swatch and all alternatives remain in the ledger; no manufacturer verification is asserted. This resolves identity, not physical colour accuracy. Other code/name ambiguities remain withheld rather than importing arbitrary first-row products.

## Colour disagreements and reproducibility

The 1,613 existing-colour comparisons include 392 substantial observations (Euclidean OKLab ≥ 0.08), representing 370 unique paints. None changes a colour in this import. The separate review uses stop-based enrichment and per-range spot checks under the merged conventions.

Run `PYTHONDONTWRITEBYTECODE=1 python3 scripts/import-arcturus.py --review-reports` to reproduce offline. The source reader verifies upstream Git blob hashes and RGB/hex consistency. The importer refuses unrelated edits. Tests verify baseline preservation, scope, identities, record/colour attribution and full MIT notice. Use `node scripts/validate.mjs --base origin/main` and `node --test scripts/*.test.mjs` too. Local import CLI path handling is fixed for directories containing spaces; smoke tests ensure the entry points really execute. No live data import is performed by these checks.

## Formal review corrections and narrower scope

Revisited [the formal review](https://github.com/paintcommons/catalog/pull/2#pullrequestreview-5966040742), not only discussion comments. FolkArt, Golden, Apple Barrel and Liquitex are now deferred at the maintainer’s request; together they account for 1,095 records in the previous proposal. The five Citadel aliases plus Boney/Bony Spikes and Terrestial/Terrestrial Titan no longer create duplicate paints.

Twelve genuine Fanatic metallics belong in **Warpaints Fanatic Metallic**, type metallic, current. They must not be moved wholesale into the original formula: the [manufacturer lists Fanatic metallics](https://thearmypainter.com/pages/metallics), including [Cobalt Metal](https://thearmypainter.com/products/warpaints-fanatic-warpaints-fanatic-metallic-cobalt-metal-wp3194p) and [Evil Chrome](https://thearmypainter.com/products/warpaints-fanatic-warpaints-fanatic-metallic-evil-chrome-wp3185p). Shared names across original/Fanatic generations do not establish duplicates. Original Warpaints was replaced by Fanatic; the separately versioned transparent line is Speedpaint / Speedpaint 2.0. There is no asserted Fanatic 2.0 generation in this import.

The misfiled Fanatic wash rows are separated into 11 actual washes, eight effects, one primer and one medium. Range placement uses the existing Fanatic/Effects/Metallic structure; type overrides distinguish primer and medium without inventing box-labelled ranges.

All 464 new Vallejo observations and 133 superseded original Army Painter observations are marked legacy/discontinued, following the current-catalogue/superseded-generation review. This is a catalogue-status classification, not a claim about remaining retailer stock. The imported rows retain that review as their availability basis. Existing published records are unchanged.

Existing unambiguous range types are inherited. Known acrylic product families are explicitly classified; source-dependent lacquer/spray/pigment ranges are not indiscriminately made acrylic. The remaining `other` count is **1,835 of 6,287 (29.2%)**, down from 4,719 of 7,389 (63.9%). Every rule, source correction and disposition is reproducible in the generator.

The upstream spelling `Arte Deco Colores Fluoresecents` remains disclosed rather than silently inventing a printed range name. Phone colour-matching/label-reading regression testing requested by the reviewer remains a pre-merge device check; these local catalogue checks do not claim to cover the installed application.
