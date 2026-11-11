"""Group OSM track segments into coasters and score how usable each outline is.

Usage: python3 -I build_coasters.py <tracks.json> <out.json>
"""
import json
import math
import sys
from collections import defaultdict

from country import inside


def key(pt):
    return (round(pt['lat'], 7), round(pt['lon'], 7))


def metres(a, b):
    lat = math.radians((a[0] + b[0]) / 2)
    dx = (b[1] - a[1]) * 111320 * math.cos(lat)
    dy = (b[0] - a[0]) * 110540
    return math.hypot(dx, dy)


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, i):
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, a, b):
        self.parent[self.find(a)] = self.find(b)


def main(src, dst):
    ways = [e for e in json.load(open(src))['elements'] if e['type'] == 'way']

    tracks, areas = [], []
    for w in ways:
        t = w.get('tags', {})
        pts = [key(p) for p in w['geometry']]
        closed = pts[0] == pts[-1]
        if t.get('attraction') == 'roller_coaster' and closed and t.get('roller_coaster') != 'track':
            areas.append({'id': w['id'], 'tags': t, 'poly': pts})
        else:
            tracks.append({'id': w['id'], 'tags': t, 'pts': pts})

    # Segments that share any vertex belong to the same coaster.
    uf = UnionFind(len(tracks))
    owner = {}
    for i, tr in enumerate(tracks):
        for p in tr['pts']:
            if p in owner:
                uf.union(i, owner[p])
            else:
                owner[p] = i

    groups = defaultdict(list)
    for i in range(len(tracks)):
        groups[uf.find(i)].append(tracks[i])

    # Index footprint areas on a coarse grid so naming lookups stay fast.
    grid = defaultdict(list)
    for a in areas:
        lats = [p[0] for p in a['poly']]
        lons = [p[1] for p in a['poly']]
        a['bbox'] = (min(lats), min(lons), max(lats), max(lons))
        for gy in range(int(min(lats) * 100), int(max(lats) * 100) + 1):
            for gx in range(int(min(lons) * 100), int(max(lons) * 100) + 1):
                grid[(gy, gx)].append(a)

    coasters = []
    for segs in groups.values():
        length = sum(metres(a, b) for s in segs for a, b in zip(s['pts'], s['pts'][1:]))
        # Count how many segment ends touch nothing else: 0 for a full circuit,
        # 2 for a shuttle, lots for a gappy trace.
        degree = defaultdict(int)
        for s in segs:
            for a, b in zip(s['pts'], s['pts'][1:]):
                degree[a] += 1
                degree[b] += 1
        loose_ends = sum(1 for d in degree.values() if d == 1)
        vertices = len(degree)

        tags = {}
        for s in segs:
            for k in ('name', 'wikidata', 'wikipedia', 'operator', 'start_date'):
                if k in s['tags'] and k not in tags:
                    tags[k] = s['tags'][k]

        mid = segs[0]['pts'][len(segs[0]['pts']) // 2]
        for a in grid.get((int(mid[0] * 100), int(mid[1] * 100)), []):
            b = a['bbox']
            if b[0] <= mid[0] <= b[2] and b[1] <= mid[1] <= b[3] and inside(mid, a['poly']):
                for k in ('name', 'wikidata', 'wikipedia', 'operator', 'start_date'):
                    if k in a['tags'] and k not in tags:
                        tags[k] = a['tags'][k]
                tags['area_id'] = a['id']
                break

        verts = list(degree)
        coasters.append({
            'osm_id': min(s['id'] for s in segs),
            'centroid': [sum(p[0] for p in verts) / len(verts), sum(p[1] for p in verts) / len(verts)],
            'ways': [s['id'] for s in segs],
            'tags': tags,
            'length_m': round(length),
            'vertices': vertices,
            'loose_ends': loose_ends,
            'lines': [[[p[0], p[1]] for p in s['pts']] for s in segs],
        })

    coasters.sort(key=lambda c: -c['length_m'])
    json.dump({'coasters': coasters}, open(dst, 'w'))

    def count(f):
        return sum(1 for c in coasters if f(c))

    print('coasters (connected track groups):', len(coasters))
    print('  >= 150 m of track:', count(lambda c: c['length_m'] >= 150))
    print('  >= 150 m and named:', count(lambda c: c['length_m'] >= 150 and 'name' in c['tags']))
    print('  ... and with wikidata:', count(lambda c: c['length_m'] >= 150 and 'wikidata' in c['tags']))
    print('  >= 150 m, named, <= 2 loose ends, >= 40 vertices:',
          count(lambda c: c['length_m'] >= 150 and 'name' in c['tags'] and c['loose_ends'] <= 2 and c['vertices'] >= 40))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
