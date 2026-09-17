#!/usr/bin/env python3
"""Pull contact details for every member of the 194th General Court.

Each detail record is ~1.6 MB because it embeds every sponsored bill, but the
fields we want come first, so the response is truncated after a few KB.
"""
import json, re, subprocess, urllib.parse
from concurrent.futures import ThreadPoolExecutor

codes = [m['MemberCode'] for m in json.load(open('mem194.json'))]
FIELDS = ('Name', 'Branch', 'MemberCode', 'District', 'Party',
          'EmailAddress', 'RoomNumber', 'PhoneNumber', 'LeadershipPosition')

def grab(code):
    # A few member codes contain a space ("L M0"), so they must be encoded.
    url = ('https://malegislature.gov/api/GeneralCourts/194/LegislativeMembers/'
           + urllib.parse.quote(code, safe=''))
    head = subprocess.run(f'curl -s --max-time 60 "{url}" | head -c 4000',
                          shell=True, capture_output=True, text=True).stdout
    rec = {}
    for f in FIELDS:
        m = re.search(r'"%s":(null|"((?:[^"\\]|\\.)*)")' % f, head)
        rec[f] = json.loads(m.group(1)) if m else None
    return rec if rec.get('Name') else None

with ThreadPoolExecutor(max_workers=10) as ex:
    members = [r for r in ex.map(grab, codes) if r]

json.dump(members, open('members_detail.json', 'w'), indent=1)
print('fetched', len(members), 'of', len(codes))

from collections import Counter
dupes = {k: v for k, v in Counter((m['Branch'], m['District']) for m in members).items() if v > 1}
print('districts with more than one member on record:', len(dupes))
for k, v in sorted(dupes.items())[:10]:
    print('  ', k, v, [m['Name'] for m in members if (m['Branch'], m['District']) == k])
