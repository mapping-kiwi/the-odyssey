
import pandas as pd

from config import (
    PROCESSED_CSV_PATH,
    RANDOM_SEED,
    TARGET
)

cleaned_path = (
    PROCESSED_CSV_PATH.parent /
    "odyssey_cleaned_posts.csv"
)

df = pd.read_csv(cleaned_path)

# Randomly select 400 candidates for review
review_size = min(400, len(df))

review = df.sample(
    n=review_size,
    random_state=RANDOM_SEED
)

review["relevant"] = ""

review_path = (
    PROCESSED_CSV_PATH.parent /
    "odyssey_review_sample.csv"
)

review.to_csv(review_path, index=False)

print("Posts selected for review:", len(review))
print("Saved to:", review_path)
