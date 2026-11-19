// Writes a Stipplewise export (the JSON returned by its catalog-export function) into this
// checkout, replacing paints/ entirely so ranges that disappeared don't linger. Used by the
// "Sync from Stipplewise" workflow; validate.mjs --base HEAD then refuses removed paints.
//   node scripts/apply-export.mjs <export.json>
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve, relative } from "node:path";

const root = fileURLToPath(new URL("..", import.meta.url));
const { files, report } = JSON.parse(readFileSync(process.argv[2], "utf8"));
if (!files || typeof files !== "object" || !files["sources.json"]) throw new Error("Not a catalog export");

const ALLOWED = /^(paints\/[a-z0-9-]+\/[a-z0-9-]+\.json|sources\.json|equivalents\.json|aliases\.json)$/;
const writes = Object.entries(files).map(([path, text]) => {
  const target = resolve(root, path);
  const inside = relative(root, target);
  if (inside.startsWith("..") || !ALLOWED.test(inside) || typeof text !== "string") throw new Error(`Refusing to write ${path}`);
  return [target, text];
});

// Everything checked; only now touch the working tree.
rmSync(resolve(root, "paints"), { recursive: true, force: true });
for (const [target, text] of writes) {
  mkdirSync(dirname(target), { recursive: true });
  writeFileSync(target, text);
}
console.log(`Applied: ${report.paints} paints, ${report.barcodes} barcodes, ${report.colours} colours, ${report.equivalents} equivalents.`);
if (report.unknownSources && Object.keys(report.unknownSources).length) console.log(`Colours withheld (source not yet listed): ${JSON.stringify(report.unknownSources)}`);
