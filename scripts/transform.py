
import json
import pandas as pd

from config import (
    MOVIE,
    RAW_JSON_PATH,
    PROCESSED_CSV_PATH
)

# Load raw JSON
with open(RAW_JSON_PATH, "r", encoding="utf-8") as file:
    posts = json.load(file)

rows = []

# Extract relevant fields
for post in posts:

    record = post.get("record") or {}
    author = post.get("author") or {}
    embed = post.get("embed") or {}
    external = embed.get("external") or {}

    rows.append({
        "movie": MOVIE,
        "uri": post.get("uri"),
        "author.did": author.get("did"),
        "record.text": record.get("text"),
        "coding": "",
        "record.created_at": record.get("created_at"),
        "record.langs": ",".join(record.get("langs") or []),
        "record.reply": record.get("reply") is not None,
        "record.tags": ",".join(record.get("tags") or []),
        "embed.external.title": external.get("title"),
        "embed.external.description": external.get("description"),
        "embed.external.uri": external.get("uri"),
        "like_count": post.get("like_count", 0),
        "reply_count": post.get("reply_count", 0),
        "repost_count": post.get("repost_count", 0),
        "quote_count": post.get("quote_count", 0)
    })

# Convert to DataFrame
df = pd.DataFrame(rows)

# Save to CSV
PROCESSED_CSV_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(PROCESSED_CSV_PATH, index=False)

print("Raw posts:", len(posts))
print("CSV rows:", len(df))
print("Saved to:", PROCESSED_CSV_PATH)
