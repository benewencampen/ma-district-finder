#!/bin/bash
# Full rebuild: fresh data -> ../index.html
set -euo pipefail
cd "$(dirname "$0")"

./fetch_sources.sh
python3 fetch_members.py
python3 build_data.py
python3 build_html.py

echo
echo "Spot-check the lookup against the Census Bureau's own spatial join:"
echo "  python3 validate.py"
