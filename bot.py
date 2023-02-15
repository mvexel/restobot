#!/usr/bin/env python3

import psycopg2
import private
from mastodon import Mastodon


def compose_message(days, name, place, osm_link):
    """Defines what the bot will say"""
    return f"""Resto-bot 🤖 here! It's been {days} days since {name or "an unnamed restaurant"} {place} has been updated on OSM. 

If you could do some research and check if this restaurant still exists, that would make RestoBot very happy! Here's the OSM link: {osm_link}. 💡 Help is here: https://git.sr.ht/~mvexel/restobot/tree/main/item/INSTRUCTIONS.md

#OpenStreetMap loves you back! ❤️🙏
"""


def compose_place(state, place):
    """Smartly composes a good place string based on a state name and an optional place name"""
    if place is None:
        return f"in {state}"
    if state is None:
        return None
    return f"in {place}, {state}"


def compose_link(osm_type, osm_id):
    """Composes a link to an OSM feature from an OSM id and an OSM type (N or W)"""
    if osm_type == "N":
        return f"https://osm.org/node/{osm_id}"
    if osm_type == "W":
        return f"https://osm.org/way/{osm_id}"


# Database connection
dsn = f"postgresql://{private.pg_user}:{private.pg_pass}@{private.pg_host}:{private.pg_port}/{private.pg_db}"
conn = psycopg2.connect(dsn)
cur = conn.cursor()

# Mastodon client
client = Mastodon(
    api_base_url=private.masto_base_url, access_token=private.masto_access_token
)

# Get a random record
cur.execute(
    f"SELECT osm_type, osm_id, name, age, state, place FROM {private.pg_table} WHERE posted IS NULL ORDER BY RANDOM() LIMIT 1;",
)
result = cur.fetchone()

# Compose the message
msg = compose_message(
    days=result[3],
    name=result[2],
    place=compose_place(state=result[4], place=result[5]),
    osm_link=compose_link(osm_type=result[0], osm_id=result[1]),
)

print(msg)
# client.toot(msg)

cur.execute(
    f"UPDATE {private.pg_table} SET posted = current_timestamp WHERE osm_id = {result[1]}"
)
conn.commit()
conn.close()
