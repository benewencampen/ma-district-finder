# Build pipeline

Produces `../index.html`, the single self-contained page served by GitHub
Pages: click a point in Massachusetts, get the State Representative and
State Senator for that point.

## Rebuild

```sh
cd build
chmod +x rebuild.sh fetch_sources.sh   # first time only
./rebuild.sh
```

Takes a few minutes, almost all of it downloading the 204 member records.
Re-run after any special election, and after each biennial General Court turnover
(bump `194` to the new court number in `fetch_sources.sh` and `fetch_members.py`).
Commit the regenerated `../index.html`.

## What comes from where

| Input | Source | Why |
|---|---|---|
| District polygons | Census TIGERweb, *2026 State Legislative Districts* | The only free, queryable copy of the post-2021 maps. Generalised server-side to ~2 m. |
| Who holds each seat | Open States `current/ma.csv` | The only source that distinguishes the **current** holder from a predecessor who sat earlier in the same General Court. |
| Contact details, photo, profile URL | `malegislature.gov` member API | Authoritative. Open States' phone coverage is thin. |
| Map tiles | Esri ArcGIS Online (free, keyless) | `tile.openstreetmap.org`'s own usage policy reserves it for light testing, not a public app; CARTO's anonymous tile endpoints now require an API key. |

The two rosters are joined on chamber + district, then on name. Name matching folds
accents (`Judith García` / `Judith A. Garcia`) and drops middle initials and suffixes.
District names are normalised because the sources punctuate multi-county districts
differently (`Berkshire, Hampden, Franklin and Hampshire` vs `Berkshire-Hampden-Franklin-Hampshire`).

`build_data.py` prints a vacancy list and a per-field coverage count. A seat with no
current holder renders as a "seat is vacant" card rather than disappearing.

## Files

- `fetch_sources.sh` — boundaries, Open States CSV, member index
- `fetch_members.py` — per-member contact details (truncates each ~1.6 MB response, since
  the fields we want precede the embedded bill list)
- `build_data.py` — joins everything into `ma_legislative_data.json`
- `build_html.py` — inlines that JSON into `template.html`, writes `../index.html`
- `template.html` — the page itself; edit this, not the built output
- `validate.py` — cross-checks 60 random points against the Census Bureau's own
  spatial join. Last run: 60/60 agreement on both chambers.

The raw/intermediate files these scripts fetch (`*.geojson`, `ma_people.csv`,
`mem194.json`, `members_detail.json`, `ma_legislative_data.json`) are gitignored —
they're regenerable and would just be a second, staler copy of what's baked
into `index.html`.

## Notes

- No API keys anywhere. Map tiles are Esri; geocoding is Census (JSONP, since it
  sends no CORS headers) with Nominatim as fallback for place names.
- Point-in-polygon is ray casting with a bounding-box prefilter, holes handled.
- Deep links: `?lat=&lng=` reproduces a location, which is what the "Copy link" button emits.
