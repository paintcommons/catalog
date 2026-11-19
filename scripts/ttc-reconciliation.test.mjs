import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {snapshotAt} from './diff-for-import.mjs';
test('TTC reconciliation retires exactly 180 legacy IDs and preserves every other record and swatch',()=>{
 const root=new URL('..',import.meta.url);
 const before=snapshotAt('e15f0c5121b076b5a846f9d4c24b93ec09655030').paints;
 const current=readdirSync(new URL('paints/',root)).flatMap(brand=>readdirSync(new URL(`paints/${brand}/`,root)).filter(f=>f.endsWith('.json')).flatMap(file=>JSON.parse(readFileSync(new URL(`paints/${brand}/${file}`,root)))));
 const byId=new Map(current.map(p=>[p.id,p]));
 const aliases=JSON.parse(readFileSync(new URL('aliases.json',root)));
 const oldById=new Map(before.map(p=>[p.id,p]));
 assert.equal(aliases.length,180);assert.equal(current.length,8307);
 for(const p of before){if(p.brand==='Duncan Rhodes')continue;assert.deepEqual(byId.get(p.id),p,p.name);}
 for(const a of aliases){const old=oldById.get(a.alias_id),canonical=byId.get(a.canonical_id);assert.equal(old.brand,'Duncan Rhodes');assert.equal(canonical.brand,'Two Thin Coats');assert.deepEqual(canonical.colour,old.colour);assert.equal(canonical.range,old.range);assert.ok(!byId.has(a.alias_id));}
 assert.equal(current.filter(p=>p.brand==='Two Thin Coats').length,219);
 assert.ok(!current.some(p=>p.brand==='Duncan Rhodes'));
});
