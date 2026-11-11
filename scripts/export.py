"""Write the app's coaster data and the puzzle candidate shortlist.

Usage: python3 -I export.py <stats.json> <coasters.json> <countries.geojson> <app coasters.json> <candidates.json>
"""
import json
import os
import re
import sys

# Run with python3 -I, which leaves this folder off the import path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import country  # noqa: E402
from match import match  # noqa: E402
from outline import svg_path  # noqa: E402

CANDIDATE_COUNT = 120
WILD_MOUSE = re.compile(r'wild(e)? ?maus|wild mouse', re.I)


def is_valid(row):
    if (row.get('height_m') or 0) > 140 or (row.get('speed_kmh') or 0) > 260:
        return False
    if (row.get('inversions') or 0) > 14 or (row.get('length_m') or 0) > 2600:
        return False
    text = ' '.join(str(row.get(k) or '') for k in ('name', 'article')).lower()
    if 'euthanasia' in text or 'alpine coaster' in text:
        return False
    return 'alpine' not in (row.get('type') or '').lower()


def is_kiddie(row):
    height, length = row.get('height_m'), row.get('length_m')
    return (height is not None and height < 10) or (length is not None and length < 250)


def good_outline(c):
    return c['length_m'] >= 150 and c['loose_ends'] <= 2 and c['vertices'] >= 40


def is_operating(c):
    return (c['status'] or '').lower().startswith(('operating', 'open'))


def main(stats_path, osm_path, countries_path, app_out, candidates_out):
    rows = [r for r in json.load(open(stats_path)) if is_valid(r)]
    osm = json.load(open(osm_path))['coasters']
    countries = country.load(countries_path)
    matched = match(osm, rows)

    coasters, candidates = [], []
    for r in rows:
        track = matched.get(r['id'])
        if r['lat'] is not None:
            where = countries.lookup(r['lat'], r['lon'])
        elif track:
            where = countries.lookup(*track['centroid'])
        else:
            where = None
        c = {
            'id': r['id'], 'name': r['name'], 'park': r['park'], 'country': where,
            'opened': r['opened'], 'manufacturer': r['manufacturer'],
            'height_m': r['height_m'], 'speed_kmh': r['speed_kmh'], 'length_m': r['length_m'],
            'inversions': r['inversions'], 'status': r['status'], 'article': r['article'],
            'path': svg_path(track['lines']) if track and good_outline(track) else None,
        }
        coasters.append(c)
        clues = ('opened', 'height_m', 'speed_kmh', 'manufacturer', 'country', 'park')
        kind = ' '.join(str(r.get(k) or '') for k in ('type', 'model'))
        if c['path'] and all(c[k] is not None for k in clues) and not is_kiddie(r) and not WILD_MOUSE.search(kind):
            candidates.append(c)

    candidates.sort(key=lambda c: (not is_operating(c), -c['height_m']))
    json.dump({'coasters': coasters}, open(app_out, 'w'), separators=(',', ':'), ensure_ascii=False)
    json.dump(candidates[:CANDIDATE_COUNT], open(candidates_out, 'w'), indent=1, ensure_ascii=False)
    print('coasters exported:', len(coasters))
    print('  with an outline:', sum(1 for c in coasters if c['path']))
    print('  with a country:', sum(1 for c in coasters if c['country']))
    print('puzzle candidates: %d (kept %d)' % (len(candidates), min(len(candidates), CANDIDATE_COUNT)))


if __name__ == '__main__':
    main(*sys.argv[1:6])
