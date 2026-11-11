import json, sys, collections
d = json.load(open(sys.argv[1]))
ways = [e for e in d['elements'] if e['type'] == 'way']
print('ways', len(ways))
c = collections.Counter()
for w in ways:
    t = w.get('tags', {})
    kind = ('track' if t.get('roller_coaster') == 'track' else '') + ('+attr' if t.get('attraction') == 'roller_coaster' else '')
    closed = w['geometry'][0] == w['geometry'][-1]
    c[(kind, 'closed' if closed else 'open', 'named' if 'name' in t else 'unnamed', 'wd' if 'wikidata' in t else '-')] += 1
for k, v in c.most_common(): print(v, k)
keys = collections.Counter(k for w in ways for k in w.get('tags', {}))
print(keys.most_common(30))
