import {test} from 'node:test';
import assert from 'node:assert/strict';
import {diffSnapshots} from './diff-for-import.mjs';
const paint={id:'00000000-0000-4000-8000-000000000001',brand:'Test',name:'Paint',range:null,code:null,type:'acrylic',status:'current',barcodes:[]};
const snap=p=>({paints:[p],equivalents:[]});
test('optional metadata is diffed for imports and missing/null values are equivalent',()=>{
 const after={...paint,finish:'Matte',manufacturer_colour_family:'Published triad',status:'discontinued'};
 const changes=diffSnapshots(snap(paint),snap(after));
 assert.deepEqual(changes.map(c=>c.field).sort(),['finish','manufacturer_colour_family','status']);
 assert.ok(changes.every(c=>c.op==='update'));
 assert.deepEqual(diffSnapshots(snap(paint),snap({...paint,finish:null,manufacturer_colour_family:null})),[]);
 assert.deepEqual(diffSnapshots(snap(after),snap(paint)).find(c=>c.field==='finish').after,null);
});
