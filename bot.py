#!/usr/bin/env python3

import random
from datetime import date, timedelta

import pyarrow.compute as pc
import pyarrow.dataset as ds
import requests
from mastodon import Mastodon
from shapely import wkb

import private

# A POI is "stale" once it hasn't been touched in this many days.
STALE_DAYS = 365 * 5


def compose_message(days, name, place, osm_link):
    """Defines what the bot will say"""
    location = f" {place}" if place else ""
    return f"""Resto-bot 🤖 here! It's been {days} days since {name or "an unnamed restaurant"}{location} has been updated on OSM.

If you could do some research and check if this restaurant still exists, that would make RestoBot very happy! Here's the OSM link: {osm_link}. 💡 Help is here: https://git.sr.ht/~mvexel/restobot/tree/main/item/INSTRUCTIONS.md

#OpenStreetMap loves you back! ❤️🙏
"""


def compose_place(state, place):
    """Smartly composes a good place string from a state and/or place name"""
    if place and state:
        return f"in {place}, {state}"
    if place:
        return f"in {place}"
    if state:
        return f"in {state}"
    return None


def compose_link(osm_type, osm_id):
    """Composes a link to an OSM feature from an OSM id and an OSM type (N or W)"""
    if osm_type == "N":
        return f"https://osm.org/node/{osm_id}"
    if osm_type == "W":
        return f"https://osm.org/way/{osm_id}"


def load_posted(path):
    """Reads the set of already-posted feature keys (e.g. 'N123', 'W456')"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        return set()


def mark_posted(path, key):
    """Appends a feature key to the posted log so we never repeat it"""
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{key}\n")


def reverse_geocode(lat, lon):
    """Looks up (state, place) for a coordinate via OSM Nominatim"""
    resp = requests.get(
        "https://nominatim.openstreetmap.org/reverse",
        params={"lat": lat, "lon": lon, "format": "jsonv2", "zoom": 14},
        headers={"User-Agent": private.nominatim_user_agent},
        timeout=30,
    )
    resp.raise_for_status()
    address = resp.json().get("address", {})
    place = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
    )
    return address.get("state"), place


def pick_record():
    """Picks a random stale POI that hasn't been posted yet, or None"""
    posted = load_posted(private.posted_file)
    cutoff = (date.today() - timedelta(days=STALE_DAYS)).isoformat()

    # timestamps are RFC3339 strings (e.g. 2018-03-01T12:00:00Z); ISO-8601
    # ordering matches chronological ordering, so a string compare is correct
    # and lets pyarrow push the filter down into the parquet scan.
    dataset = ds.dataset(private.data_dir, format="parquet")
    table = dataset.to_table(
        columns=["osm_type", "osm_id", "name", "timestamp", "geometry"],
        filter=pc.field("timestamp") < cutoff,
    )

    candidates = [
        row
        for row in table.to_pylist()
        if f"{row['osm_type']}{row['osm_id']}" not in posted
    ]
    return random.choice(candidates) if candidates else None


def main():
    record = pick_record()
    if record is None:
        print("No stale, unposted POIs left to toot about.")
        return

    key = f"{record['osm_type']}{record['osm_id']}"
    point = wkb.loads(record["geometry"])
    state, place = reverse_geocode(point.y, point.x)
    days = (date.today() - date.fromisoformat(record["timestamp"][:10])).days

    msg = compose_message(
        days=days,
        name=record["name"],
        place=compose_place(state=state, place=place),
        osm_link=compose_link(record["osm_type"], record["osm_id"]),
    )

    print(msg)

    client = Mastodon(
        api_base_url=private.masto_base_url,
        access_token=private.masto_access_token,
    )
    client.toot(msg)

    mark_posted(private.posted_file, key)


if __name__ == "__main__":
    main()
