# Resto-Bot

Code for a Mastodon bot that draws attention to stale POIs.

## Database

This is the table schema:

```
CREATE TABLE public.restodon (
    osm_type character(1),
    osm_id bigint,
    name text,
    class text,
    subclass text,
    geom public.geometry(Point,4326),
    version smallint,
    age real,
    place text,
    state text,
    posted date
);
```
