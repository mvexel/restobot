#!/usr/local/bin python3

import psycopg2
import private
from mastodon import Mastodon


def compose_place(state, place):
    if place is None:
        return f"in {state}"
    if state is None:
        return None
    return f"in {place}, {state}"


def compose_link(osm_type, osm_id):
    if osm_type == "N":
        return f"https://osm.org/node/{osm_id}"
    if osm_type == "W":
        return f"https://osm.org/way/{osm_id}"


dsn = f"postgresql://{private.pg_user}:{private.pg_pass}@{private.pg_host}:{private.pg_port}"
conn = psycopg2.connect(
    f"dbname={private.pg_db} host = {private.pg_host} port={private.pg_port} user={private.pg_user} password={private.pg_pass}"
)
cur = conn.cursor()

client = Mastodon(
    api_base_url="https://botsin.space", access_token=private.masto_access_token
)

cur.execute(
    f"SELECT osm_id, name, st_astext(geom), age, state, place, osm_type FROM {private.pg_table} WHERE posted IS NULL ORDER BY RANDOM() LIMIT 1;",
)
result = cur.fetchone()
message = f"""
Resto-bot 🤖 here! It's been {int(result[3])} days since {result[1] or "an unnamed restaurant"} {compose_place(result[4], result[5])} has been updated on OSM. 

If you could do some research and check if this restaurant still exists, that would make RestoBot very happy! Here's the OSM link: {compose_link(result[6], result[0])}

#OpenStreetMap loves you back! ❤️🙏
"""

print(message)
client.toot(message)

cur.execute(
    f"UPDATE {private.pg_table} SET posted = current_timestamp WHERE osm_id = {result[0]}"
)
conn.commit()
conn.close()
