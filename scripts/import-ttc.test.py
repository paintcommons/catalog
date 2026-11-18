"""Preservation and source checks for the TTC enrichment, including paints without ids."""
import collections
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('ttc', ROOT / 'scripts/import-ttc.py')
ttc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ttc)


class TTCPreservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = ttc.baseline()
        cls.current = {str(f.relative_to(ROOT)): json.loads(f.read_text())
                       for f in (ROOT / 'paints').glob('*/*.json')}
        review = ROOT / 'reports/arcturus-review/ttc-colour-summary.json'
        if review.exists():
            # In the draft replacement branch, test the pinned TTC import
            # baseline here. The review invariants separately check every
            # current record against that baseline and its explicit proposals.
            base = json.loads(review.read_text())['review_base_commit']
            files = ttc.subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', base, '--', 'paints'], cwd=ROOT, text=True).splitlines()
            cls.current = {f: json.loads(ttc.subprocess.check_output(['git', 'show', f'{base}:{f}'], cwd=ROOT, text=True))
                           for f in files if f.endswith('.json')}

    def test_every_unrelated_file_is_identical(self):
        old = {f: p for f, p in self.old.items() if not f.startswith('paints/duncan-rhodes/')}
        current = {f: p for f, p in self.current.items() if not f.startswith('paints/two-thin-coats/')}
        self.assertEqual(current, old)

    def test_existing_paints_preserve_identity_colour_and_other_fields(self):
        facts = json.loads((ttc.SOURCES / 'ttc-manufacturer-products.json').read_text())
        self.assertEqual(len(facts), 180)
        by_name = {ttc.normalise(f['name']): f for f in facts}
        changes = json.loads((ttc.REPORT / 'existing-record-changes.json').read_text())
        expected_pairs = []
        total = 0
        for file, paints in self.old.items():
            if not file.startswith('paints/duncan-rhodes/'):
                continue
            replacements = self.current[file.replace('/duncan-rhodes/', '/two-thin-coats/')]
            self.assertEqual(len(paints), len(replacements))
            by_code = {p['code']: p for p in replacements}
            for before in paints:
                fact = by_name[ttc.normalise(ttc.ALIASES.get(before['name'], before['name']))]
                after = by_code[fact['code']]
                self.assertEqual(after['brand'], 'Two Thin Coats')
                self.assertEqual(after['name'], fact['name'])
                self.assertEqual(after['barcodes'], [dict(ean=fact['ean'], source='published', source_url=fact['source_url'])])
                # Strict whitelist: includes unchanged colour, type, range, id,
                # status, and any future fields present in the pinned source.
                allowed = {'brand', 'name', 'code', 'barcodes'}
                self.assertEqual({k: v for k, v in before.items() if k not in allowed},
                                 {k: v for k, v in after.items() if k not in allowed})
                expected_pairs.append((before, after))
                total += 1
        self.assertEqual(total, 180)
        self.assertEqual([(x['before'], x['after']) for x in changes], expected_pairs)

    def test_new_colours_are_limited_to_exact_dark_arts_source_matches(self):
        facts = json.loads((ttc.SOURCES / 'ttc-additions.json').read_text())
        added = [p for f, rows in self.current.items()
                 if f in ('paints/two-thin-coats/dark-arts.json', 'paints/two-thin-coats/effects-paints.json')
                 for p in rows]
        self.assertEqual(len(added), 39)
        self.assertEqual(collections.Counter(p['type'] for p in added),
                         {'acrylic': 21, 'metallic': 3, 'ink': 6, 'effect': 8, 'medium': 1})
        self.assertEqual({p['name'] for p in added}, {p['name'] for p in facts})
        swatches = {p['name']: p for p in ttc.read_swatches()}
        self.assertEqual(sum('colour' in p for p in added), 30)
        for p in added:
            if p['range'] == 'Dark Arts':
                self.assertEqual(p['colour'], dict(hex=swatches[p['name']]['hex'], gradient=None, source=ttc.COLOUR_SOURCE))
            else:
                self.assertNotIn('colour', p)
            self.assertNotIn('id', p)
            self.assertIsNone(p['code'])
            self.assertEqual(p['barcodes'], [])
            fact = next(f for f in facts if f['name'] == p['name'])
            self.assertEqual((p['range'], p['type']), (fact['range'], fact['type']))
            self.assertTrue(fact['source_url'].startswith(('https://transatlantisgames.com/', 'https://store.duncanrhodes.com/')))


if __name__ == '__main__':
    unittest.main()
