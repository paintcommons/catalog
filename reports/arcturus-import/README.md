# Scoped Arcturus import

Based on merged catalogue conventions at `1cdcaf9633e88534762133991ea27584e1f16470`. Upstream: [Rick Fleuren / Miniature Painter Pro miniature-paints](https://github.com/Arcturus5404/miniature-paints/tree/22791a682e1d155da388f4f856cd7196cd9f2677), MIT. Stable record/colour source: `arcturus-miniature-paints`; priority 40; full credit and licence in [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

## Import result

7,385 unambiguous additions remain after 579 scope exclusions. Four normalized conflict identities are also admitted, for **7,389 additions / 9,370 total paints / 25 brands**. Every one of the 1,981 records on the merged main baseline is preserved exactly, including all colours, manual overrides, ids and barcodes. Imported records and their colours both cite the MIT source.

Excluded: five brands with fewer than 100 paints; Citadel Foundation/old Foundation Wash/Primer entries; listed box/set pseudo-ranges; new ranges with fewer than five paints. The full [decisions ledger](decisions.json) retains every one of the 9,909 upstream hobby rows and the exclusion reasons. Small additions to existing Citadel Base (2), Layer (2), Shade (1) remain. D&D Nolzur’s main bottle-labelled range remains; its separately split sub-five wash/primer fragments are deferred under the same small-range rule.

Reaper’s documented acrylic ranges and Scale75 Artist, Fantasy & Games, Scale Color and Warfront are classified as acrylic. Scale75 Instant Colors is speedpaint and Metal N Alchemy is metallic; other unsupported classifications are not invented. AK 3rd Gen was already classified.

## Identity-conflict review moved from PR #3

[conflict-review.json](conflict-review.json) retains all 127 source observations and their dispositions. The original proposal inputs are pinned in `data/sources/arcturus-conflict-review.json`; no competing evidence is discarded.

Of the previous 76 provisional selected additions: 37 are outside the approved scope; 33 still need identity clarification (20 same-name/multiple-code cases, eight different-name/same-code cases, five existing-range ambiguities); two are normalized spelling aliases, not additional paints. Four unique identities can be admitted without choosing between different codes or paint names:

- FolkArt Chocolate Brown, SKU 2570.
- Mission Models Grey Blue Cockpit / Camo Modern Russian Jets, MMP-096 (spacing variants collapse).
- P3 'Jack Bone (apostrophe variant collapses).
- P3 Battle Dress Green (spacing variant collapses).

For those four, the first pinned upstream colour observation is used as an approximate swatch and all alternatives remain in the ledger; no manufacturer verification is asserted. This resolves identity, not physical colour accuracy. Other code/name ambiguities remain withheld rather than importing arbitrary first-row products.

## Colour disagreements and reproducibility

The 1,613 existing-colour comparisons include 392 substantial observations (Euclidean OKLab ≥ 0.08), representing 370 unique paints. None changes a colour in this import. The separate review uses stop-based enrichment and per-range spot checks under the merged conventions.

Run `PYTHONDONTWRITEBYTECODE=1 python3 scripts/import-arcturus.py --review-reports` to reproduce offline. The source reader verifies upstream Git blob hashes and RGB/hex consistency. The importer refuses unrelated edits. Tests verify baseline preservation, scope, identities, record/colour attribution and full MIT notice. Use `node scripts/validate.mjs --base origin/main` and `node --test scripts/*.test.mjs` too. Local import CLI path handling is fixed for directories containing spaces; smoke tests ensure the entry points really execute. No live data import is performed by these checks.
