"""Count English title-search results over the same UTC release window for three films."""
import argparse
import csv
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from atproto import Client
from dotenv import load_dotenv

FILMS = [
    ("The Odyssey", "2026-07-17"),
    ("Spider-Man: Brand New Day", "2026-07-31"),
    ("Toy Story 5", "2026-06-19"),
]


def stamp(value):
    return value.isoformat().replace("+00:00", "Z")


def search_day(client, title, start):
    stop = start + timedelta(days=1)
    params = {"q": f'"{title}"', "lang": "en", "sort": "latest", "limit": 100,
              "since": stamp(start), "until": stamp(stop)}
    seen_cursors = set()
    posts = {}
    while True:
        page = client.app.bsky.feed.search_posts(params)
        for post in page.posts:
            created = datetime.fromisoformat(str(post.record.created_at).replace("Z", "+00:00"))
            if start <= created < stop:
                posts[post.uri] = post.record.reply is None
        cursor = page.cursor
        if not cursor:
            status = "full_last_page_no_cursor" if len(page.posts) == params["limit"] else "pagination_ended"
            return len(posts), sum(posts.values()), status
        if cursor in seen_cursors:
            return len(posts), sum(posts.values()), "repeated_cursor"
        seen_cursors.add(cursor)
        params["cursor"] = cursor
        time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="New CSV file for this independent collection")
    args = parser.parse_args()
    load_dotenv()
    username = os.getenv("BSKY_HANDLE") or os.getenv("USERNAME")
    password = os.getenv("BSKY_APP_PASSWORD") or os.getenv("PROJECT_PW")
    if not username or not password:
        parser.error("Set BSKY_HANDLE and BSKY_APP_PASSWORD in your environment")
    if args.output.exists():
        parser.error("Choose a new output file")
    client = Client()
    client.login(username, password)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["film", "query", "utc_date", "day_from_release", "retrieved_matches",
                         "retrieved_top_level", "pagination_status", "retrieved_at_utc"])
        for film, release in FILMS:
            release_day = datetime.fromisoformat(release).replace(tzinfo=timezone.utc)
            for offset in range(-7, 22):
                day = release_day + timedelta(days=offset)
                count, top, status = search_day(client, film, day)
                writer.writerow([film, f'"{film}"', day.date(), offset, count, top, status,
                                 stamp(datetime.now(timezone.utc))])
                file.flush()
                time.sleep(0.5)


if __name__ == "__main__":
    main()
