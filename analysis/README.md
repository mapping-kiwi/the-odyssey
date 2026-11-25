# COMP 370 movie discussion analysis

Run these commands from the repository root using Python 3.11 or later. Put the private analysis workbook in `analysis/private/`. The input is `COMP370_Private_Analysis.xlsx`, which contains the corrected labels and restored post text. The original collection exports do not contain these analysis fields.

```sh
python -m pip install -r analysis/requirements.txt
python analysis/analyze.py analysis/private/COMP370_Private_Analysis.xlsx
```

The default destination is `analysis/private/results/`. Use `--out` to select a new directory for a later run. Generated examples contain post text. Keep inputs, credentials and generated outputs private.

## What is reproduced

- Validate unique post identifiers, recognized films and topics, post bodies and nonnegative integer engagement counts. The private workbook preserves the row-level annotation and encoding audit.
- Count each topic within each film, divide by that film's sample size, and compute the distribution over the combined annotated sample. Save the counts, percentages and a figure.
- Calculate mean, median, sum and maximum likes, replies, reposts and quotes in each topic, including posts with zero engagement.
- Fit one TF-IDF vocabulary over post bodies and nonduplicated link titles after removing links, handles, full title phrases and English stop words. Use unigrams of at least two letters, minimum document frequency two, smoothed IDF and L2 normalization. Average over every post in a topic, including zero vectors, and rank the ten highest-scoring words.
- Recreate the summary input selection by sorting post URIs by SHA-256 and taking up to four per film and topic. Export the archived topic summaries and verify that the selected examples match the texts stored in the workbook.
- Read the 29 daily rows per film, retain observed-only counts for capped collection days and calculate relative shares only among films with a full comparator series. Save the daily table, aggregate totals and comparison figure.

The script compares all topic counts and within-film shares, engagement statistics, 80 ranked words and scores, and summary inputs to the saved workbook before publishing the results directory. A mismatch raises an error. If human labels change, build and review a new reference workbook before claiming reproduction of that version.

## Independent coverage collection

The historic Odyssey search requested at most 100 latest results each day. To collect a new, consistently queried series for all three films, install the repo's Bluesky client and supply a Bluesky handle and app password using the environment variables below. The script also supports the existing project credentials configuration.

```sh
python -m pip install atproto python-dotenv
# Set BSKY_HANDLE and BSKY_APP_PASSWORD locally.
python analysis/collect_coverage.py analysis/private/fresh_coverage.csv
```

Each film uses the same quoted full-title template, English search filter, and a UTC window covering days -7 through +21. The collector follows cursors and records distinct returned post URIs with creation times in each day. Only aggregate counts are written. A repeated cursor or a full terminal page is flagged. If a request fails, the command exits and the finished rows remain available for inspection. Check that there are 87 rows, 29 distinct offsets per film, and no flagged days before comparing totals. Even when cursor pagination ends, the results describe matches exposed by the search service. Full titles can differ in recall across films. This fresh series must be evaluated on its own and kept separate from the historic comparison file.
