import unittest

import parse_infoboxes


class SmokeTest(unittest.TestCase):
    def test_number_parses_feet(self):
        self.assertEqual(parse_infoboxes.number('205 ft'), 205.0)


if __name__ == '__main__':
    unittest.main()
