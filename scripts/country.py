"""Offline point → country lookup over Natural Earth admin-0 boundaries (public domain)."""
import json


def inside(pt, poly):
    """Ray-casting point-in-polygon, poly is a list of (lat, lon)."""
    y, x = pt
    hit = False
    for (y1, x1), (y2, x2) in zip(poly, poly[1:]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            hit = not hit
    return hit


class Countries:
    def __init__(self, polygons):
        # Each entry: (name, outer ring as (lat, lon) list, bbox)
        self.polygons = polygons

    def lookup(self, lat, lon, near=0.3):
        for name, ring, (s, w, n, e) in self.polygons:
            if s <= lat <= n and w <= lon <= e and inside((lat, lon), ring):
                return name
        # Coastal parks can sit just outside a simplified coastline: take the
        # nearest boundary edge if it's close enough.
        best, best_d = None, near ** 2
        for name, ring, (s, w, n, e) in self.polygons:
            if s - near <= lat <= n + near and w - near <= lon <= e + near:
                for a, b in zip(ring, ring[1:]):
                    d = segment_distance_sq((lat, lon), a, b)
                    if d < best_d:
                        best, best_d = name, d
        return best


def segment_distance_sq(p, a, b):
    (py, px), (ay, ax), (by, bx) = p, a, b
    dy, dx = by - ay, bx - ax
    length_sq = dy * dy + dx * dx
    t = 0 if length_sq == 0 else max(0, min(1, ((py - ay) * dy + (px - ax) * dx) / length_sq))
    cy, cx = ay + t * dy, ax + t * dx
    return (py - cy) ** 2 + (px - cx) ** 2


def load(path):
    polygons = []
    for f in json.load(open(path))['features']:
        name = f['properties'].get('NAME_EN') or f['properties'].get('NAME')
        g = f['geometry']
        parts = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        for part in parts:
            ring = [(lat, lon) for lon, lat in part[0]]
            lats = [p[0] for p in ring]
            lons = [p[1] for p in ring]
            polygons.append((name, ring, (min(lats), min(lons), max(lats), max(lons))))
    return Countries(polygons)
