#!/bin/sh
set -eu

: "${OSM_PBF_URL:=https://download.geofabrik.de/north-america/us-latest.osm.pbf}"
: "${OSM_PBF_PATH:=/data/input.osm.pbf}"
: "${DATA_PATH:=${DATA_DIR:-/data/pois.parquet}}"

mkdir -p "$(dirname "$OSM_PBF_PATH")" "$(dirname "$DATA_PATH")"

if [ ! -s "$OSM_PBF_PATH" ]; then
    echo "Downloading $OSM_PBF_URL to $OSM_PBF_PATH"
    curl -fL --retry 3 --retry-delay 10 -o "$OSM_PBF_PATH" "$OSM_PBF_URL"
else
    echo "Using existing $OSM_PBF_PATH"
fi

if [ "${FORCE_SEED:-0}" = "1" ]; then
    rm -rf "$DATA_PATH"
fi

if [ ! -s "$DATA_PATH" ]; then
    echo "Building GeoParquet candidate data in $DATA_PATH"
    cosmo convert \
        --input "$OSM_PBF_PATH" \
        --filters /app/pois.yaml \
        --output "$DATA_PATH" \
        --format parquet
else
    echo "Using existing GeoParquet data in $DATA_PATH"
fi
