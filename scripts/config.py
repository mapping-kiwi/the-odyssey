from pathlib import Path
# Data collection settings

TARGET = 250
MAX_LIMIT = 100
REQUEST_DELAY = 1
RANDOM_SEED = 42

# Odyssey configs
MOVIE = "The Odyssey"
MOVIE_FOLDER = "odyssey"

# Bluesky search parameters for Odyssey
PARAMS = {
    "q": '"The Odyssey"',
    "lang": "en",
    "sort": "latest",
    "since": "2026-07-10T00:00:00Z", # 7 days before release
    "until": "2026-08-08T00:00:00Z" # 21 days after release
}

# Cleaning settings
REMOVE_REPLIES = True
REMOVE_DUPLICATES = True
REQUIRE_MOVIE_RELEVANCE = True

# Regular project directories
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

# Odyssey output paths
OUTPUT_DIR = DATA_DIR / MOVIE_FOLDER

RAW_JSON_PATH = OUTPUT_DIR / "odyssey_raw_posts.json"
PROCESSED_CSV_PATH = OUTPUT_DIR / "odyssey_processed_posts.csv"
FINAL_CSV_PATH = OUTPUT_DIR / "odyssey_final_250.csv"
REVIEWED_CSV_PATH = OUTPUT_DIR / "odyssey_relevance_review.csv"