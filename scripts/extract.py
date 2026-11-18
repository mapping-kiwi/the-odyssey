import json
from connect_bsky import client
from config import TARGET, MAX_LIMIT, REQUEST_DELAY, PARAMS, RAW_JSON_PATH
import time 

posts = []
seen = set()
cursor = None

while len(posts) < TARGET:
    params = PARAMS.copy()

    params["limit"] = min(MAX_LIMIT, TARGET - len(posts))

    if cursor:
        params["cursor"] = cursor

    response = client.app.bsky.feed.search_posts(params)

    for post in response.posts:
        if post.uri not in seen:
            posts.append(post)
            seen.add(post.uri)

    print("Posts collected:", len(posts))

    if not response.cursor or response.cursor == cursor:
        break

    cursor = response.cursor

    time.sleep(REQUEST_DELAY)

    print("Total posts retrieved:", len(posts))
    
data_path = RAW_JSON_PATH

# Export raw posts to JSON
with open(RAW_JSON_PATH, "w", encoding="utf-8") as file:
    json.dump(
        [post.model_dump(mode="json") for post in posts],
        file,
        indent=4,
        ensure_ascii=False
    )

print("JSON exported successfully")