import { test } from "node:test";
import assert from "node:assert/strict";
import { toBatches, combine } from "./send-import.mjs";

test("sources go in the first batch and batches stay under the size", () => {
  const paints = Array.from({ length: 25 }, (_, i) => ({ op: "insert", paint: { name: `P${i}` } }));
  const batches = toBatches([...paints.slice(0, 12), { op: "source_upsert", source: { id: "s" } }, ...paints.slice(12)], 10);
  assert.deepEqual(batches.map((b) => b.length), [10, 10, 6]);
  assert.equal(batches[0][0].op, "source_upsert");
  assert.deepEqual(toBatches([], 10), [[]], "an empty commit is still sent, so it's recorded as imported");
});

test("the colour-override label marks colour updates only", () => {
  const [batch] = toBatches([{ op: "update", field: "colour" }, { op: "update", field: "name" }], 10, { override: true });
  assert.deepEqual(batch.map((c) => c.override), [true, undefined]);
  assert.equal(toBatches([{ op: "update", field: "colour" }], 10)[0][0].override, undefined);
});

test("responses combine into one report", () => {
  const r = combine([
    { commit: "c", applied: 2, conflicts: 1, failed_inserts: 1, complete: false, results: [{ outcome: "applied" }] },
    { commit: "c", applied: 3, conflicts: 0, failed_inserts: 0, complete: true, results: [{ outcome: "conflict" }] },
  ]);
  assert.deepEqual([r.applied, r.conflicts, r.failed_inserts, r.complete, r.results.length, r.already_imported], [5, 1, 1, true, 2, false]);
});
