# Resto-Bot

Code for a Mastodon bot that draws attention to stale POIs.

## Database prep and data loading

Create a database `osm` with PostGIS extension.

Download an OSM PBF file.

Optionally, filter it with `osmium` to reduce `osm2pgsql` processing time.

`osmium tags-filter -o us-poi.osm.pbf us-latest.osm.pbf nw/amenity,shop,tourism,craft,emergency,historic,leisure,office,sport,public_transport`

Load data:

`osm2pgsql -d osm -x -O flex -S poi.lua -c us-poi.osm.pbf`

Crontab example

0 10 \* \* \* cd /home/mvexel/restobot/ && venv/bin/python3 bot.py >> /home/mvexel/restobot.log
