"""Rebuild the COMP 370 results from the private analysis workbook."""
import argparse
import hashlib
import re
from pathlib import Path
from tempfile import TemporaryDirectory

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

TOPICS = ["Reviews", "Viewing", "Industry", "Discourse", "Filmmaking", "Other", "Fandom", "Story"]
FILMS = ["The Odyssey", "Spider-Man: Brand New Day", "Toy Story 5"]
METRICS = ["like_count", "reply_count", "repost_count", "quote_count"]
DISPLAY = ["Likes", "Replies", "Reposts", "Quotes"]
TITLES = re.compile(r"\b(?:the\s+odyssey|theodyssey|toy[\s-]*story[\s-]*5|spider[\s-]*man[\s:\u2013\u2014-]*brand[\s-]*new[\s-]*day)\b", re.I)
LINKS = re.compile(r"(?:https?://|www\.)\S+|\b(?:[\w-]+\.)+[a-zA-Z]{2,}(?:/\S*)?|(?<!\w)@[\w.:-]+")
EXTRA_STOP = {"ve", "ll", "re", "don", "didn", "doesn", "isn", "wasn", "just"}


def validate(posts):
    required = {"movie", "uri", "Final topic", "Analysis text", "Analysis title", *METRICS}
    missing = required - set(posts)
    if missing:
        raise ValueError(f"Analysis data is missing columns: {sorted(missing)}")
    for field in ["uri", "Analysis text"]:
        if posts[field].fillna("").str.strip().eq("").any():
            raise ValueError(f"Blank {field}")
    if posts.uri.duplicated().any():
        raise ValueError("Duplicate post URI")
    if not posts["Final topic"].isin(TOPICS).all() or set(posts.movie) != set(FILMS):
        raise ValueError("Unrecognized topic, missing topic, or unexpected set of films")
    counts = posts[METRICS].apply(pd.to_numeric, errors="raise")
    if not np.isfinite(counts.to_numpy()).all() or ((counts < 0) | (counts % 1 != 0)).any().any():
        raise ValueError("Invalid engagement count")
    posts[METRICS] = counts


def post_document(body, title):
    if title.strip() and title.casefold() not in body.casefold():
        return body + " " + title
    return body


def characterize(posts):
    texts = [post_document(body, title) for body, title in
             zip(posts["Analysis text"], posts["Analysis title"].fillna(""))]
    cleaned = [TITLES.sub(" ", LINKS.sub(" ", doc)).replace("\u2019", "'") for doc in texts]
    vectorizer = TfidfVectorizer(
        stop_words=sorted(set(ENGLISH_STOP_WORDS) | EXTRA_STOP),
        token_pattern=r"(?u)\b[^\W\d_]{2,}\b", strip_accents="unicode", min_df=2,
    )
    matrix = vectorizer.fit_transform(cleaned)
    terms = vectorizer.get_feature_names_out()
    rows = []
    for topic in TOPICS:
        mask = posts["Final topic"].eq(topic).to_numpy()
        if not mask.any():
            raise ValueError(f"No posts for topic {topic}")
        scores = np.asarray(matrix[mask].mean(axis=0)).ravel()
        for rank, i in enumerate(np.lexsort((terms, -scores))[:10], 1):
            rows.append((topic, rank, terms[i], scores[i]))
    words = pd.DataFrame(rows, columns=["Topic", "Rank", "Word", "Mean TF-IDF"])
    sample = posts.assign(
        text=texts, sort_key=posts.uri.map(lambda s: hashlib.sha256(s.encode()).hexdigest())
    ).sort_values("sort_key").groupby(["Final topic", "movie"], sort=False).head(4)
    return words, sample[["Final topic", "movie", "uri", "text"]], len(terms), (matrix.getnnz(axis=1) == 0).sum()


def coverage(book):
    days = pd.read_excel(book, sheet_name="Daily coverage")
    offsets = set(range(-7, 22))
    if set(days.Film) != set(FILMS) or days.duplicated(["Film", "Day from release"]).any():
        raise ValueError("Missing film or duplicate film-day")
    if any(set(group["Day from release"]) != offsets for _, group in days.groupby("Film")):
        raise ValueError("Incomplete release window")
    complete = days.Completeness.eq("Full day per collection file")
    numeric = ["Matched", "Top level", "Filtered pool"]
    full_counts = days.loc[complete, numeric]
    if full_counts.isna().any().any() or (full_counts < 0).any().any():
        raise ValueError("Missing or negative full-day counts")
    if not days.loc[~complete, numeric].isna().all().all():
        raise ValueError("Partial days contain full-count estimates")
    eligible = complete.groupby(days.Film).all()
    full = days[days.Film.isin(eligible[eligible].index)]
    totals = full.groupby("Film")[numeric].sum()
    if totals.Matched.sum() > 0:
        totals["Share among fully observed films"] = totals.Matched / totals.Matched.sum()
    return days, full, totals


def plot(data, xlabel, ylabel, path, kind="line"):
    ax = data.plot(kind=kind, figsize=(8, 4.7), width=0.8) if kind == "barh" else data.plot(figsize=(8, 4.7))
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.legend(title="", fontsize=8)
    ax.figure.tight_layout()
    ax.figure.savefig(path, dpi=180)
    plt.close(ax.figure)


def run(book, out):
    posts = pd.read_excel(book, sheet_name="Analysis data")
    validate(posts)
    counts = pd.crosstab(posts["Final topic"], posts.movie).reindex(index=TOPICS, columns=FILMS, fill_value=0)
    shares = counts.div(counts.sum()) * 100
    counts.to_csv(out / "topic_counts.csv")
    shares.to_csv(out / "within_film_percent.csv")
    overall = counts.sum(axis=1).rename("Posts").to_frame()
    overall["Sample percent"] = 100 * overall.Posts / len(posts)
    overall.to_csv(out / "sample_distribution.csv")

    engagement = posts.groupby("Final topic")[METRICS].agg(["mean", "median", "sum", "max"]).reindex(TOPICS)
    engagement.columns = [DISPLAY[METRICS.index(m)] + " " + stat for m, stat in engagement.columns]
    engagement.insert(0, "Posts", overall.Posts)
    engagement.to_csv(out / "engagement.csv")

    words, examples, vocab, empty = characterize(posts)
    words.to_csv(out / "tfidf.csv", index=False)
    examples.to_csv(out / "summary_examples_private.csv", index=False)
    saved = pd.read_excel(book, sheet_name="Topics and words")
    summary_col, = [col for col in saved if col.casefold().endswith("summary")]
    saved.rename(columns={summary_col: "Summary"})[["Topic", "Codebook definition", "Summary"]].to_csv(
        out / "archived_summaries.csv", index=False
    )

    days, full, totals = coverage(book)
    days.to_csv(out / "coverage_daily.csv", index=False)
    totals.to_csv(out / "coverage_totals.csv")
    plot(shares.iloc[::-1], "Percent of each film sample", "", out / "topics.png", "barh")
    if not full.empty:
        plot(full.pivot(index="Day from release", columns="Film", values="Matched"),
             "Day from release", "Matched posts", out / "coverage.png")

    # Compare independent calculations against the saved workbook before publishing files.
    ref = pd.read_excel(book, sheet_name="TF-IDF scores").sort_values(["Topic", "Rank"]).reset_index(drop=True)
    actual = words.sort_values(["Topic", "Rank"]).reset_index(drop=True)
    pd.testing.assert_frame_equal(actual, ref, check_dtype=False, atol=1e-10, rtol=1e-8)
    ref_dist = pd.read_excel(book, sheet_name="Topic distribution").set_index("Topic").loc[TOPICS]
    for movie, short in zip(FILMS, ["Odyssey", "Spider-Man", "Toy Story 5"]):
        np.testing.assert_array_equal(counts[movie], ref_dist[short + " posts"])
        np.testing.assert_allclose(shares[movie] / 100, ref_dist[short + " share"])
    ref_eng = pd.read_excel(book, sheet_name="Engagement").set_index("Topic").loc[TOPICS]
    np.testing.assert_allclose(engagement[ref_eng.columns], ref_eng, atol=0.000051, rtol=0)
    with pd.ExcelFile(book) as workbook:
        inputs_tab, = [tab for tab in workbook.sheet_names if tab.casefold().endswith(" inputs")]
        ref_inputs = workbook.parse(inputs_tab).set_index("URI").sort_index()
    text_col, = [col for col in ref_inputs if col.casefold().endswith("input text")]
    sample = examples.set_index("uri").sort_index()
    if list(sample.index) != list(ref_inputs.index) or list(sample.text) != list(ref_inputs[text_col]):
        raise ValueError("Summary inputs have changed; review the archived summaries")
    print(f"Verified {len(posts)} posts, {len(words)} ranked terms and {len(examples)} summary examples.")
    print(f"Vocabulary: {vocab}; empty vectors: {empty}. Coverage rows: {len(days)}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--out", type=Path, default=Path("analysis/private/results"))
    args = parser.parse_args()
    if args.out.exists():
        parser.error("Choose a new output directory to preserve previous results")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=args.out.parent) as temp:
        staging = Path(temp) / "results"
        staging.mkdir()
        run(args.workbook, staging)
        staging.rename(args.out)
