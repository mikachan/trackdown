import unittest

from match import match, normalise

M = 1 / 111_000  # roughly one metre in degrees of latitude


def osm(osm_id, name, lat, lon):
    return {'osm_id': osm_id, 'tags': {'name': name}, 'centroid': [lat, lon]}


def row(row_id, name, lat=None, lon=None):
    return {'id': row_id, 'name': name, 'lat': lat, 'lon': lon}


class NormaliseTest(unittest.TestCase):
    def test_normalise(self):
        self.assertEqual(normalise('The Smiler'), 'smiler')
        self.assertEqual(normalise('Fønix!'), 'fonix')
        self.assertEqual(normalise('  Blue   Fire '), 'blue fire')


class MatchTest(unittest.TestCase):
    def test_same_name_far_apart_not_matched(self):
        result = match([osm(1, 'Goliath', 34.4, -118.6)], [row('goliath-walibi-holland', 'Goliath', 52.44, 5.76)])
        self.assertEqual(result, {})

    def test_same_name_close_matched(self):
        result = match([osm(1, 'The Smiler', 52.9870, -1.8860)], [row('smiler', 'Smiler', 52.9870 + 300 * M, -1.8860)])
        self.assertEqual(result['smiler']['osm_id'], 1)

    def test_one_osm_coaster_only_used_once(self):
        coaster = osm(1, 'Nemesis', 50.0, 0.0)
        result = match([coaster], [row('far', 'Nemesis', 50.0 + 1800 * M, 0.0), row('near', 'Nemesis', 50.0 + 1000 * M, 0.0)])
        self.assertEqual(list(result), ['near'])

    def test_no_coords_unique_name(self):
        result = match([osm(1, 'Taron', 50.8, 6.88)], [row('taron', 'Taron')])
        self.assertEqual(result['taron']['osm_id'], 1)

    def test_no_coords_ambiguous_name(self):
        result = match([osm(1, 'Goliath', 34.4, -118.6), osm(2, 'Goliath', 52.44, 5.76)], [row('goliath', 'Goliath')])
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()
