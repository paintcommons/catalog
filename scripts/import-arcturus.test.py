import collections
import importlib.util
import json
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('arcturus', ROOT / 'scripts/import-arcturus.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ImportInvariants(unittest.TestCase):
    def test_all_existing_records_are_identical(self):
        current = [p for f in (ROOT / 'paints').glob('*/*.json') for p in json.loads(f.read_text())]
        by_id = {p['id']: p for p in current if p.get('id')}
        files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', module.BASE, '--', 'paints'], cwd=ROOT, text=True).splitlines()
        old = [p for f in files if f.endswith('.json') for p in json.loads(subprocess.check_output(['git', 'show', f'{module.BASE}:{f}'], cwd=ROOT, text=True))]
        self.assertEqual(len(old), 1981)
        review = ROOT / 'reports/arcturus-review/colour-proposals.json'
        proposals = {r['id']:r for r in json.loads(review.read_text()) if r['apply']} if review.exists() else {}
        for p in old:
            if p['id'] in proposals:
                row = proposals[p['id']]
                self.assertEqual(row['before'], p)
                self.assertEqual(by_id[p['id']], row['after'])
                self.assertEqual(row['after']['colour']['hex'], p['colour']['hex'])
                self.assertEqual({k:v for k,v in p.items() if k!='colour'}, {k:v for k,v in row['after'].items() if k!='colour'})
                self.assertNotEqual(p['colour']['source'], 'manual-override')
            else:
                self.assertEqual(by_id[p['id']], p, p['name'])
        self.assertEqual(len(current), len(old) + 6287)
        for p in current:
            if not p.get('id'):
                self.assertEqual(p['colour']['source'], module.SOURCE)
                self.assertEqual(p['source'], module.SOURCE)
                self.assertEqual(p['barcodes'], [])

    def test_source_integrity_and_decision_accounting(self):
        # Parsing verifies every snapshot's Git blob hash and RGB/hex consistency.
        rows = module.read_upstream()
        self.assertEqual(len(rows), 9909)
        decisions = json.loads((module.REPORT / 'decisions.json').read_text())
        self.assertEqual(len(decisions), len(rows))
        self.assertEqual(len({(r['file'], r['line']) for r in decisions}), len(rows))
        counts = collections.Counter(r['decision'] for r in decisions)
        self.assertEqual(counts['added'], 6284)
        self.assertEqual(counts['excluded-scope'], 1673)
        self.assertEqual(counts['added-conflict-resolved'], 3)
        self.assertEqual(counts['duplicate-conflict-alias'], 2)

    def test_scope_and_conflict_identities(self):
        current = [p for f in (ROOT / 'paints').glob('*/*.json') for p in json.loads(f.read_text())]
        new = [p for p in current if not p.get('id')]
        self.assertFalse(any(p['brand'] in {'Kimera Kolors', 'Arteza', 'Revell', 'Italeri', 'Acrilex', 'FolkArt', 'Golden', 'Apple Barrel', 'Liquitex'} for p in new))
        self.assertFalse(any(p['brand'] == 'Citadel' and (p['range'] or '').startswith('Foundation') for p in new))
        ledger = json.loads((module.REPORT / 'conflict-review.json').read_text())
        admitted = [r for r in ledger if r['disposition'] == 'admitted-normalized-identity']
        self.assertEqual(len(admitted), 3)
        self.assertEqual(sum(r['disposition'].startswith('held-') for r in ledger), 33)
        for row in admitted:
            r = row['source']
            self.assertEqual(len({module.norm(p['name']) for p in row['alternatives']}), 1)
            matches = [p for p in new if (p['brand'], p['range'], p['code'], p['name']) == (r['brand'], r['range'], r['code'], r['name'])]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]['colour']['hex'], r['hex'])
        for p in new:
            if p['brand'] == 'Reaper' and p['range'] in ('Master Series Paints Core Colors', 'Master Series Paints Bones', 'Master Series Paints Pathfinder'):
                self.assertEqual(p['type'], 'acrylic')

    def test_reviewed_semantic_duplicates_placements_statuses_and_types(self):
        new = [p for f in (ROOT/'paints').glob('*/*.json') for p in json.loads(f.read_text()) if not p.get('id')]
        self.assertTrue(all(p['range']=='Spray' for p in new if p['brand']=='Citadel'))
        metals = [p for p in new if (p['brand'],p['range'])==('The Army Painter','Warpaints Fanatic Metallic')]
        self.assertEqual(len(metals),12)
        self.assertTrue(all(p['type']=='metallic' and p['status']=='current' for p in metals))
        self.assertIn('Evil Chrome',{p['name'] for p in metals})
        for p in new:
            if p['brand']=='Vallejo' or p['brand']=='The Army Painter' and (p['range'].startswith('Warpaints (original)') or p['range']=='Speedpaint (original)'):
                self.assertEqual(p['status'],'discontinued')
            if p['brand']=='Vallejo' and p['range'] in ('Model Color','Game Color','Panzer Aces','Game Air'):
                self.assertEqual(p['type'],'acrylic')
            if p['brand']=='The Army Painter' and p['range']=='Warpaints Fanatic Wash':
                self.assertEqual(p['type'],'wash')
                self.assertNotIn(p['name'],{'Brush-On Primer','Wash Medium','Dry Blood','Fresh Rust'})
        primer=next(p for p in new if p['brand']=='The Army Painter' and p['name']=='Brush-On Primer' and p['range']=='Warpaints Fanatic')
        medium=next(p for p in new if p['brand']=='The Army Painter' and p['name']=='Wash Medium' and p['range']=='Warpaints Fanatic')
        self.assertEqual(primer['type'],'primer');self.assertEqual(medium['type'],'medium')

    def test_full_mit_notice_and_rights_exception_are_distributed(self):
        notice = (ROOT / 'THIRD_PARTY_NOTICES.md').read_text()
        self.assertIn((module.VENDOR / 'LICENSE').read_text().strip(), notice)
        self.assertIn('Rick Fleuren', notice)
        self.assertIn('Miniature Painter Pro', notice)
        source = next(s for s in json.loads((ROOT / 'sources.json').read_text())['colour_sources'] if s['id'] == module.SOURCE)
        self.assertIn('MIT', source['licence'])
        self.assertIn(module.REVISION, source['url'])
        self.assertEqual(source['priority'], 40)
        self.assertEqual(source['licence'], 'MIT')
        self.assertEqual(source['notice'], 'THIRD_PARTY_NOTICES.md')


if __name__ == '__main__': unittest.main()
