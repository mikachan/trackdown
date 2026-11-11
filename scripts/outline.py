"""Turn OSM track geometry into small SVG paths for a 0 0 100 100 viewBox."""
import math

SIZE = 100
PAD = 4
TOLERANCE = 0.35  # in viewBox units


def simplify(line, tolerance):
    """Ramer–Douglas–Peucker over 2D points."""
    if len(line) < 3:
        return [list(p) for p in line]
    (ay, ax), (by, bx) = line[0], line[-1]
    dy, dx = by - ay, bx - ax
    norm = math.hypot(dy, dx)
    worst, index = -1.0, 0
    for i, (py, px) in enumerate(line[1:-1], 1):
        if norm == 0:
            d = math.hypot(py - ay, px - ax)
        else:
            d = abs(dx * (ay - py) - dy * (ax - px)) / norm
        if d > worst:
            worst, index = d, i
    if worst <= tolerance:
        return [list(line[0]), list(line[-1])]
    return simplify(line[:index + 1], tolerance)[:-1] + simplify(line[index:], tolerance)


def svg_path(lines, tolerance=TOLERANCE):
    lat0 = sum(p[0] for l in lines for p in l) / sum(len(l) for l in lines)
    k = math.cos(math.radians(lat0))
    xy = [[(p[1] * k, -p[0]) for p in l] for l in lines]
    xs = [x for l in xy for x, _ in l]
    ys = [y for l in xy for _, y in l]
    inner = SIZE - 2 * PAD
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
    s = inner / span
    ox = PAD + (inner - (max(xs) - min(xs)) * s) / 2
    oy = PAD + (inner - (max(ys) - min(ys)) * s) / 2
    parts = []
    for l in xy:
        pts = simplify([((x - min(xs)) * s + ox, (y - min(ys)) * s + oy) for x, y in l], tolerance)
        parts.append('M' + ' L'.join('%.1f,%.1f' % (x, y) for x, y in pts))
    return ' '.join(parts)
