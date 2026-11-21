
import pandas as pd

from config import (
    PROCESSED_CSV_PATH,
    PARAMS
)

# Load processed data
df = pd.read_csv(PROCESSED_CSV_PATH)

print("Initial posts:", len(df))

# 1. Remove duplicates
df = df.drop_duplicates(subset="uri")
print("After duplicates:", len(df))

# 2. Remove replies
df = df[
    df["record.reply"].astype(str).str.lower() == "false"
].copy()
print("After removing replies:", len(df))

# 3. Keep English posts
df = df[
    df["record.langs"].fillna("").str.split(",")
      .apply(lambda langs: "en" in langs)
].copy()
print("After language filtering:", len(df))

# 4. Filter dates
dates = pd.to_datetime(
    df["record.created_at"],
    utc=True,
    errors="coerce"
)

start = pd.Timestamp(PARAMS["since"])
end = pd.Timestamp(PARAMS["until"])

df = df[
    (dates >= start) &
    (dates < end)
].copy()

print("After date filtering:", len(df))

# 5. Remove empty post text
df = df.dropna(subset=["record.text"])
df = df[df["record.text"].str.strip() != ""].copy()

print("After removing empty posts:", len(df))

# 6. Save cleaned candidates for relevance review
output_path = PROCESSED_CSV_PATH.parent / "odyssey_cleaned_posts.csv"

df["relevant"] = ""

df.to_csv(output_path, index=False)

print("Cleaned candidates:", len(df))
print("Saved to:", output_path)
