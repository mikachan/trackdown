#!/usr/bin/env bash
# Rebuild Trackdown's data from the raw downloads.
#
# The raw downloads are manual and not committed. To refresh them:
#   - OpenStreetMap: run the Overpass query for ways tagged roller_coaster=track or
#     attraction=roller_coaster (out tags geom) and save it as data/osm/tracks.json.
#   - Wikipedia: python3 -I scripts/fetch_wikipedia.py data/wikipedia/pages.json
#   - Natural Earth: curl -sSfL -o data/naturalearth/ne_50m_admin_0_countries.geojson \
#       https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -I scripts/build_coasters.py data/osm/tracks.json data/coasters.json
python3 -I scripts/parse_infoboxes.py data/wikipedia/pages.json data/coasters.json data/wikipedia/stats.json
python3 -I scripts/export.py data/wikipedia/stats.json data/coasters.json \
  data/naturalearth/ne_50m_admin_0_countries.geojson app/src/lib/data/coasters.json data/candidates.json
if [ -f data/schedule.json ]; then
  python3 -I scripts/encode_schedule.py data/schedule.json app/src/lib/data/coasters.json app/src/lib/data/schedule.json
fi
