# Data
# Directory holding the cosmo parquet output (nodes.parquet + ways.parquet)
data_dir = "./data"
# File used to remember which POIs have already been posted (created on first run)
posted_file = "./posted.txt"
# Nominatim requires a User-Agent identifying the app, with a contact URL.
# Do not use a bare email or "example.com" here: Nominatim blocks those.
nominatim_user_agent = "restobot/1.0 (+https://git.sr.ht/~mvexel/restobot)"
# Mastodon
masto_base_url = ""
masto_access_token = ""
