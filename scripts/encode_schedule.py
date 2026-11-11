"""Lightly scramble Sarah's puzzle schedule so the public repo doesn't spoil answers.

This is not security: the app decodes it with the same key (app/src/lib/day.ts).

Usage: python3 -I encode_schedule.py <data/schedule.json> <app coasters.json> <app schedule.json>
"""
import base64
import json
import sys

KEY = 'trackdown-v1'


def _xor(data, key):
    k = key.encode()
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(data))


def encode(ids, key):
    return [base64.urlsafe_b64encode(_xor(i.encode(), key)).decode().rstrip('=') for i in ids]


def decode(days, key):
    return [_xor(base64.urlsafe_b64decode(d + '=' * (-len(d) % 4)), key).decode() for d in days]


def main(schedule_path, coasters_path, out_path):
    ids = json.load(open(schedule_path))['ids']
    known = {c['id']: c for c in json.load(open(coasters_path))['coasters']}
    unknown = [i for i in ids if i not in known]
    no_outline = [i for i in ids if i in known and not known[i]['path']]
    if unknown or no_outline:
        if unknown:
            print('unknown ids: %s' % ', '.join(unknown), file=sys.stderr)
        if no_outline:
            print('ids without an outline: %s' % ', '.join(no_outline), file=sys.stderr)
        sys.exit(1)
    json.dump({'v': 1, 'days': encode(ids, KEY)}, open(out_path, 'w'), indent=1)
    print('schedule: %d days' % len(ids))


if __name__ == '__main__':
    main(*sys.argv[1:4])
