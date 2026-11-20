"""Preservation and source checks for the TTC enrichment, including paints without ids."""
import collections
import importlib.util
import json
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('ttc', ROOT / 'scripts/import-ttc.py')
ttc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ttc)

# These invariants describe the catalog as of the TTC reconciliation (#7). Later syncs from
# Stipplewise add paints and barcodes, so the checks read that commit, not the working tree.
PINNED = '371540c00e690879e12ffe2accf64a37aaf911ca'


def pinned_files():
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', PINNED, '--', 'paints'], cwd=ROOT, text=True).splitlines()
    return {f: json.loads(subprocess.check_output(['git', 'show', f'{PINNED}:{f}'], cwd=ROOT, text=True)) for f in names if f.endswith('.json')}



class TTCPreservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = ttc.baseline()
        cls.current = pinned_files()
        original_ids = {p['id'] for rows in cls.old.values() for p in rows if p.get('id')}
        # Verify the separately approved stops, then test TTC against its original snapshot.
        stops = {r['id']: r for r in json.loads((ROOT/'reports/arcturus-review/colour-proposals.json').read_text()) if r['apply']}
        for paints in cls.current.values():
            for i, paint in enumerate(paints):
                row = stops.get(paint.get('id'))
                if row:
                    assert paint == row['after']
                    paints[i] = row['before']
            for paint in paints:
                if paint.get('id') not in original_ids: paint.pop('id', None)

    def test_every_unrelated_file_is_identical(self):
        old = {f: p for f, p in self.old.items() if not f.startswith('paints/duncan-rhodes/')}
        current = {f: p for f, p in self.current.items() if not f.startswith(('paints/two-thin-coats/', 'paints/duncan-rhodes/'))}
        stable = lambda files: {f: sorted(rows, key=lambda p: (p['brand'], str(p['range']), str(p['code']), p['name'])) for f, rows in files.items()}
        self.assertEqual(stable(current), stable(old))

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
