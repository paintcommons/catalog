// Sends one commit's changes to Stipplewise's catalog-import in numbered batches, then writes the
// combined response for import-report.mjs. Used by the "Import into Stipplewise" workflow.
//   node scripts/send-import.mjs <changes.json> <result.json>
// Environment: CATALOG_SYNC_SECRET, GITHUB_SHA, AUTHOR, PR_URL (optional), OVERRIDE ("true" when the
// pull request carries the colour-override label), IMPORT_URL (optional, for testing).
import { readFileSync, writeFileSync, realpathSync } from "node:fs";
import { pathToFileURL } from "node:url";

export const BATCH_SIZE = 1000;

/** Splits changes into batches; source changes always travel in the first one. */
export function toBatches(changes, size = BATCH_SIZE, { override = false } = {}) {
  const marked = changes.map((c) => (override && c.op === "update" && c.field === "colour" ? { ...c, override: true } : c));
  const sources = marked.filter((c) => c.op === "source_upsert");
  const rest = marked.filter((c) => c.op !== "source_upsert");
  const batches = [];
  let current = [...sources];
  for (const c of rest) {
    if (current.length >= size) { batches.push(current); current = []; }
    current.push(c);
  }
  batches.push(current);
  return batches;
}

/** Adds up the responses of every batch into one, shaped like a single-batch response. */
export function combine(responses) {
  return {
    commit: responses[0]?.commit,
    already_imported: responses.every((r) => r.already_imported),
    applied: responses.reduce((n, r) => n + (r.applied ?? 0), 0),
    conflicts: responses.reduce((n, r) => n + (r.conflicts ?? 0), 0),
    failed_inserts: responses.reduce((n, r) => n + (r.failed_inserts ?? 0), 0),
    complete: responses.at(-1)?.complete ?? responses.every((r) => r.already_imported),
    results: responses.flatMap((r) => r.results ?? []),
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) {
  const [changesFile, resultFile] = process.argv.slice(2);
  const { CATALOG_SYNC_SECRET, GITHUB_SHA, AUTHOR, PR_URL, OVERRIDE } = process.env;
  const url = process.env.IMPORT_URL ?? "https://ibexwyfkzydpgdzkgoma.supabase.co/functions/v1/catalog-import";
  const batches = toBatches(JSON.parse(readFileSync(changesFile, "utf8")), BATCH_SIZE, { override: OVERRIDE === "true" });
  const responses = [];
  for (const [batch, changes] of batches.entries()) {
    const body = JSON.stringify({ commit: GITHUB_SHA, author: AUTHOR || null, pr_url: PR_URL || null, changes, batch, batches: batches.length });
    let res;
    for (let attempt = 1; ; attempt++) {
      res = await fetch(url, { method: "POST", headers: { Authorization: `Bearer ${CATALOG_SYNC_SECRET}`, "Content-Type": "application/json" }, body, signal: AbortSignal.timeout(150_000) }).catch((e) => ({ ok: false, status: 0, text: async () => String(e) }));
      // Re-sending a batch is a no-op in Stipplewise, so retrying after a timeout is safe.
      if (res.ok || attempt === 3 || (res.status >= 400 && res.status < 500)) break;
      await new Promise((r) => setTimeout(r, 5000 * attempt));
    }
    if (!res.ok) { console.error(`Batch ${batch + 1} of ${batches.length} failed with HTTP ${res.status}: ${await res.text()}`); process.exit(1); }
    responses.push(await res.json());
    console.log(`Batch ${batch + 1} of ${batches.length}: ${changes.length} changes sent.`);
  }
  writeFileSync(resultFile, JSON.stringify(combine(responses)));
}
