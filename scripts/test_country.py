import os
import unittest

import country

FIXTURE = os.path.join(os.path.dirname(__file__), 'fixtures', 'countries.geojson')


class CountryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = country.load(FIXTURE)

    def test_inside(self):
        self.assertEqual(self.c.lookup(5, 5), 'Squareland')

    def test_inside_multipolygon(self):
        self.assertEqual(self.c.lookup(25, 5), 'Otherland')

    def test_near_coast(self):
        self.assertEqual(self.c.lookup(10.2, 5), 'Squareland')

    def test_open_sea(self):
        self.assertIsNone(self.c.lookup(15, 5))


if __name__ == '__main__':
    unittest.main()
