# syntax=docker/dockerfile:1

FROM rust:1.88-bookworm AS cosmo-builder
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates git pkg-config cmake clang sqlite3 libsqlite3-dev libssl-dev libproj-dev \
    && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/mvexel/cosmo.git /src/cosmo \
    && git -C /src/cosmo checkout 4e290b6ac8d227270d01bf2e17d3a958a5a06b41  # cosmo 0.2.0
WORKDIR /src/cosmo
RUN cargo install --path . --locked --root /opt/cosmo

FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_PATH=/data/pois.parquet \
    POSTED_FILE=/data/posted.txt \
    OSM_PBF_PATH=/data/input.osm.pbf \
    OSM_PBF_URL=https://download.geofabrik.de/north-america/us-latest.osm.pbf

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl libmagic1 libproj25 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=cosmo-builder /opt/cosmo/bin/cosmo /usr/local/bin/cosmo

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py pois.yaml seed_osm.sh ./

VOLUME ["/data"]
CMD ["python", "bot.py"]
