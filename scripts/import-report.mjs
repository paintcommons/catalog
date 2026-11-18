// Turns catalog-import's response into a job summary and, when something was refused, an issue body.
//   node scripts/import-report.mjs <response.json> <commit> <pr url or "">
import { readFileSync, writeFileSync, appendFileSync } from "node:fs";

const [file, commit, pr] = process.argv.slice(2);
const res = JSON.parse(readFileSync(file, "utf8"));
const results = res.results ?? [];
const refused = results.filter((r) => r.outcome === "conflict" || r.outcome === "skipped");
const line = (r) => `- **${r.outcome}** ${r.op}${r.name ? ` "${r.name}"` : ""}${r.id ? ` (\`${r.id}\`)` : ""}${r.detail ? `: ${r.detail}` : ""}`;
const summary = res.already_imported
  ? `Commit ${commit} was already imported.`
  : `Imported ${commit}${pr ? ` (${pr})` : ""} into Stipplewise: ${res.applied ?? 0} applied, ${results.filter((r) => r.outcome === "unchanged").length} already the same, ${refused.length} refused.\n\n${refused.map(line).join("\n")}`;
if (process.env.GITHUB_STEP_SUMMARY) appendFileSync(process.env.GITHUB_STEP_SUMMARY, summary + "\n");
console.log(summary);
const paused = (res.failed_inserts ?? 0) > 0
  ? `\n\n**${res.failed_inserts} new paint${res.failed_inserts === 1 ? " was" : "s were"} refused, so the hourly sync from Stipplewise is paused** (it would otherwise drop them from this repository). Fix them in a new pull request (add the missing source, correct the duplicate, or remove the paint); paints without an id are sent again with every commit, and the sync resumes once a commit imports completely.`
  : "";
if (refused.length) {
  writeFileSync("import-issue.md", `Some changes from ${pr || commit} didn't reach Stipplewise. Stipplewise keeps its current values for these, and the next hourly sync will write them back here.${paused}\n\n${refused.map(line).join("\n")}\n\nTo apply one anyway, open a new pull request starting from the current \`main\`. A colour refused for priority can be applied with the \`colour-override\` label.\n`);
}
process.exit(res.conflicts > 0 || (res.failed_inserts ?? 0) > 0 ? 2 : 0);
