import unittest

from parse_infoboxes import coord, fields, slug


class CoordTest(unittest.TestCase):
    def test_coord_decimal(self):
        self.assertEqual(coord('{{coord|41.4822|N|82.6835|W|display=inline,title}}'), (41.4822, -82.6835))

    def test_coord_dms(self):
        lat, lon = coord('{{Coord|50|48|02|N|6|52|39|E}}')
        self.assertAlmostEqual(lat, 50.8006, places=3)
        self.assertAlmostEqual(lon, 6.8775, places=3)

    def test_coord_plain_signed(self):
        self.assertEqual(coord('{{coord|-33.95|151.2}}'), (-33.95, 151.2))

    def test_coords_alias_with_type_parameter(self):
        self.assertEqual(coord('{{Coords|43.1821|10.5447|display=inline,title}}'), (43.1821, 10.5447))
        lat, lon = coord('{{Coords|34|25|24.6|N|118|35|56|W|type:landmark_region:US-CA|display=title,inline}}')
        self.assertAlmostEqual(lat, 34.4235, places=3)
        self.assertAlmostEqual(lon, -118.5989, places=3)

    def test_coord_missing(self):
        self.assertIsNone(coord(''))


class SlugTest(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(slug('Goliath', 'Walibi Holland'), 'goliath-walibi-holland')
        self.assertEqual(slug('Fønix', 'Fårup Sommerland'), 'fonix-farup-sommerland')
        self.assertEqual(slug('Taron', None), 'taron')


class FieldsTest(unittest.TestCase):
    def test_type_and_model_fields_are_read(self):
        f = fields('{{Infobox roller coaster\n| name = Max\n| type = Steel\n| model = Wild Mouse\n}}')
        self.assertEqual((f['type'], f['model']), ('Steel', 'Wild Mouse'))


if __name__ == '__main__':
    unittest.main()
