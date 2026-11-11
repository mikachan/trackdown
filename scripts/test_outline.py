import re
import unittest

from outline import simplify, svg_path


def points(path):
    return [(float(x), float(y)) for x, y in re.findall(r'(-?[\d.]+),(-?[\d.]+)', path)]


class SimplifyTest(unittest.TestCase):
    def test_simplify_keeps_corners(self):
        leg1 = [[0.0, i / 50] for i in range(51)]
        leg2 = [[i / 50, 1.0] for i in range(1, 51)]
        self.assertEqual(simplify(leg1 + leg2, 0.001), [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0]])


class SvgPathTest(unittest.TestCase):
    LINES = [[[51.0, 0.0], [51.001, 0.002], [51.002, 0.0]], [[51.0, 0.0], [50.999, 0.001]]]

    def test_path_fits_viewbox(self):
        for x, y in points(svg_path(self.LINES)):
            self.assertTrue(4 <= x <= 96 and 4 <= y <= 96, (x, y))

    def test_path_north_up(self):
        pts = points(svg_path(self.LINES))
        northmost = pts[2]  # 51.002 is the northernmost input point
        self.assertEqual(northmost[1], min(y for _, y in pts))

    def test_path_one_subpath_per_line(self):
        self.assertEqual(svg_path(self.LINES).count('M'), 2)


if __name__ == '__main__':
    unittest.main()
