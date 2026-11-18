// Lists the catalog changes between two commits, in the shape Stipplewise's catalog-import expects.
//   node scripts/diff-for-import.mjs <base sha> <head sha>   → JSON array on stdout
// Paints are matched by id across files, so moving a paint to another range is an update. Sources
// (sources.json colour_sources) come first, so paints in the same commit can cite a source it adds.
// A paint without an id is sent as an insert by every commit until the hourly sync writes its id
// back; Stipplewise answers "unchanged" once it has it, and a commit that fixes a refused paint
// completes the import.
import { execFileSync } from "node:child_process";

const FIELDS = ["brand", "range", "code", "name", "type", "status", "finish", "manufacturer_colour_family", "source"];
const same = (a, b) => JSON.stringify(a ?? null) === JSON.stringify(b ?? null);
const pairKey = (e) => `${e.paint_a}|${e.paint_b}`;

/** Changes between two snapshots: { paints: [...], equivalents: [...], sources?: [...] }. */
export function diffSnapshots(base, head) {
  const changes = [];
  const baseSources = new Map((base.sources ?? []).map((s) => [s.id, s]));
  for (const s of head.sources ?? []) {
    const old = baseSources.get(s.id);
    if (!same(old, s)) changes.push({ op: "source_upsert", source: s, before: old ?? null });
  }
  const baseById = new Map(base.paints.filter((p) => p.id).map((p) => [p.id, p]));

  for (const p of head.paints) {
    if (!p.id) { changes.push({ op: "insert", paint: p }); continue; }
    const old = baseById.get(p.id);
    if (!old) { changes.push({ op: "insert", paint: p }); continue; }
    for (const field of FIELDS) {
      if (!same(old[field], p[field])) changes.push({ op: "update", id: p.id, field, before: old[field] ?? null, after: p[field] ?? null });
    }
    if (!same(old.colour, p.colour)) changes.push({ op: "update", id: p.id, field: "colour", before: old.colour ?? null, after: p.colour ?? null });
    const oldEans = new Map((old.barcodes ?? []).map((b) => [b.ean, b]));
    const newEans = new Map((p.barcodes ?? []).map((b) => [b.ean, b]));
    for (const [ean, b] of newEans) if (!oldEans.has(ean)) changes.push({ op: "barcode_add", id: p.id, barcode: b });
    for (const ean of oldEans.keys()) if (!newEans.has(ean)) changes.push({ op: "barcode_remove", id: p.id, ean });
  }

  const oldPairs = new Map(base.equivalents.map((e) => [pairKey(e), e]));
  const newPairs = new Map(head.equivalents.map((e) => [pairKey(e), e]));
  for (const [k, e] of newPairs) if (!oldPairs.has(k)) changes.push({ op: "equivalent_add", pair: e });
  for (const [k, e] of oldPairs) if (!newPairs.has(k)) changes.push({ op: "equivalent_remove", pair: e });
  return changes;
}

/** Reads every paint, the equivalents and the sources at a commit. */
export function snapshotAt(ref, cwd = new URL("..", import.meta.url).pathname) {
  const git = (...args) => execFileSync("git", args, { cwd, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  const files = git("ls-tree", "-r", "--name-only", ref, "--", "paints").split("\n").filter((f) => f.endsWith(".json"));
  const paints = files.flatMap((f) => JSON.parse(git("show", `${ref}:${f}`)));
  let equivalents = [];
  try { equivalents = JSON.parse(git("show", `${ref}:equivalents.json`)); } catch { /* not there yet */ }
  let sources = [];
  try { sources = JSON.parse(git("show", `${ref}:sources.json`)).colour_sources ?? []; } catch { /* not there yet */ }
  return { paints, equivalents, sources };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const [base, head] = process.argv.slice(2);
  if (!base || !head) { console.error("Usage: node scripts/diff-for-import.mjs <base> <head>"); process.exit(1); }
  process.stdout.write(JSON.stringify(diffSnapshots(snapshotAt(base), snapshotAt(head)), null, 1) + "\n");
}
