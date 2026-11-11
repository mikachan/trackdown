# Trackdown

[![Spacefast](https://img.shields.io/github/deployments/mikachan/trackdown/production?label=Spacefast)](https://github.com/mikachan/trackdown/deployments)

A daily guessing game for roller coaster fans. Each day there's a new coaster to find from its track, seen from above. Every wrong guess unlocks a clue: when it opened, its height, its top speed, who built it, and where it is. There's also an endless Higher or Lower game comparing coaster stats.

Trackdown is part of [sekai.co.uk](https://sekai.co.uk).

## How it works

Trackdown is a static site. A small Python pipeline turns open data into JSON files, and a SvelteKit app uses them to run both games in the browser. There's no server and no database. Players' streaks and scores are kept in their own browser.

- **Track outlines** come from OpenStreetMap: coaster tracks tagged `roller_coaster=track` or `attraction=roller_coaster`.
- **Stats** (height, speed, length, inversions, opening year, manufacturer, park) come from Wikipedia's coaster infoboxes.
- **Countries** come from the coaster's coordinates, using Natural Earth's country boundaries.

The puzzles are picked from a shortlist and kept in order in a schedule. The schedule in the repo is lightly scrambled so browsing the code doesn't spoil upcoming answers.

## Project layout

```
app/        SvelteKit app (the site)
  src/lib/          game logic, with tests next to each file
  src/lib/data/     generated data: coasters.json and the scrambled schedule.json
  src/routes/       pages: daily puzzle, Higher or Lower, about, 404
scripts/    Python data pipeline, with tests (test_*.py)
data/       pipeline inputs and outputs (raw downloads aren't committed)
sf.jsonc    Spacefast build settings
```

## Working on the app

You'll need Node 22 or newer.

```sh
cd app
npm install
npm run dev       # local dev server
npm test          # unit tests (Vitest)
npm run check     # type check
npm run build     # static build in app/build
npm run preview   # serve the build locally
```

## Updating the data

The pipeline needs Python 3.11 or newer and nothing outside the standard library.

1. Download the raw data. These files aren't committed; how to get each one is described at the top of `scripts/pipeline.sh`.
   - OpenStreetMap tracks → `data/osm/tracks.json` (from an Overpass query)
   - Wikipedia infoboxes → `data/wikipedia/pages.json` (`scripts/fetch_wikipedia.py`)
   - Natural Earth countries → `data/naturalearth/ne_50m_admin_0_countries.geojson`
2. Rebuild everything:

   ```sh
   bash scripts/pipeline.sh
   ```

   This writes `app/src/lib/data/coasters.json` and a puzzle shortlist in `data/candidates.json`.
3. Run the pipeline tests:

   ```sh
   python3 -m unittest discover -s scripts -p 'test_*.py'
   ```

### Choosing puzzles

```sh
python3 -I scripts/review.py data/candidates.json review/review.html
open review/review.html
```

Approve and order coasters on the review page, then export `schedule.json` into `data/`. The next `bash scripts/pipeline.sh` scrambles it into `app/src/lib/data/schedule.json`. The plain `data/schedule.json` isn't committed.

## Deploying

The site is hosted on [Spacefast](https://spacefast.com). Pushes to `main` build and deploy through the Spacefast GitHub App, using the settings in `sf.jsonc`: it builds `app/` and publishes `app/build`.

## Credits and licences

- Track data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), available under the [Open Database Licence](https://opendatacommons.org/licenses/odbl/). The derived track data in this repo (`app/src/lib/data/coasters.json`) is available under the same licence.
- Coaster stats from [Wikipedia](https://en.wikipedia.org/), available under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- Country boundaries from [Natural Earth](https://www.naturalearthdata.com/) (public domain).

## Licence

Trackdown is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 2 of the License, or (at your option) any later version. See [`LICENSE`](LICENSE).

The data has its own licences, listed under [Credits and licences](#credits-and-licences).
