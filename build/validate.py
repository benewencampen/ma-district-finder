#!/usr/bin/env python3
"""Cross-check the tool's point-in-polygon result against the Census Bureau's
own spatial join, over random points across Massachusetts."""
import json, random, subprocess, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor

DATA = json.load(open('ma_legislative_data.json'))

for ch in DATA['chambers'].values():
    for f in ch['features']:
        xs, ys = [], []
        polys = [f['geometry']['coordinates']] if f['geometry']['type'] == 'Polygon' else f['geometry']['coordinates']
        for poly in polys:
            for ring in poly:
                for x, y in ring:
                    xs.append(x); ys.append(y)
        f['bbox'] = (min(xs), min(ys), max(xs), max(ys))

def in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside

def in_poly(x, y, rings):
    if not in_ring(x, y, rings[0]):
        return False
    return not any(in_ring(x, y, r) for r in rings[1:])

def find(chamber, lat, lng):
    for f in DATA['chambers'][chamber]['features']:
        minx, miny, maxx, maxy = f['bbox']
        if not (minx <= lng <= maxx and miny <= lat <= maxy):
            continue
        g = f['geometry']
        polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        if any(in_poly(lng, lat, rings) for rings in polys):
            return f['properties']['district']
    return None

def census(lat, lng):
    url = ('https://geocoding.geo.census.gov/geocoder/geographies/coordinates?'
           + urllib.parse.urlencode({'x': lng, 'y': lat, 'benchmark': 'Public_AR_Current',
                                     'vintage': 'Current_Current', 'layers': 'all', 'format': 'json'}))
    try:
        out = subprocess.run(['curl', '-s', '--max-time', '45', url],
                             capture_output=True, text=True).stdout
        d = json.loads(out)['result']['geographies']
    except Exception as e:
        return ('ERR', str(e)[:40])
    def pick(kind):
        for k, v in d.items():
            if 'State Legislative' in k and kind in k and v:
                return v[0]['NAME'].replace(' District', '')
        return None
    return (pick('Lower'), pick('Upper'))

random.seed(7)
pts = []
while len(pts) < 60:
    lat = random.uniform(41.3, 42.85)
    lng = random.uniform(-73.4, -70.0)
    if find('house', lat, lng):                 # keep points that land on a district
        pts.append((lat, lng))

def check(p):
    lat, lng = p
    mine = (find('house', lat, lng), find('senate', lat, lng))
    theirs = census(lat, lng)
    return (lat, lng, mine, theirs)

with ThreadPoolExecutor(max_workers=6) as ex:
    results = list(ex.map(check, pts))

ok = bad = err = 0
for lat, lng, mine, theirs in results:
    if theirs[0] == 'ERR':
        err += 1; continue
    if mine == theirs:
        ok += 1
    else:
        bad += 1
        print(f'MISMATCH {lat:.5f},{lng:.5f}  mine={mine}  census={theirs}')

print(f'\nagree: {ok}   disagree: {bad}   errors: {err}   (of {len(pts)} points)')
sys.exit(1 if bad else 0)
