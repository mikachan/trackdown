"""Pull coaster stats out of Wikipedia infoboxes and report coverage.

Usage: python3 -I parse_infoboxes.py <pages.json> <coasters.json> <out.json>
"""
import json
import re
import sys
from collections import Counter


def boxes(text):
    """Every {{Infobox roller coaster ...}} in an article, braces matched."""
    out = []
    for m in re.finditer(r'\{\{\s*Infobox[ _]roller[ _]coaster', text, re.I):
        i, depth = m.start(), 0
        while i < len(text):
            if text.startswith('{{', i):
                depth += 1
                i += 2
            elif text.startswith('}}', i):
                depth -= 1
                i += 2
                if depth == 0:
                    break
            else:
                i += 1
        out.append(text[m.start():i])
    return out


def fields(box):
    """Top-level |key = value pairs, ignoring pipes inside nested templates and links."""
    out, depth, start = {}, 0, None
    body = box[2:-2]
    parts, i = [], 0
    while i < len(body):
        two = body[i:i + 2]
        if two in ('{{', '[['):
            depth += 1
            i += 2
        elif two in ('}}', ']]'):
            depth -= 1
            i += 2
        elif body[i] == '|' and depth == 0:
            parts.append(i)
            i += 1
        else:
            i += 1
    parts.append(len(body))
    for a, b in zip(parts, parts[1:]):
        k, eq, v = body[a + 1:b].partition('=')
        if eq:
            out[k.strip()] = v.strip()
    return out


def clean(v):
    v = re.sub(r'<ref[^>]*/>|<ref.*?</ref>|<!--.*?-->', '', v, flags=re.S)
    v = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', v)
    return v.strip()


def number(v):
    m = re.search(r'\d[\d,]*(?:\.\d+)?', clean(v or ''))
    return float(m.group().replace(',', '')) if m else None


def year(v):
    v = clean(v or '')
    m = re.search(r'\{\{\s*start date[^|]*\|\s*(\d{4})', v, re.I) or re.search(r'\b(1[89]\d\d|20\d\d)\b', v)
    return int(m.group(1)) if m else None


def text(v):
    v = clean(v or '')
    v = re.sub(r'\{\{[^{}]*\}\}', '', v)
    return re.sub(r'\s+', ' ', v).strip() or None


def metric(f, ft_key, m_key, factor=0.3048):
    if number(f.get(m_key)) is not None:
        return round(number(f[m_key]), 1)
    if number(f.get(ft_key)) is not None:
        return round(number(f[ft_key]) * factor, 1)
    return None


def main(src, osm_src, dst):
    pages = json.load(open(src))
    rows = []
    for title, wikitext in pages.items():
        for box in boxes(wikitext):
            f = fields(box)
            speed = number(f.get('speed_km/h'))
            if speed is None and number(f.get('speed_mph')) is not None:
                speed = number(f['speed_mph']) * 1.609344
            rows.append({
                'article': title,
                'name': text(f.get('name')) or title,
                'park': text(f.get('location')),
                'status': text(f.get('status')),
                'opened': year(f.get('opened')),
                'manufacturer': text(f.get('manufacturer')),
                'height_m': metric(f, 'height_ft', 'height_m'),
                'drop_m': metric(f, 'drop_ft', 'drop_m'),
                'length_m': metric(f, 'length_ft', 'length_m'),
                'speed_kmh': round(speed, 1) if speed is not None else None,
                'inversions': int(number(f['inversions'])) if number(f.get('inversions')) is not None else None,
                'rcdb': text(f.get('rcdb_number')),
            })
    json.dump(rows, open(dst, 'w'), indent=1)

    stats = ['height_m', 'drop_m', 'length_m', 'speed_kmh', 'inversions', 'opened', 'manufacturer']
    print('coasters with an infobox:', len(rows))
    for s in stats:
        print('  %-12s %d' % (s, sum(1 for r in rows if r[s] is not None)))
    core = ['height_m', 'length_m', 'speed_kmh', 'inversions', 'opened']
    print('  all five of height, length, speed, inversions, opened:',
          sum(1 for r in rows if all(r[s] is not None for s in core)))
    print('  status:', Counter((r['status'] or '?').split(' ')[0].lower() for r in rows).most_common(5))

    # Sanity check: values that look like unit or parsing mistakes.
    odd = [r for r in rows if (r['height_m'] or 0) > 160 or (r['speed_kmh'] or 0) > 250 or (r['inversions'] or 0) > 15]
    print('  suspicious values:', [(r['name'], r['height_m'], r['speed_kmh'], r['inversions']) for r in odd][:10])

    osm_names = {c['tags']['name'].lower() for c in json.load(open(osm_src))['coasters']
                 if 'name' in c['tags'] and c['length_m'] >= 150 and c['loose_ends'] <= 2 and c['vertices'] >= 40}
    matched = {r['name'].lower() for r in rows} & osm_names
    print('  OSM outlines (of %d) whose name matches an infobox: %d' % (len(osm_names), len(matched)))


if __name__ == '__main__':
    main(*sys.argv[1:4])
