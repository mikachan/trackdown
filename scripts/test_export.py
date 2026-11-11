import contextlib
import io
import json
import os
import tempfile
import unittest

import export

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')

COASTER_KEYS = {'id', 'name', 'park', 'country', 'opened', 'manufacturer', 'height_m', 'speed_kmh',
                'length_m', 'inversions', 'status', 'article', 'path'}


def row(**kw):
    base = {'id': 'x', 'article': 'X', 'name': 'X', 'park': 'P', 'lat': None, 'lon': None, 'type': None,
            'model': None, 'status': 'Operating', 'opened': 2000, 'manufacturer': 'Intamin', 'height_m': 30.0,
            'drop_m': None, 'length_m': 800.0, 'speed_kmh': 90.0, 'inversions': 0, 'rcdb': None}
    return {**base, **kw}


class ValidityTest(unittest.TestCase):
    def test_rejects_known_bad(self):
        self.assertFalse(export.is_valid(row(name='Rough Riders', height_m=1280.2)))
        self.assertFalse(export.is_valid(row(name='Euthanasia Coaster', height_m=500.0, speed_kmh=360.0, inversions=7)))
        self.assertFalse(export.is_valid(row(name='Smoky Mountain Alpine Coaster', height_m=1200.0)))
        self.assertFalse(export.is_valid(row(name='Forest Flyer', type='Alpine')))

    def test_accepts_real_coaster(self):
        self.assertTrue(export.is_valid(row(name='Steel Vengeance', height_m=62.5, speed_kmh=119.1, inversions=4, length_m=1749.6)))

    def test_kiddie(self):
        self.assertTrue(export.is_kiddie(row(height_m=8.0)))
        self.assertTrue(export.is_kiddie(row(length_m=200.0)))
        self.assertFalse(export.is_kiddie(row(name='Taron', height_m=30.0, length_m=1320.0)))
        self.assertFalse(export.is_kiddie(row(height_m=None, length_m=None)))


class ExportTest(unittest.TestCase):
    def test_export_shape(self):
        rows = [row(id='taron-phantasialand', name='Taron', park='Phantasialand', lat=5.0, lon=5.0),
                row(id='nowhere', name='Nowhere', lat=None, lon=None)]
        track = [[5.0 + i * 0.0002, 5.0 + (i % 7) * 0.0003] for i in range(60)]
        osm = [{'osm_id': 1, 'tags': {'name': 'Taron'}, 'centroid': [5.006, 5.001], 'length_m': 900,
                'loose_ends': 0, 'vertices': 60, 'lines': [track]}]
        with tempfile.TemporaryDirectory() as tmp:
            paths = {k: os.path.join(tmp, k + '.json') for k in ('stats', 'osm', 'app', 'cand')}
            json.dump(rows, open(paths['stats'], 'w'))
            json.dump({'coasters': osm}, open(paths['osm'], 'w'))
            with contextlib.redirect_stdout(io.StringIO()):
                export.main(paths['stats'], paths['osm'], os.path.join(FIXTURES, 'countries.geojson'),
                            paths['app'], paths['cand'])
            coasters = json.load(open(paths['app']))['coasters']
        self.assertEqual(len(coasters), 2)
        for c in coasters:
            self.assertEqual(set(c), COASTER_KEYS)
        taron = next(c for c in coasters if c['id'] == 'taron-phantasialand')
        self.assertTrue(taron['path'].startswith('M'))
        self.assertEqual(taron['country'], 'Squareland')
        self.assertIsNone(next(c for c in coasters if c['id'] == 'nowhere')['path'])


if __name__ == '__main__':
    unittest.main()
