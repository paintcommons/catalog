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
    def test_review_changes_are_limited_to_listed_candidates(self):
        review = ROOT / 'reports/arcturus-review'
        proposals = json.loads((review / 'colour-proposals.json').read_text())
        conflicts = json.loads((review / 'conflict-proposals.json').read_text())
        base = json.loads((review / 'summary.json').read_text())['clean_import_commit']
        files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', base, '--', 'paints'], cwd=ROOT, text=True).splitlines()
        old = [p for f in files if f.endswith('.json') for p in json.loads(subprocess.check_output(['git', 'show', f'{base}:{f}'], cwd=ROOT, text=True))]
        current = [p for f in (ROOT / 'paints').glob('*/*.json') for p in json.loads(f.read_text())]
        by_id = {p['id']: p for p in current if p.get('id')}
        changes = {p['id']: p for p in proposals}
        for p in old:
            if p.get('id') in changes:
                candidate = changes[p['id']]
                self.assertEqual(candidate['before'], p)
                self.assertEqual(by_id[p['id']], candidate['after'])
                self.assertEqual({k:v for k,v in p.items() if k != 'colour'},
                                 {k:v for k,v in candidate['after'].items() if k != 'colour'})
            else:
                self.assertIn(p, current)
        additions = [c['after'] for c in conflicts if c['proposal'] == 'add-candidate']
        for p in additions: self.assertIn(p, current)
        self.assertEqual(len(current), len(old) + len(additions))
        self.assertEqual(len(changes), 370)
        self.assertEqual(len(additions), 76)
        for p in proposals:
            source = p['selected_source']
            self.assertGreaterEqual(module.distance(p['before']['colour']['hex'], p['after']['colour']['hex']), .08)
            self.assertEqual(p['after']['colour']['hex'], source['hex'])
            self.assertEqual(p['status'], 'pending-review')

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
