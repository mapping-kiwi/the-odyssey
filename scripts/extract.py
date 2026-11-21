import json
from connect_bsky import client
import time 
from datetime import datetime, timedelta
from config import (
    TARGET, MAX_LIMIT, 
    REQUEST_DELAY, 
    PARAMS, 
    RAW_JSON_PATH
)

posts = []
seen = set()

start = datetime.fromisoformat(
    PARAMS["since"].replace("Z", "+00:00")
)

end = datetime.fromisoformat(
    PARAMS["until"].replace("Z", "+00:00")
)

current = start

while current < end:
    next_day = min(current + timedelta(days=1), end)

    params = PARAMS.copy()
    params["since"] = current.isoformat()
    params["until"] = next_day.isoformat()
    params["limit"] = MAX_LIMIT

    try:
        response = client.app.bsky.feed.search_posts(params)

        print(
            current.date(),
            "-",
            len(response.posts),
            "posts returned"
        )

        if len(response.posts) == MAX_LIMIT:
            print("Warning: daily results may be truncated")

        for post in response.posts:
            if post.uri not in seen:
                posts.append(post)
                seen.add(post.uri)

    except Exception as error:
        print("Request failed:", current.date(), error)
        raise

    current = next_day
    time.sleep(REQUEST_DELAY)

# Save candidate posts
RAW_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(RAW_JSON_PATH, "w", encoding="utf-8") as file:
    json.dump(
        [post.model_dump(mode="json") for post in posts],
        file,
        indent=4,
        ensure_ascii=False
    )

print("Total unique candidates:", len(posts))
print("Saved to:", RAW_JSON_PATH)