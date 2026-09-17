#!/usr/bin/env python3
"""Join MA legislative district boundaries to the sitting legislator for each seat.

Who holds a seat comes from Open States (actively maintained, and the only
source that distinguishes the current holder from a predecessor who sat earlier
in the same General Court).  Contact details, the photo code and the profile URL
come from malegislature.gov, which is authoritative for them -- Open States has
stale photo codes for some members.
"""
import csv, json, re, datetime, unicodedata
from collections import defaultdict

def norm_district(s):
    """'Berkshire, Hampden, Franklin and Hampshire' == 'Berkshire-Hampden-Franklin-Hampshire'"""
    s = s.lower().replace('-', ' ').replace(',', ' ')
    s = re.sub(r'\band\b', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

SUFFIXES = {'jr', 'sr', 'ii', 'iii', 'iv'}

def name_key(s):
    """'Jay D. Livingstone' -> ('jay', 'livingstone'); drops initials and suffixes.

    Accents are folded first: the two sources disagree on them (Open States has
    'Judith García', malegislature.gov has 'Judith A. Garcia').
    """
    s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
    parts = [re.sub(r'[^a-z]', '', p.lower()) for p in s.replace('.', ' ').split()]
    parts = [p for p in parts if len(p) > 1 and p not in SUFFIXES]
    return (parts[0], parts[-1]) if len(parts) >= 2 else (parts[0] if parts else '', '')

# --- malegislature.gov: contact details, indexed by branch + district ---------
ml = defaultdict(list)
for m in json.load(open('members_detail.json')):
    branch = 'lower' if m['Branch'] == 'House' else 'upper'
    ml[(branch, norm_district(m['District'] or ''))].append(m)

# --- Open States: who currently holds each seat ------------------------------
people, unmatched = {}, []
for r in csv.DictReader(open('ma_people.csv')):
    chamber, district = r['current_chamber'], norm_district(r['current_district'])
    key = name_key(r['name'])
    hit = next((m for m in ml[(chamber, district)] if name_key(m['Name']) == key), None)
    if hit is None:  # fall back to surname alone, then give up on details
        hit = next((m for m in ml[(chamber, district)] if name_key(m['Name'])[1] == key[1]), None)
    if hit is None:
        unmatched.append((r['name'], r['current_district']))

    code = hit['MemberCode'] if hit else None
    people[(chamber, district)] = {
        'name': hit['Name'] if hit else r['name'],
        'party': (hit['Party'] if hit else r['current_party']) or '',
        'email': (hit['EmailAddress'] if hit else '') or r['email'],
        'phone': (hit['PhoneNumber'] if hit else '') or r['capitol_voice'],
        'room': (hit['RoomNumber'] if hit else '') or '',
        'role': (hit['LeadershipPosition'] if hit else '') or '',
        'image': f'https://malegislature.gov/Legislators/Profile/170/{code}.jpg' if code else '',
        'url': f'https://malegislature.gov/Legislators/Profile/{code}' if code else '',
    }

print(f'roster: {len(people)} seats, {len(unmatched)} without malegislature details')
for n, d in unmatched:
    print('   no detail match:', n, '|', d)

# --- attach to boundaries ----------------------------------------------------
out = {'generated': datetime.date.today().isoformat(), 'court': 194, 'chambers': {}}
for layer, chamber, key in [('1', 'upper', 'senate'), ('2', 'lower', 'house')]:
    feats, vacant = [], []
    for f in json.load(open(f'fine_{layer}.geojson'))['features']:
        name = f['properties']['BASENAME']
        if 'not defined' in name.lower():
            continue                       # TIGER's unassigned-water placeholder
        leg = people.get((chamber, norm_district(name)))
        if leg is None:
            vacant.append(name)
        feats.append({'type': 'Feature',
                      'properties': {'district': name, 'legislator': leg},
                      'geometry': f['geometry']})
    out['chambers'][key] = {'type': 'FeatureCollection', 'features': feats}
    print(f'{key:7s} {len(feats):3d} districts, {len(vacant)} vacant {vacant or ""}')

json.dump(out, open('ma_legislative_data.json', 'w'), separators=(',', ':'))
print('bundle:', round(len(open('ma_legislative_data.json').read()) / 1e6, 2), 'MB')

filled = sum(1 for p in people.values() if p['phone'])
print(f'phone numbers: {filled}/{len(people)};',
      f"photos: {sum(1 for p in people.values() if p['image'])}/{len(people)}")
