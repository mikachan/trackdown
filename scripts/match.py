"""Match OSM track outlines to Wikipedia infobox rows by name and distance."""
import re
import unicodedata
from collections import defaultdict

from build_coasters import metres

MAX_DISTANCE_M = 2000


def normalise(name):
    s = name.replace('ø', 'o').replace('Ø', 'O').replace('æ', 'ae').replace('ß', 'ss')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return re.sub(r'^the ', '', s)


def match(osm, rows):
    """Return {row id: osm coaster}. Each OSM coaster is used at most once (nearest row wins)."""
    by_name = defaultdict(list)
    for c in osm:
        if c['tags'].get('name'):
            by_name[normalise(c['tags']['name'])].append(c)
    rows_by_name = defaultdict(list)
    for r in rows:
        rows_by_name[normalise(r['name'])].append(r)

    pairs = []
    for r in rows:
        if r.get('lat') is None:
            continue
        for c in by_name.get(normalise(r['name']), []):
            d = metres((r['lat'], r['lon']), tuple(c['centroid']))
            if d <= MAX_DISTANCE_M:
                pairs.append((d, r['id'], c))

    result, used = {}, set()
    for _, row_id, c in sorted(pairs, key=lambda p: p[0]):
        if row_id not in result and c['osm_id'] not in used:
            result[row_id] = c
            used.add(c['osm_id'])

    # Rows without coordinates: only when the name is unique on both sides.
    for r in rows:
        if r.get('lat') is not None or r['id'] in result:
            continue
        key = normalise(r['name'])
        cands = by_name.get(key, [])
        if len(cands) == 1 and len(rows_by_name[key]) == 1 and cands[0]['osm_id'] not in used:
            result[r['id']] = cands[0]
            used.add(cands[0]['osm_id'])
    return result
