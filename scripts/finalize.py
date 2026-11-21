import pandas as pd
from config import FINAL_CSV_PATH, RANDOM_SEED, TARGET

review = pd.read_csv(
    FINAL_CSV_PATH.parent / "odyssey_review_sample.csv"
)

relevant = review[review["relevant"] == 1]

if len(relevant) < TARGET:
    raise ValueError(
        f"Only {len(relevant)} relevant posts. "
        "Review more candidates before sampling."
    )

final = relevant.sample(
    n=TARGET,
    random_state=RANDOM_SEED
)

final = final.drop(columns=["relevant"])
final.to_csv(FINAL_CSV_PATH, index=False)

print("Final sample:", len(final))