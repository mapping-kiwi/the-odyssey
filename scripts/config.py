from pathlib import Path
# Data collection settings

TARGET = 250
MAX_LIMIT = 100
REQUEST_DELAY = 1

# Bluesky search parameters for Odyssey
PARAMS = {
    "q": '"The Odyssey"',
    "lang": "en",
    "sort": "latest",
    "since": "2026-06-01T00:00:00Z",
    "until": "2026-09-01T00:00:00Z"
}

# Regular project directories
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

# Odyssey configs
MOVIE = "The Odyssey"
MOVIE_FOLDER = "odyssey"

OUTPUT_DIR = DATA_DIR / MOVIE_FOLDER
RAW_JSON_PATH = OUTPUT_DIR / "odyssey_raw_posts.json"