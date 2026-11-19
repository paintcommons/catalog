// Checks every data file. No dependencies: `node scripts/validate.mjs` (Node 20+).
// Pass --base <git ref> to also refuse removed paints and changed ids compared with that commit.
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join, relative } from "node:path";
import { execFileSync } from "node:child_process";

const root = fileURLToPath(new URL("..", import.meta.url));
const errors = [];
const fail = (where, message) => errors.push(`${where}: ${message}`);

const TYPES = new Set(["acrylic", "wash", "metallic", "effect", "speedpaint", "medium", "ink", "varnish", "primer", "other"]);
const BARCODE_SOURCES = new Set(["calculated", "published", "scan"]);
const KEYS = new Set(["id", "brand", "range", "code", "name", "type", "barcodes", "colour", "status", "finish", "manufacturer_colour_family", "source"]);
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const HEX = /^#[0-9A-F]{6}$/;

export const slug = (text) => String(text ?? "").normalize("NFKD").replace(/[̀-ͯ]/g, "")
  .toLowerCase().replace(/&/g, " and ").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "general";

/** GTIN check digit (EAN-8, UPC-A, EAN-13, GTIN-14). */
export function validGtin(code) {
  if (!/^(\d{8}|\d{12,14})$/.test(code)) return false;
  const digits = code.split("").map(Number);
  const check = digits.pop();
  const sum = digits.reverse().reduce((s, d, i) => s + d * (i % 2 === 0 ? 3 : 1), 0);
  return (10 - (sum % 10)) % 10 === check;
}

const readJson = (path) => {
  try { return JSON.parse(readFileSync(path, "utf8")); } catch (e) { fail(relative(root, path), `not valid JSON (${e.message})`); return null; }
};
const files = (dir) => readdirSync(dir).flatMap((f) => {
  const p = join(dir, f);
  return statSync(p).isDirectory() ? files(p) : f.endsWith(".json") ? [p] : [];
});

// Licences a published source may carry (SPDX ids); notice: true means the licence asks for its credit
// and notice to travel with copies, so the source needs an attribution and a notice file here.
// LicenseRef-facts: factual values (names, codes, approximate colours) from a source that states no
// licence, published with credit and a notice; no licence is claimed for the source itself.
// Keep in step with PUBLISHABLE_LICENCES in Stipplewise's shared/commons.mjs.
const LICENCES = { "CC0-1.0": false, "LicenseRef-facts": true, "CC-BY-4.0": true, "MIT": true, "BSD-2-Clause": true, "BSD-3-Clause": true, "ISC": true };
const SOURCE_KEYS = new Set(["id", "name", "url", "method", "status", "licence", "attribution", "notice", "priority"]);
const sources = readJson(join(root, "sources.json")) ?? { colour_sources: [] };
const sourceIds = new Set();
for (const s of sources.colour_sources ?? []) {
  const at = `sources.json ${s?.id ?? "(no id)"}`;
  for (const k of Object.keys(s ?? {})) if (!SOURCE_KEYS.has(k)) fail(at, `unknown field "${k}"`);
  if (!/^[a-z0-9][a-z0-9-]*$/.test(s?.id ?? "")) fail(at, "id must be lowercase letters, digits and hyphens");
  else if (sourceIds.has(s.id)) fail(at, "id used twice"); else sourceIds.add(s.id);
  if (typeof s?.name !== "string" || !s.name.trim()) fail(at, "name is required");
  if (!["published", "withheld"].includes(s?.status)) fail(at, 'status must be "published" or "withheld"');
  if (!/^[A-Za-z0-9.+-]+$/.test(s?.licence ?? "")) fail(at, 'licence must be an SPDX id (like "MIT" or "CC0-1.0") or "unknown"');
  if (s?.priority !== undefined && !(Number.isInteger(s.priority) && s.priority >= 0 && s.priority <= 100)) fail(at, "priority must be a whole number from 0 to 100");
  if (s?.notice !== undefined && !existsSync(join(root, s.notice.split("#")[0]))) fail(at, `notice file ${s.notice} doesn't exist`);
  if (s?.status === "published") {
    if (!(s.licence in LICENCES)) fail(at, `licence ${s.licence} can't be published (allowed: ${Object.keys(LICENCES).join(", ")}); mark the source "withheld"`);
    else if (LICENCES[s.licence] && (!s.attribution?.trim() || !s.notice?.trim())) fail(at, `${s.licence} needs an attribution and a notice file (THIRD_PARTY_NOTICES.md)`);
  }
}
const publishedColourSources = new Set((sources.colour_sources ?? []).filter((s) => s.status === "published").map((s) => s.id));

const ids = new Map(), codes = new Map(), names = new Map(), eans = new Map();
let count = 0;
for (const path of files(join(root, "paints"))) {
  const where = relative(root, path);
  const list = readJson(path);
  if (!list) continue;
  if (!Array.isArray(list)) { fail(where, "must be an array of paints"); continue; }
  list.forEach((p, i) => {
    const at = `${where} #${i + 1}${p?.name ? ` (${p.name})` : ""}`;
    if (!p || typeof p !== "object") return fail(at, "not an object");
    count++;
    for (const k of Object.keys(p)) if (!KEYS.has(k)) fail(at, `unknown field "${k}"`);
    if (p.id !== undefined) {
      if (!UUID.test(p.id)) fail(at, "id must be a lowercase UUID (or left out for a new paint)");
      else if (ids.has(p.id)) fail(at, `id also used by ${ids.get(p.id)}`);
      else ids.set(p.id, at);
    }
    if (typeof p.brand !== "string" || !p.brand.trim()) fail(at, "brand is required");
    if (!(p.range === null || (typeof p.range === "string" && p.range.trim()))) fail(at, "range must be text or null");
    if (!(p.code === null || (typeof p.code === "string" && p.code.trim()))) fail(at, "code must be text or null");
    if (typeof p.name !== "string" || !p.name.trim()) fail(at, "name is required");
    if (!TYPES.has(p.type)) fail(at, `type must be one of ${[...TYPES].join(", ")}`);
    for (const [field,max] of [["finish",120],["manufacturer_colour_family",200]]) {
      const value=p[field];
      if (value !== undefined && value !== null && (typeof value !== "string" || !value.trim() || value.length>max)) fail(at, `${field} must be a non-empty string of up to ${max} characters, null, or omitted`);
    }
    if (!["current", "discontinued"].includes(p.status)) fail(at, 'status must be "current" or "discontinued"');
    if (p.source !== undefined && !publishedColourSources.has(p.source)) fail(at, `source "${p.source}" isn't a published source in sources.json`);
    const expected = `paints/${slug(p.brand)}/${slug(p.range)}.json`;
    if (where !== expected) fail(at, `belongs in ${expected}`);
    if (p.code) {
      const key = `${p.brand}|${p.code}`;
      if (codes.has(key)) fail(at, `code ${p.code} also used by ${codes.get(key)}`); else codes.set(key, at);
    }
    const nameKey = `${p.brand}|${p.range ?? ""}|${String(p.name).toLowerCase()}`;
    if (names.has(nameKey)) fail(at, `same brand, range and name as ${names.get(nameKey)}`); else names.set(nameKey, at);
    if (!Array.isArray(p.barcodes)) fail(at, "barcodes must be an array (can be empty)");
    else for (const b of p.barcodes) {
      if (!b || typeof b.ean !== "string" || !validGtin(b.ean)) { fail(at, `barcode ${b?.ean} has a wrong check digit or length`); continue; }
      if (!BARCODE_SOURCES.has(b.source)) fail(at, `barcode ${b.ean} source must be one of ${[...BARCODE_SOURCES].join(", ")}`);
      if (b.source === "published" && !/^https?:\/\//.test(b.source_url ?? "")) fail(at, `published barcode ${b.ean} needs a source_url`);
      for (const k of Object.keys(b)) if (!["ean", "source", "source_url"].includes(k)) fail(at, `barcode ${b.ean}: unknown field "${k}"`);
      if (eans.has(b.ean)) fail(at, `barcode ${b.ean} also on ${eans.get(b.ean)}`); else eans.set(b.ean, at);
    }
    if (p.colour !== undefined) {
      const c = p.colour;
      if (!c || !HEX.test(c.hex ?? "")) fail(at, "colour.hex must look like #A1B2C3 (uppercase)");
      // Gradients: speedpaints, washes and glazes hold up to three stops in the order pooled, true
      // colour, thinned (as far as the sources show them; apps generate the rest), and the true colour
      // is the paint's hex. Apps draw speedpaints as bands and washes and glazes as a smooth blend.
      // Metallics and colour-shift paints hold two or more stops sampled from the source.
      // A position the source doesn't show is null (only for these three-stop kinds).
      const g = c?.gradient;
      const shaded = p.type === "speedpaint" || p.type === "wash" || /\bwash(es)?\b|\bglaze/i.test(`${p.range ?? ""} ${p.name}`);
      if (!(g === null || (Array.isArray(g) && g.every((h) => HEX.test(h) || (shaded && h === null))))) fail(at, shaded ? "colour.gradient must be null or a list of uppercase hex colours (null for a position the source doesn't show)" : "colour.gradient must be null or a list of uppercase hex colours");
      else if (g && shaded) {
        if (g.length < 1 || g.length > 3 || !g.some(Boolean)) fail(at, "a speedpaint, wash or glaze's colour.gradient holds one to three stops: pooled, true colour, thinned");
        else if (g[1] && g[1] !== c.hex) fail(at, "the second gradient stop is the true colour and must equal colour.hex");
      } else if (g && g.length < 2) fail(at, "colour.gradient needs two or more stops");
      for (const k of Object.keys(c ?? {})) if (!["hex", "gradient", "source"].includes(k)) fail(at, `colour: unknown field "${k}"`);
    }
  });
}

const equivalents = readJson(join(root, "equivalents.json")) ?? [];
equivalents.forEach((e, i) => {
  const at = `equivalents.json #${i + 1}`;
  if (!ids.has(e.paint_a) || !ids.has(e.paint_b)) fail(at, "both paints must exist (by id)");
  if (e.paint_a === e.paint_b) fail(at, "a paint can't be its own equivalent");
});

// A merged duplicate remains addressable through its alias; unrelated removals are forbidden.
const aliases = existsSync(join(root, "aliases.json")) ? readJson(join(root, "aliases.json")) : [];
const aliasTargets = new Map();
if (!Array.isArray(aliases)) fail("aliases.json", "must be an array");
for (const a of Array.isArray(aliases) ? aliases : []) {
  if (!a || Object.keys(a).sort().join(",") !== "alias_id,canonical_id" || !UUID.test(a.alias_id) || !UUID.test(a.canonical_id)) { fail("aliases.json", "each alias needs two UUIDs"); continue; }
  if (a.alias_id === a.canonical_id || ids.has(a.alias_id) || !ids.has(a.canonical_id) || aliasTargets.has(a.alias_id)) fail("aliases.json", "alias must be unique, retired, and point directly to an existing paint");
  aliasTargets.set(a.alias_id, a.canonical_id);
}

// Compared with a base commit: paints are never removed and ids never change.
const baseAt = process.argv.indexOf("--base");
if (baseAt > 0) {
  const base = process.argv[baseAt + 1];
  let previousAliases = [];
  try { previousAliases = JSON.parse(execFileSync("git", ["show", `${base}:aliases.json`], { cwd: root, encoding: "utf8", stdio: ["ignore","pipe","ignore"] })); } catch { /* older catalogue */ }
  for (const a of previousAliases) if (aliasTargets.get(a.alias_id) !== a.canonical_id) fail("aliases.json", `Existing redirect ${a.alias_id} must be preserved.`);
  const listed = execFileSync("git", ["ls-tree", "-r", "--name-only", base, "paints"], { cwd: root, encoding: "utf8" }).split("\n").filter((f) => f.endsWith(".json"));
  for (const file of listed) {
    let old;
    try { old = JSON.parse(execFileSync("git", ["show", `${base}:${file}`], { cwd: root, encoding: "utf8" })); } catch { continue; }
    for (const p of old) if (p.id && !ids.has(p.id) && !aliasTargets.has(p.id)) fail(file, `"${p.name}" (${p.id}) was removed. Paints are never deleted; set "status": "discontinued" instead.`);
  }
}

if (errors.length) {
  console.error(errors.join("\n"));
  console.error(`\n${errors.length} problem${errors.length === 1 ? "" : "s"} in ${count} paints.`);
  process.exit(1);
}
console.log(`OK: ${count} paints, ${eans.size} barcodes, ${equivalents.length} equivalents.`);
