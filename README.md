# Who Represents This Spot? — Massachusetts

Click anywhere in Massachusetts and see the State Representative and State
Senator for that exact point — not the town, the point. Built for reporting a
specific problem (a pothole, a broken guardrail, a flooded underpass) to the
two people who can actually do something about it on Beacon Hill.

**[Open the tool](https://benewencampen.github.io/ma-district-finder/)**

## What it does

- Click the map, or search an address, or use your current location.
- Shows the sitting State Rep and State Senator for that point: photo, party,
  district, email, phone, State House room, and a link to their profile.
- **Copy link** produces a `?lat=&lng=` URL that reopens that exact spot, so
  you can hand someone the pothole.
- Three base maps (Streets, Satellite, Light) via Esri's free tile services.

It's a single self-contained `index.html` — no backend, no build step to
serve it, no API keys. District boundaries and the legislator roster are
baked in at build time (see `build/`).

## Data & accuracy

- **Boundaries**: U.S. Census Bureau TIGERweb, 2026 State Legislative
  Districts (the maps in effect since 2021 redistricting), simplified to
  roughly 2 m.
- **Legislators**: the current General Court roster, cross-referenced between
  [Open States](https://openstates.org) (who holds each seat right now) and
  [malegislature.gov](https://malegislature.gov) (authoritative contact
  details, photo, profile link).
- The point-in-polygon lookup was cross-checked against the Census Bureau's
  own spatial join on 60 random points statewide: 60/60 agreement on both
  chambers (`build/validate.py`).
- Not an official state service. If a click lands right on a district line,
  confirm at [malegislature.gov/Search/FindMyLegislator](https://malegislature.gov/Search/FindMyLegislator).

## Rebuilding after an election

Legislator data goes stale after a special election or a new General Court.
See [`build/README.md`](build/README.md) for the rebuild pipeline
(`build/rebuild.sh`), which re-fetches everything and regenerates
`index.html`.

## Hosting

This repo is set up to serve `index.html` directly from GitHub Pages. Any
static host works, too — it's one file.
