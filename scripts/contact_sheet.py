"""Draw coaster outlines on one HTML page so we can judge them by eye.

Usage: python3 -I contact_sheet.py <coasters.json> <out.html>
"""
import html
import json
import math
import random
import sys

FAMOUS = ['Nemesis', 'The Smiler', 'Steel Vengeance', 'Millennium Force', 'Kingda Ka',
          'Fury 325', 'Taron', 'Blue Fire', 'Stealth', 'Icon', 'The Big One', 'Wicker Man',
          'Maverick', 'Expedition GeForce', 'Lightning Rod', 'Formula Rossa', 'Shambhala',
          'Helix', 'Voltron Nevera', 'Velocicoaster']


def usable(c):
    return c['length_m'] >= 150 and 'name' in c['tags'] and c['loose_ends'] <= 2 and c['vertices'] >= 40


def svg(c, size=180, pad=10):
    lat0 = sum(p[0] for l in c['lines'] for p in l) / sum(len(l) for l in c['lines'])
    k = math.cos(math.radians(lat0))
    xy = [[(p[1] * k, -p[0]) for p in l] for l in c['lines']]
    xs = [x for l in xy for x, _ in l]
    ys = [y for l in xy for _, y in l]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
    s = (size - 2 * pad) / span
    ox = pad + ((size - 2 * pad) - (max(xs) - min(xs)) * s) / 2
    oy = pad + ((size - 2 * pad) - (max(ys) - min(ys)) * s) / 2
    paths = ''.join(
        '<polyline points="%s"/>' % ' '.join('%.1f,%.1f' % (ox + (x - min(xs)) * s, oy + (y - min(ys)) * s) for x, y in l)
        for l in xy)
    return '<svg viewBox="0 0 %d %d">%s</svg>' % (size, size, paths)


def card(c):
    t = c['tags']
    meta = '%s m · %d ends · %d pts%s' % (c['length_m'], c['loose_ends'], c['vertices'], ' · wd' if 'wikidata' in t else '')
    return '<figure>%s<figcaption><b>%s</b><span>%s</span></figcaption></figure>' % (
        svg(c), html.escape(t.get('name', '(unnamed)')), meta)


def main(src, dst):
    coasters = json.load(open(src))['coasters']
    rng = random.Random(7)

    famous = []
    for name in FAMOUS:
        hits = [c for c in coasters if c['tags'].get('name', '').lower() == name.lower()]
        if hits:
            famous.append(max(hits, key=lambda c: c['length_m']))

    good = [c for c in coasters if usable(c)]
    rejected = [c for c in coasters if c['length_m'] >= 150 and not usable(c)]
    sections = [
        ('Famous coasters (%d of %d found)' % (len(famous), len(FAMOUS)), famous),
        ('Random sample of the %d that pass the filter' % len(good), rng.sample(good, 60)),
        ('Random sample of the %d that fail it' % len(rejected), rng.sample(rejected, 24)),
    ]

    body = ''.join('<h2>%s</h2><div class="grid">%s</div>' % (html.escape(h), ''.join(card(c) for c in cs))
                   for h, cs in sections)
    page = '''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trackdown outline check</title>
<style>
:root { --bg:#faf8f5; --fg:#1d1b19; --muted:#6f6a64; --card:#fff; --line:#d6462c; --edge:#e8e3dc; }
@media (prefers-color-scheme: dark) { :root { --bg:#161514; --fg:#eeeae4; --muted:#9b958d; --card:#211f1d; --line:#ff7a5c; --edge:#33302c; } }
body { margin:0; padding:24px 16px 64px; background:var(--bg); color:var(--fg); font:14px/1.4 system-ui, sans-serif; }
h1 { font-size:22px; margin:0 0 4px; } h2 { font-size:16px; margin:32px 0 12px; }
p { color:var(--muted); margin:0; max-width:60ch; }
.grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(160px, 1fr)); gap:12px; }
figure { margin:0; background:var(--card); border:1px solid var(--edge); border-radius:10px; padding:8px; }
svg { width:100%; aspect-ratio:1; display:block; }
polyline { fill:none; stroke:var(--line); stroke-width:2.2; stroke-linejoin:round; stroke-linecap:round; }
figcaption { display:flex; flex-direction:column; gap:2px; margin-top:4px; }
figcaption b { font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
figcaption span { color:var(--muted); font-size:12px; }
</style>
<h1>Trackdown outline check</h1>
<p>Track outlines from OpenStreetMap, north at the top. "ends" counts loose track ends (0 means a full circuit, 2 a shuttle). "wd" means the track links to Wikidata. Map data &copy; OpenStreetMap contributors (ODbL).</p>
''' + body
    open(dst, 'w').write(page)
    print('famous found:', [c['tags']['name'] for c in famous])
    print('missing:', [n for n in FAMOUS if n.lower() not in {c['tags']['name'].lower() for c in famous}])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
