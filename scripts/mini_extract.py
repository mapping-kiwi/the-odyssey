from connect_bsky import client 

# Search for lastest 10 posts
response = client.app.bsky.feed.search_posts({
    "q": '"The Odyssey"',
    "limit": 10,
    "lang": "en",
    "sort": "latest"
})

# Display
for post in response.posts:
    print(post.record.text)

print("Total posts:", len(response.posts))