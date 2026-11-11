"""Download the wikitext of every English Wikipedia article using {{Infobox roller coaster}}.

Usage: python3 -I fetch_wikipedia.py <out.json>
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = 'https://en.wikipedia.org/w/api.php'
UA = 'trackdown-research/0.1 (personal hobby project; contact via github.com/mikachan)'


def get(params):
    params = {**params, 'format': 'json', 'formatversion': '2', 'maxlag': '5'}
    req = urllib.request.Request(API + '?' + urllib.parse.urlencode(params), headers={'User-Agent': UA})
    for attempt in range(5):
        try:
            data = json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(int(e.headers.get('Retry-After') or 0) or 10 * (attempt + 1))
            continue
        if data.get('error', {}).get('code') == 'maxlag':
            time.sleep(5 * (attempt + 1))
            continue
        return data
    raise RuntimeError('Wikipedia kept reporting lag')


def main(dst):
    titles, cont = [], {}
    while True:
        data = get({'action': 'query', 'list': 'embeddedin', 'eititle': 'Template:Infobox roller coaster',
                    'einamespace': '0', 'eilimit': '500', **cont})
        titles += [p['title'] for p in data['query']['embeddedin']]
        if 'continue' not in data:
            break
        cont = data['continue']
    print('articles using the infobox:', len(titles))

    pages = {}
    for i in range(0, len(titles), 50):
        data = get({'action': 'query', 'prop': 'revisions', 'rvprop': 'content', 'rvslots': 'main',
                    'titles': '|'.join(titles[i:i + 50])})
        for p in data['query']['pages']:
            if 'revisions' in p:
                pages[p['title']] = p['revisions'][0]['slots']['main']['content']
        time.sleep(3)
    json.dump(pages, open(dst, 'w'))
    print('downloaded:', len(pages))


if __name__ == '__main__':
    main(sys.argv[1])
