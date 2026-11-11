import contextlib
import io
import json
import os
import tempfile
import unittest

import build_coasters


def way(way_id, points, **tags):
    return {'type': 'way', 'id': way_id, 'tags': {'roller_coaster': 'track', **tags},
            'geometry': [{'lat': lat, 'lon': lon} for lat, lon in points]}


class BuildCoastersTest(unittest.TestCase):
    def test_groups_ways_and_adds_osm_id_and_centroid(self):
        elements = [
            way(7, [(0.0, 0.0), (0.0, 0.002)], name='Test'),
            way(3, [(0.0, 0.002), (0.002, 0.002)]),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = os.path.join(tmp, 'in.json'), os.path.join(tmp, 'out.json')
            json.dump({'elements': elements}, open(src, 'w'))
            with contextlib.redirect_stdout(io.StringIO()):
                build_coasters.main(src, dst)
            coasters = json.load(open(dst))['coasters']
        self.assertEqual(len(coasters), 1)
        self.assertEqual(coasters[0]['osm_id'], 3)
        lat, lon = coasters[0]['centroid']
        self.assertAlmostEqual(lat, 0.002 / 3, places=6)
        self.assertAlmostEqual(lon, 0.004 / 3, places=6)


if __name__ == '__main__':
    unittest.main()
