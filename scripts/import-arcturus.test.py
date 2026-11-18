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
        ttc_rows = json.loads((review / 'ttc-colour-comparisons.json').read_text())
        ttc_proposals = [p for p in ttc_rows if p['colour_differs']]
        conflicts = json.loads((review / 'conflict-proposals.json').read_text())
        base = json.loads((review / 'summary.json').read_text())['review_base_commit']
        files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', base, '--', 'paints'], cwd=ROOT, text=True).splitlines()
        old = [p for f in files if f.endswith('.json') for p in json.loads(subprocess.check_output(['git', 'show', f'{base}:{f}'], cwd=ROOT, text=True))]
        current = [p for f in (ROOT / 'paints').glob('*/*.json') for p in json.loads(f.read_text())]
        key = lambda p: p.get('id') or (p['brand'], p['range'], p['code'], p['name'])
        by_key = {key(p): p for p in current}
        changes = {key(p['before']): p for p in proposals + ttc_proposals}
        for p in old:
            if key(p) in changes:
                candidate = changes[key(p)]
                self.assertEqual(candidate['before'], p)
                self.assertEqual(by_key[key(p)], candidate['after'])
                allowed = {'colour'}
                if candidate.get('review_decision'):
                    self.assertEqual((p['brand'], p['code']), ('Two Thin Coats', '10044'))
                    self.assertEqual(candidate['after']['type'], 'metallic')
                    allowed.add('type')
                self.assertEqual({k:v for k,v in p.items() if k not in allowed},
                                 {k:v for k,v in candidate['after'].items() if k not in allowed})
            else:
                self.assertIn(p, current)
        additions = [c['after'] for c in conflicts if c['proposal'] == 'add-candidate']
        for p in additions: self.assertIn(p, current)
        self.assertEqual(len(current), len(old) + len(additions))
        self.assertEqual(len(changes), 370 + 167)
        self.assertEqual(len(additions), 76)
        for p in proposals:
            source = p['selected_source']
            self.assertGreaterEqual(module.distance(p['before']['colour']['hex'], p['after']['colour']['hex']), .08)
            self.assertEqual(p['after']['colour']['hex'], source['hex'])
            self.assertEqual(p['status'], 'pending-review')

    def test_ttc_comparisons_match_pinned_values_and_keep_unchanged_hex_provenance(self):
        spec = importlib.util.spec_from_file_location('ttc', ROOT / 'scripts/import-ttc.py')
        ttc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ttc)
        swatches = {p['source_index']: p for p in ttc.read_swatches()}
        rows = json.loads((ROOT / 'reports/arcturus-review/ttc-colour-comparisons.json').read_text())
        self.assertEqual(len(rows), 180)
        self.assertEqual(sum(r['substantial'] for r in rows), 23)
        self.assertEqual(sum(r['match'] == 'explicit alias' for r in rows), 5)
        self.assertEqual(sum(r['identity_review'] for r in rows), 1)
        for row in rows:
            source = swatches[row['source_index']]
            self.assertEqual(row['source_name'], source['name'])
            self.assertEqual(row['gerinfact_colour']['hex'], source['hex'])
            if row['review_decision']:
                self.assertEqual(row['before']['code'], '10044')
                self.assertEqual(row['after']['colour'], dict(hex='#CDA24E', gradient=['#4F442C', '#CDA24E'], source='ttc-dragons-gold-composite-review'))
                self.assertEqual(row['after']['type'], 'metallic')
            else:
                self.assertEqual(row['after']['colour']['hex'], source['hex'])
            self.assertEqual(row['substantial'], module.distance(row['before']['colour']['hex'], source['hex']) >= .08)
            if row['colour_differs']:
                self.assertEqual(row['status'], 'pending-review')
                if not row['review_decision']:
                    self.assertEqual(row['after']['colour']['source'], ttc.COLOUR_SOURCE)
            else:
                self.assertEqual(row['before'], row['after'])

    def test_chart_samples_are_reference_only_and_distances_are_consistent(self):
        report = json.loads((ROOT / 'reports/arcturus-review/ttc-chart-references.json').read_text())
        rows = report['comparisons']
        self.assertEqual(len(rows), 180)
        self.assertEqual(len({r['code'] for r in rows}), 180)
        self.assertEqual(len(report['charts']), 3)
        by_code = {r['code']: r for r in rows}
        # Wave 2 places glazes before washes in the PDF, unlike SKU order.
        self.assertEqual((by_code['10115']['grid_row'], by_code['10115']['grid_column']), (9, 4))
        self.assertEqual((by_code['10112']['grid_row'], by_code['10112']['grid_column']), (10, 4))
        for row in rows:
            self.assertGreater(row['samples'], 1000)
            self.assertAlmostEqual(row['current_to_reference'], module.distance(row['current_hex'], row['reference_median']), places=6)
            self.assertAlmostEqual(row['gerinfact_to_reference'], module.distance(row['gerinfact_hex'], row['reference_median']), places=6)
        gold = next(r for r in rows if r['code'] == '10044')
        self.assertLess(gold['current_to_reference'], gold['gerinfact_to_reference'])
        self.assertLess(gold['nearest_chart_pixels']['current']['normalised_radius'],
                        gold['nearest_chart_pixels']['gerinfact']['normalised_radius'])

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
