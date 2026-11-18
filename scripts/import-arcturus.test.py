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
        for p in old: self.assertEqual(by_id[p['id']], p, p['name'])
        self.assertEqual(len(current), len(old) + 7389)
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
        self.assertEqual(counts['added'], 7385)
        self.assertEqual(counts['excluded-scope'], 579)
        self.assertEqual(counts['added-conflict-resolved'], 4)
        self.assertEqual(counts['duplicate-conflict-alias'], 2)

    def test_scope_and_conflict_identities(self):
        current = [p for f in (ROOT / 'paints').glob('*/*.json') for p in json.loads(f.read_text())]
        new = [p for p in current if not p.get('id')]
        self.assertFalse(any(p['brand'] in {'Kimera Kolors', 'Arteza', 'Revell', 'Italeri', 'Acrilex'} for p in new))
        self.assertFalse(any(p['brand'] == 'Citadel' and (p['range'] or '').startswith('Foundation') for p in new))
        ledger = json.loads((module.REPORT / 'conflict-review.json').read_text())
        admitted = [r for r in ledger if r['disposition'] == 'admitted-normalized-identity']
        self.assertEqual(len(admitted), 4)
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
