#!/bin/bash
# Download the two raw inputs: district boundaries and the legislator roster.
set -euo pipefail
cd "$(dirname "$0")"

TIGER="https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Legislative/MapServer"

# Layer 1 = State Senate (upper), layer 2 = State House (lower).
# maxAllowableOffset generalises server-side: 0.00002 degrees is roughly 2 m,
# which keeps the whole state near 2.3 MB without moving district lines
# enough to change an answer.
for LAYER in 1 2; do
  echo "downloading boundary layer $LAYER ..."
  curl -sfG "$TIGER/$LAYER/query" \
    --data-urlencode "where=GEOID LIKE '25%'" \
    --data-urlencode "outFields=NAME,GEOID,BASENAME" \
    --data-urlencode "returnGeometry=true" \
    --data-urlencode "outSR=4326" \
    --data-urlencode "maxAllowableOffset=0.00002" \
    --data-urlencode "geometryPrecision=6" \
    --data-urlencode "f=geojson" \
    --max-time 300 -o "fine_${LAYER}.geojson"
done

echo "downloading Open States roster ..."
curl -sf "https://data.openstates.org/people/current/ma.csv" --max-time 60 -o ma_people.csv

echo "downloading General Court member index ..."
curl -sf "https://malegislature.gov/api/GeneralCourts/194/LegislativeMembers" \
  --max-time 60 -o mem194.json

echo "done. next: python3 fetch_members.py && python3 build_data.py && python3 build_html.py"
