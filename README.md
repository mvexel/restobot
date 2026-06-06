# Resto-Bot

Code for a Mastodon bot that draws attention to stale POIs.

Resto-bot reads its candidates straight from a GeoParquet file produced by
[cosmo](https://github.com/mvexel/cosmo) — no PostgreSQL/PostGIS required. It
picks a random POI that hasn't been edited in over five years, toots a link to
it, and remembers what it posted in a plain text log.

## Data prep

Build the candidate dataset from an OSM PBF extract with cosmo and the
[`pois.yaml`](pois.yaml) filter. This extracts every `amenity`/`shop` POI as a
point (building polygons are reduced to their centroid) into a directory holding
`nodes.parquet` and `ways.parquet`:

```bash
cosmo convert \
  --input ~/osm/data/us-latest.osm.pbf \
  --filters pois.yaml \
  --output ./data \
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
cp private_example.py private.py   # then fill in your settings
```

`private.py` settings:

- `data_dir` — the cosmo output directory (contains `nodes.parquet` / `ways.parquet`)
- `posted_file` — path to the log of already-posted features (created on first run)
- `nominatim_user_agent` — identifying string with a contact address (required by [Nominatim's usage policy](https://operations.osmfoundation.org/policies/nominatim/))
- `masto_base_url`, `masto_access_token` — your Mastodon instance and token

## Running

```bash
venv/bin/python3 bot.py
```

Each run selects one stale, not-yet-posted POI, reverse-geocodes its location,
toots about it, and appends its key (e.g. `N123456`) to `posted_file`.

Crontab it:

```cron
0 10 * * * cd /home/mvexel/restobot/ && venv/bin/python3 bot.py >> /home/mvexel/restobot.log
```
