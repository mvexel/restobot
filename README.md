# Resto-Bot

Code for a Mastodon bot that draws attention to stale POIs.

Resto-bot reads its candidates straight from a GeoParquet file produced by
[cosmo](https://github.com/mvexel/cosmo) — no PostgreSQL/PostGIS required. It
picks a random POI that hasn't been edited in over five years, toots a link to
it, and remembers what it posted in a plain text log.

## Data prep

Build the candidate dataset from an OSM PBF extract with cosmo and the
[`pois.yaml`](pois.yaml) filter. This extracts every `amenity=restaurant` POI as
a point (building polygons are reduced to their centroid) into one GeoParquet file:

```bash
cosmo convert \
  --input ~/osm/data/us-latest.osm.pbf \
  --filters pois.yaml \
  --output ./data/pois.parquet \
  --format parquet
```

Re-run this whenever you want fresher data (e.g. download a new extract and
regenerate on a schedule). There is no replication or spatial join step
anymore; the place/state shown in each toot is fetched on demand from OSM
Nominatim when the bot runs.

## Setup

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

Configuration is read from environment variables:

- `DATA_PATH` — the GeoParquet file produced by cosmo; defaults to `./data/pois.parquet`
- `POSTED_FILE` — path to the log of already-posted features; defaults to `./posted.txt`
- `NOMINATIM_USER_AGENT` — identifying string with a contact address; required by [Nominatim's usage policy](https://operations.osmfoundation.org/policies/nominatim/)
- `MASTO_BASE_URL`, `MASTO_ACCESS_TOKEN` — your Mastodon instance and token; required unless `DRY_RUN=1`
- `DRY_RUN` — set to `1`, `true`, or `yes` to print one post without sending it or updating `POSTED_FILE`


## Docker

Configuration is read from a `.env` file in the project root, which compose
auto-loads for the `${VAR}` substitutions in `docker-compose.yml`. Copy the
template and fill it in once — no need to pass settings on the command line:

```bash
cp .env.example .env
$EDITOR .env
```

Build the image:

```bash
docker compose build
```

Seed the data volume from the current Geofabrik United States extract. This downloads
`us-latest.osm.pbf` and converts it to the GeoParquet file used by the bot:

```bash
docker compose --profile seed run --rm seed
```

The seed step is intentionally separate from the bot run because the US PBF is large.
Override the extract URL or force regeneration. Keep each of these on a single
line — the trailing-`\` multi-line form is easy to mangle on paste, which leaves
the variable unset:

```bash
OSM_PBF_URL=https://download.geofabrik.de/north-america/us-latest.osm.pbf docker compose --profile seed run --rm seed

FORCE_SEED=1 docker compose --profile seed run --rm seed
```

`FORCE_SEED=1` is required to rebuild `pois.parquet` after changing `pois.yaml`,
since seeding skips regeneration when the file already exists.

Run the bot. With `DRY_RUN=1` in `.env` this prints one post without sending it
or touching `posted.txt`; blank out `DRY_RUN` and set the Mastodon values for a
real toot. Rebuild first if you've changed `bot.py` since the last image build:

```bash
docker compose build restobot
docker compose run --rm restobot
```

The `restobot-data` Docker volume stores the downloaded PBF, generated parquet data,
and `posted.txt`.

## Running

```bash
DRY_RUN=1 NOMINATIM_USER_AGENT='restobot/1.0 (+https://codeberg.org/mvexel/restobot)' venv/bin/python3 bot.py
```

For a real toot, include the Mastodon settings and omit `DRY_RUN`:

```bash
NOMINATIM_USER_AGENT='restobot/1.0 (+https://codeberg.org/mvexel/restobot)' MASTO_BASE_URL='https://botsin.space' MASTO_ACCESS_TOKEN='...' venv/bin/python3 bot.py
```

Each run selects one stale, not-yet-posted POI, reverse-geocodes its location,
toots about it, and appends its key (e.g. `node/123456`) to `POSTED_FILE`.

Crontab it:

```cron
NOMINATIM_USER_AGENT='restobot/1.0 (+https://example.org/contact)'
MASTO_BASE_URL='https://botsin.space'
MASTO_ACCESS_TOKEN='...'
0 10 * * * cd /home/mvexel/restobot/ && venv/bin/python3 bot.py >> /home/mvexel/restobot.log
```
