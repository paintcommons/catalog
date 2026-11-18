// Checks every data file. No dependencies: `node scripts/validate.mjs` (Node 20+).
// Pass --base <git ref> to also refuse removed paints and changed ids compared with that commit.
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { execFileSync } from "node:child_process";

const root = new URL("..", import.meta.url).pathname;
const errors = [];
const fail = (where, message) => errors.push(`${where}: ${message}`);

const TYPES = new Set(["acrylic", "wash", "metallic", "effect", "speedpaint", "medium", "ink", "varnish", "primer", "other"]);
const BARCODE_SOURCES = new Set(["calculated", "published", "scan"]);
const KEYS = new Set(["id", "brand", "range", "code", "name", "type", "barcodes", "colour", "status", "finish", "manufacturer_colour_family"]);
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

const sources = readJson(join(root, "sources.json")) ?? { colour_sources: [] };
const publishedColourSources = new Set(sources.colour_sources.filter((s) => s.status === "published").map((s) => s.id));

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
      if (!(c?.gradient === null || (Array.isArray(c?.gradient) && c.gradient.length >= 2 && c.gradient.every((h) => HEX.test(h))))) fail(at, "colour.gradient must be null or two or more uppercase hex colours");
      if (!publishedColourSources.has(c?.source)) fail(at, `colour.source "${c?.source}" isn't a published source in sources.json`);
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

// Compared with a base commit: paints are never removed and ids never change.
const baseAt = process.argv.indexOf("--base");
if (baseAt > 0) {
  const base = process.argv[baseAt + 1];
  const listed = execFileSync("git", ["ls-tree", "-r", "--name-only", base, "paints"], { cwd: root, encoding: "utf8" }).split("\n").filter((f) => f.endsWith(".json"));
  for (const file of listed) {
    let old;
    try { old = JSON.parse(execFileSync("git", ["show", `${base}:${file}`], { cwd: root, encoding: "utf8" })); } catch { continue; }
    for (const p of old) if (p.id && !ids.has(p.id)) fail(file, `"${p.name}" (${p.id}) was removed. Paints are never deleted; set "status": "discontinued" instead.`);
  }
}

if (errors.length) {
  console.error(errors.join("\n"));
  console.error(`\n${errors.length} problem${errors.length === 1 ? "" : "s"} in ${count} paints.`);
  process.exit(1);
}
console.log(`OK: ${count} paints, ${eans.size} barcodes, ${equivalents.length} equivalents.`);
