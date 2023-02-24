# Resto-Bot

Code for a Mastodon bot that draws attention to stale POIs.

## Database prep and data loading

Create a database `osm` with PostGIS extension.

```bash=
$ createuser -d osm
$ createdb -O osm osm
$ psql -d osm -c 'create extension postgis'
```

Load the initial data and init / perform replication.
(You will want to add a cron job for the `osm2pgsql-replication update` command)

```bash=
$ osm2pgsql --slim -d osm -x -O flex -S ~/dev/restobot/osm2pgsql/poi.lua -c ~/osm/data/us-latest.osm.pbf
$ osm2pgsql-replication init -d osm --osm-file ~/osm/data/us-latest.osm.pbf
$ osm2pgsql-replication update -d osm --  -x -O flex -S ~/dev/restobot/osm2pgsql/poi.lua
```

Next, load [TIGER place and state data](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-geodatabase-file.2022.html). Note that we load one places file then delete the rows from the table. This is so we can create the table schema and then use `find` to load all TIGER place files at once and avoid duplicating data. We only have to do this with the places data because it comes in one file per state. There's perhaps a smarter way to do this!

```bash=
$ shp2pgsql -c -I -D -s 4326 ~/geodata/tiger/states/2022/tl_2022_us_state/tl_2022_us_state.shp tiger_states | psql -d osm
$ shp2pgsql -c -I -D -s 4326 ~/geodata/tiger/places/2022/tl_2022_01_place/tl_2022_01_place.shp tiger_places | psql -d osm
psql -d osm -c 'delete from tiger_places;'
$ find ~/geodata/tiger/places/2022/ -name \*.shp -exec sh -c "shp2pgsql -a -D -s 4326 {} tiger_places | psql -d osm" \;
```

Next, add place and state columns and perform the spatial joins.

```psql=
# alter table pois add column place text;
# update pois set place = tp.name from tiger_places tp where pois.geom @ tp.geom;
# alter table pois add column state text;
# update pois set state = ts.name from tiger_states ts where pois.geom @ ts.geom;
```

Finally add a `posted` column so we can keep track of what's posted:

```psql=
# alter table pois add column posted timestamp;
```

Crontab the replication

```cron=
0 10 * * * cd /home/mvexel/restobot/ && venv/bin/python3 bot.py >> /home/mvexel/restobot.log
```
