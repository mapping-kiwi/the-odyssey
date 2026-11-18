# Login to Bluesky
import os
from dotenv import load_dotenv
from atproto import Client

load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PROJECT_PW")
git rm --cached --ignore-unmatch .env
client = Client()
client.login(username, password)

print("Successfully connected to Bluesky!")

