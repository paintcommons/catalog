import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('review', ROOT / 'scripts/propose-arcturus-review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewPreservation(unittest.TestCase):
    def test_every_record_matches_baseline_or_its_explicit_stop_proposal(self):
        expected = review.baseline()
        rows = json.loads((review.OUT / 'colour-proposals.json').read_text())
        self.assertEqual(len(rows), 370)
        applied = {r['id']:r for r in rows if r['apply']}
        self.assertTrue(applied)
        for file, paints in expected.items():
            for i, paint in enumerate(paints):
                if paint.get('id') in applied:
                    row = applied[paint['id']]
                    self.assertEqual(row['before'], paint)
                    paints[i] = row['after']
        current = {str(f.relative_to(ROOT)):json.loads(f.read_text()) for f in (ROOT/'paints').glob('*/*.json')}
        self.assertEqual(current, expected)
        for row in rows:
            b, a, source = row['before'], row['after'], row['selected_source']
            self.assertEqual(a['colour']['hex'], b['colour']['hex'])
            self.assertEqual({k:v for k,v in a.items() if k!='colour'}, {k:v for k,v in b.items() if k!='colour'})
            if row['apply']:
                self.assertFalse(source['name_disagrees'])
                self.assertEqual(a['colour']['gradient'], [source['hex'], b['colour']['hex'], None])
                self.assertLess(review.imp.oklab(source['hex'])[0], review.imp.oklab(b['colour']['hex'])[0])
                self.assertEqual(a['colour']['source'], review.imp.SOURCE)
                self.assertTrue(row['requires_colour_override'])
            else:
                self.assertEqual(a, b)
            if b['colour']['source']=='manual-override':
                self.assertEqual(row['disposition'], 'preserve-manual-override')


if __name__=='__main__':unittest.main()
