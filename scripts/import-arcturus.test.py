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
        # The separately tested TTC follow-up adds 39 paints and enriches its
        # 180 Arcturus records with manufacturer identifiers.
        self.assertEqual(len(current), len(old) + 7964 + 39)
        for p in current:
            if not p.get('id') and p['brand'] != 'Two Thin Coats':
                self.assertEqual(p['colour']['source'], module.SOURCE)
                self.assertEqual(p['barcodes'], [])

    def test_source_integrity_and_decision_accounting(self):
        # Parsing verifies every snapshot's Git blob hash and RGB/hex consistency.
        rows = module.read_upstream()
        self.assertEqual(len(rows), 9909)
        decisions = json.loads((module.REPORT / 'decisions.json').read_text())
        self.assertEqual(len(decisions), len(rows))
        self.assertEqual(len({(r['file'], r['line']) for r in decisions}), len(rows))
        counts = collections.Counter(r['decision'] for r in decisions)
        self.assertEqual(counts['added'], 7964)
        self.assertEqual(sum(v for k, v in counts.items() if k.startswith('withheld-')), 127)

    def test_full_mit_notice_and_rights_exception_are_distributed(self):
        notice = (ROOT / 'THIRD_PARTY_NOTICES.md').read_text()
        self.assertIn((module.VENDOR / 'LICENSE').read_text().strip(), notice)
        self.assertIn('Rick Fleuren', notice)
        self.assertIn('Miniature Painter Pro', notice)
        self.assertIn('does not remove these upstream terms', notice)
        source = next(s for s in json.loads((ROOT / 'sources.json').read_text())['colour_sources'] if s['id'] == module.SOURCE)
        self.assertIn('MIT', source['licence'])
        self.assertIn(module.REVISION, source['url'])


if __name__ == '__main__': unittest.main()
