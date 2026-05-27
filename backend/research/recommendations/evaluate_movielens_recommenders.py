from __future__ import annotations

import json
import math
import shutil
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BACKEND_DIR = Path(__file__).resolve().parents[2]

DATASET_DIR = BACKEND_DIR / "datasets" / "ml-latest-small"
REPORT_ROOT = BACKEND_DIR / "reports" / "recommendations" / "movielens"

RANDOM_SEED = 42
RELEVANT_RATING_THRESHOLD = 4.0
TEST_FRACTION = 0.2
MIN_POSITIVE_RATINGS_PER_USER = 5
K_VALUES = [5, 10, 15, 20]
MAX_K = max(K_VALUES)

HYBRID_WEIGHTS = {
    "hybrid_cbf_70_cf_30": (0.70, 0.30),
    "hybrid_cbf_50_cf_50": (0.50, 0.50),
    "hybrid_cbf_30_cf_70": (0.30, 0.70),
}

MODEL_DISPLAY_NAMES = {
    "content_based": "Content-based",
    "collaborative": "Collaborative filtering",
    "hybrid_cbf_70_cf_30": "Hybrid CBF 0.7 / CF 0.3",
    "hybrid_cbf_50_cf_50": "Hybrid CBF 0.5 / CF 0.5",
    "hybrid_cbf_30_cf_70": "Hybrid CBF 0.3 / CF 0.7",
}


def precision_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    if k <= 0:
        return 0.0

    recommended_at_k = recommended[:k]

    if not recommended_at_k:
        return 0.0

    hits = len(set(recommended_at_k) & relevant)

    return hits / k


def recall_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    if not relevant:
        return 0.0

    recommended_at_k = recommended[:k]
    hits = len(set(recommended_at_k) & relevant)

    return hits / len(relevant)


def ndcg_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    dcg = 0.0

    for index, movie_id in enumerate(recommended[:k]):
        if movie_id in relevant:
            dcg += 1.0 / math.log2(index + 2)

    ideal_hits = min(len(relevant), k)
    idcg = sum(
        1.0 / math.log2(index + 2)
        for index in range(ideal_hits)
    )

    return dcg / idcg if idcg > 0 else 0.0


def map_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    if not relevant:
        return 0.0

    hits = 0
    precision_sum = 0.0

    for index, movie_id in enumerate(recommended[:k], start=1):
        if movie_id in relevant:
            hits += 1
            precision_sum += hits / index

    denominator = min(len(relevant), k)

    return precision_sum / denominator if denominator > 0 else 0.0


def normalize_scores(scores: np.ndarray) -> np.ndarray:
    result = np.asarray(scores, dtype=float).copy()
    result[~np.isfinite(result)] = 0.0

    max_score = result.max()

    if max_score <= 0:
        return np.zeros_like(result)

    return result / max_score


def top_k_from_scores(
    scores: np.ndarray,
    movie_ids: list[int],
    movie_index: dict[int, int],
    seen_movie_ids: set[int],
    k: int,
) -> list[int]:
    safe_scores = np.asarray(scores, dtype=float).copy()
    safe_scores[~np.isfinite(safe_scores)] = 0.0

    for movie_id in seen_movie_ids:
        index = movie_index.get(movie_id)

        if index is not None:
            safe_scores[index] = -np.inf

    ranked_indexes = np.argsort(safe_scores)[::-1]

    recommendations: list[int] = []

    for index in ranked_indexes:
        score = safe_scores[index]

        if not np.isfinite(score):
            continue

        if score <= 0:
            continue

        recommendations.append(movie_ids[index])

        if len(recommendations) >= k:
            break

    return recommendations


def load_movielens() -> tuple[pd.DataFrame, pd.DataFrame]:
    ratings_path = DATASET_DIR / "ratings.csv"
    movies_path = DATASET_DIR / "movies.csv"

    if not ratings_path.exists() or not movies_path.exists():
        raise FileNotFoundError(
            "MovieLens files not found. Expected files:\n"
            f"- {ratings_path}\n"
            f"- {movies_path}\n\n"
            "Download ml-latest-small and unzip it into backend/datasets/ml-latest-small/"
        )

    ratings = pd.read_csv(ratings_path)
    movies = pd.read_csv(movies_path)

    ratings["userId"] = ratings["userId"].astype(int)
    ratings["movieId"] = ratings["movieId"].astype(int)
    ratings["rating"] = ratings["rating"].astype(float)

    movies["movieId"] = movies["movieId"].astype(int)

    return ratings, movies


def build_per_user_train_test_split(
    ratings: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[int, list[int]], dict[int, set[int]]]:
    positive_ratings = ratings[
        ratings["rating"] >= RELEVANT_RATING_THRESHOLD
    ].copy()

    rng = np.random.default_rng(RANDOM_SEED)

    train_records: list[dict] = []
    train_user_items: dict[int, list[int]] = {}
    test_user_items: dict[int, set[int]] = {}

    for user_id, group in positive_ratings.groupby("userId"):
        unique_movie_ids = group["movieId"].drop_duplicates().to_numpy(dtype=int)

        if len(unique_movie_ids) < MIN_POSITIVE_RATINGS_PER_USER:
            continue

        shuffled = unique_movie_ids.copy()
        rng.shuffle(shuffled)

        test_count = max(1, int(round(len(shuffled) * TEST_FRACTION)))
        train_items = shuffled[test_count:]
        test_items = shuffled[:test_count]

        if len(train_items) == 0 or len(test_items) == 0:
            continue

        user_id_int = int(user_id)

        train_user_items[user_id_int] = [
            int(movie_id)
            for movie_id in train_items
        ]

        test_user_items[user_id_int] = {
            int(movie_id)
            for movie_id in test_items
        }

        for movie_id in train_items:
            train_records.append(
                {
                    "userId": user_id_int,
                    "movieId": int(movie_id),
                    "value": 1.0,
                }
            )

    train_positive = pd.DataFrame(train_records)

    return train_positive, train_user_items, test_user_items


def build_content_features(
    movies: pd.DataFrame,
) -> tuple[list[int], dict[int, int], sparse.csr_matrix]:
    movies = movies.copy()

    movie_ids = movies["movieId"].astype(int).tolist()
    movie_index = {
        movie_id: index
        for index, movie_id in enumerate(movie_ids)
    }

    movies["feature_text"] = (
        movies["title"].fillna("")
        + " "
        + movies["genres"].fillna("").str.replace("|", " ", regex=False)
    ).str.lower()

    vectorizer = TfidfVectorizer(
        max_features=8000,
        ngram_range=(1, 2),
        stop_words="english",
    )

    content_matrix = vectorizer.fit_transform(movies["feature_text"]).tocsr()

    return movie_ids, movie_index, content_matrix


def build_collaborative_model(
    train_positive: pd.DataFrame,
    movie_ids: list[int],
    movie_index: dict[int, int],
) -> tuple[sparse.csr_matrix, sparse.csr_matrix, dict[int, int]]:
    train_positive = train_positive[
        train_positive["movieId"].isin(movie_index)
    ].copy()

    user_categories = pd.Categorical(train_positive["userId"])
    row_indexes = user_categories.codes

    user_id_to_row = {
        int(user_id): int(index)
        for index, user_id in enumerate(user_categories.categories)
    }

    col_indexes = train_positive["movieId"].map(movie_index).to_numpy(dtype=int)
    values = train_positive["value"].to_numpy(dtype=float)

    user_item_matrix = sparse.csr_matrix(
        (values, (row_indexes, col_indexes)),
        shape=(len(user_categories.categories), len(movie_ids)),
    )

    item_similarity = cosine_similarity(
        user_item_matrix.T,
        dense_output=False,
    ).tocsr()

    return user_item_matrix, item_similarity, user_id_to_row


def get_content_scores_for_user(
    history_movie_ids: list[int],
    movie_index: dict[int, int],
    content_matrix: sparse.csr_matrix,
) -> np.ndarray:
    history_indexes = [
        movie_index[movie_id]
        for movie_id in history_movie_ids
        if movie_id in movie_index
    ]

    if not history_indexes:
        return np.zeros(content_matrix.shape[0], dtype=float)

    user_profile = sparse.csr_matrix(
        content_matrix[history_indexes].mean(axis=0)
    )

    scores = user_profile @ content_matrix.T

    return np.asarray(scores.toarray()).ravel()


def get_collaborative_scores_for_user(
    user_id: int,
    user_item_matrix: sparse.csr_matrix,
    item_similarity: sparse.csr_matrix,
    user_id_to_row: dict[int, int],
    items_count: int,
) -> np.ndarray:
    row_index = user_id_to_row.get(user_id)

    if row_index is None:
        return np.zeros(items_count, dtype=float)

    user_row = user_item_matrix[row_index]
    scores = user_row @ item_similarity

    return np.asarray(scores.toarray()).ravel()


def evaluate_models(
    movies: pd.DataFrame,
    ratings: pd.DataFrame,
    train_positive: pd.DataFrame,
    train_user_items: dict[int, list[int]],
    test_user_items: dict[int, set[int]],
    movie_ids: list[int],
    movie_index: dict[int, int],
    content_matrix: sparse.csr_matrix,
    user_item_matrix: sparse.csr_matrix,
    item_similarity: sparse.csr_matrix,
    user_id_to_row: dict[int, int],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict] = []
    example_rows: list[dict] = []

    movie_metadata = movies.set_index("movieId")[["title", "genres"]].to_dict("index")

    evaluated_users = 0

    for user_id, relevant_items in test_user_items.items():
        history_items = [
            movie_id
            for movie_id in train_user_items.get(user_id, [])
            if movie_id in movie_index
        ]

        if not history_items:
            continue

        evaluated_users += 1

        seen_items = set(history_items)

        content_scores = get_content_scores_for_user(
            history_movie_ids=history_items,
            movie_index=movie_index,
            content_matrix=content_matrix,
        )

        collaborative_scores = get_collaborative_scores_for_user(
            user_id=user_id,
            user_item_matrix=user_item_matrix,
            item_similarity=item_similarity,
            user_id_to_row=user_id_to_row,
            items_count=len(movie_ids),
        )

        score_sets: dict[str, np.ndarray] = {
            "content_based": content_scores,
            "collaborative": collaborative_scores,
        }

        normalized_content_scores = normalize_scores(content_scores)
        normalized_collaborative_scores = normalize_scores(collaborative_scores)

        for model_key, (content_weight, collaborative_weight) in HYBRID_WEIGHTS.items():
            score_sets[model_key] = (
                content_weight * normalized_content_scores
                + collaborative_weight * normalized_collaborative_scores
            )

        for model_key, scores in score_sets.items():
            recommended = top_k_from_scores(
                scores=scores,
                movie_ids=movie_ids,
                movie_index=movie_index,
                seen_movie_ids=seen_items,
                k=MAX_K,
            )

            for k in K_VALUES:
                rows.append(
                    {
                        "model": model_key,
                        "model_name": MODEL_DISPLAY_NAMES[model_key],
                        "k": k,
                        "precision": precision_at_k(recommended, relevant_items, k),
                        "recall": recall_at_k(recommended, relevant_items, k),
                        "ndcg": ndcg_at_k(recommended, relevant_items, k),
                        "map": map_at_k(recommended, relevant_items, k),
                    }
                )

            if len(example_rows) < 5 * len(score_sets) * 10:
                for rank, movie_id in enumerate(recommended[:10], start=1):
                    metadata = movie_metadata.get(movie_id, {})

                    example_rows.append(
                        {
                            "userId": user_id,
                            "model": model_key,
                            "model_name": MODEL_DISPLAY_NAMES[model_key],
                            "rank": rank,
                            "movieId": movie_id,
                            "title": metadata.get("title"),
                            "genres": metadata.get("genres"),
                            "was_relevant_in_test": movie_id in relevant_items,
                        }
                    )

    metrics_raw = pd.DataFrame(rows)

    metrics_by_k = (
        metrics_raw
        .groupby(["model", "model_name", "k"], as_index=False)
        .agg(
            precision=("precision", "mean"),
            recall=("recall", "mean"),
            ndcg=("ndcg", "mean"),
            map=("map", "mean"),
        )
    )

    metrics_by_k["evaluated_users"] = evaluated_users

    examples = pd.DataFrame(example_rows)

    return metrics_by_k, examples


def build_dataset_summary(
    ratings: pd.DataFrame,
    movies: pd.DataFrame,
    train_positive: pd.DataFrame,
    train_user_items: dict[int, list[int]],
    test_user_items: dict[int, set[int]],
) -> dict:
    positive_ratings_count = int(
        (ratings["rating"] >= RELEVANT_RATING_THRESHOLD).sum()
    )

    return {
        "dataset": "MovieLens ml-latest-small",
        "users_total": int(ratings["userId"].nunique()),
        "movies_total": int(movies["movieId"].nunique()),
        "ratings_total": int(len(ratings)),
        "positive_ratings_threshold": RELEVANT_RATING_THRESHOLD,
        "positive_ratings_total": positive_ratings_count,
        "train_positive_interactions": int(len(train_positive)),
        "evaluation_users": int(len(test_user_items)),
        "test_fraction": TEST_FRACTION,
        "min_positive_ratings_per_user": MIN_POSITIVE_RATINGS_PER_USER,
        "random_seed": RANDOM_SEED,
    }


def save_json(path: Path, data) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def save_dataframe_json(path: Path, dataframe: pd.DataFrame) -> None:
    with path.open("w", encoding="utf-8") as file:
        file.write(dataframe.to_json(orient="records", force_ascii=False, indent=2))


def plot_metric_at_k(
    metrics_by_k: pd.DataFrame,
    output_dir: Path,
    metric: str,
    k: int = 10,
) -> None:
    data = metrics_by_k[metrics_by_k["k"] == k].copy()
    data = data.sort_values(metric, ascending=False)

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.bar(data["model_name"], data[metric])
    ax.set_title(f"{metric.upper()}@{k} comparison")
    ax.set_xlabel("Model")
    ax.set_ylabel(f"{metric.upper()}@{k}")
    ax.tick_params(axis="x", rotation=25)

    fig.tight_layout()
    fig.savefig(output_dir / f"{metric}_at_{k}.png", dpi=180)
    plt.close(fig)


def plot_metric_by_k(
    metrics_by_k: pd.DataFrame,
    output_dir: Path,
    metric: str,
) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))

    for model_name, group in metrics_by_k.groupby("model_name"):
        group = group.sort_values("k")
        ax.plot(group["k"], group[metric], marker="o", label=model_name)

    ax.set_title(f"{metric.upper()} by K")
    ax.set_xlabel("K")
    ax.set_ylabel(metric.upper())
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_dir / f"{metric}_by_k.png", dpi=180)
    plt.close(fig)


def plot_dataset_summary(summary: dict, output_dir: Path) -> None:
    keys = [
        "users_total",
        "movies_total",
        "ratings_total",
        "positive_ratings_total",
        "train_positive_interactions",
        "evaluation_users",
    ]

    values = [summary[key] for key in keys]

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.bar(keys, values)
    ax.set_title("MovieLens dataset summary")
    ax.set_xlabel("Statistic")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=25)

    fig.tight_layout()
    fig.savefig(output_dir / "dataset_summary.png", dpi=180)
    plt.close(fig)


def plot_rating_distribution(ratings: pd.DataFrame, output_dir: Path) -> None:
    distribution = (
        ratings["rating"]
        .value_counts()
        .sort_index()
    )

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.bar(distribution.index.astype(str), distribution.values)
    ax.set_title("MovieLens rating distribution")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Count")

    fig.tight_layout()
    fig.savefig(output_dir / "rating_distribution.png", dpi=180)
    plt.close(fig)


def create_report_notes(
    run_dir: Path,
    dataset_summary: dict,
    metrics_at_10: pd.DataFrame,
) -> None:
    best_precision_row = metrics_at_10.sort_values(
        "precision",
        ascending=False,
    ).iloc[0]

    best_recall_row = metrics_at_10.sort_values(
        "recall",
        ascending=False,
    ).iloc[0]

    best_ndcg_row = metrics_at_10.sort_values(
        "ndcg",
        ascending=False,
    ).iloc[0]

    text = f"""# MovieLens Offline Evaluation Report

## Dataset

- Dataset: {dataset_summary["dataset"]}
- Users: {dataset_summary["users_total"]}
- Movies: {dataset_summary["movies_total"]}
- Ratings: {dataset_summary["ratings_total"]}
- Relevant rating threshold: rating >= {dataset_summary["positive_ratings_threshold"]}
- Evaluation users: {dataset_summary["evaluation_users"]}
- Test fraction: {dataset_summary["test_fraction"]}

## Models

Evaluated models:

1. Content-based filtering
2. Item-based collaborative filtering
3. Hybrid model with several CBF/CF weight combinations

## Best results at K=10

- Best Precision@10: {best_precision_row["model_name"]} = {best_precision_row["precision"]:.4f}
- Best Recall@10: {best_recall_row["model_name"]} = {best_recall_row["recall"]:.4f}
- Best NDCG@10: {best_ndcg_row["model_name"]} = {best_ndcg_row["ndcg"]:.4f}

## Files generated

- dataset_summary.json
- dataset_summary.csv
- metrics_by_k.csv
- metrics_by_k.json
- metrics_at_10.csv
- metrics_at_10.json
- hybrid_weights_at_10.csv
- recommendation_examples.csv
- plots/*.png

## Interpretation note

These results are used only for offline evaluation in the diploma work.
They do not replace or directly train the production MediaCompass MongoDB recommendation model.
The purpose is to compare recommendation approaches on a public benchmark dataset.
"""

    (run_dir / "report_notes.md").write_text(text, encoding="utf-8")


def save_outputs(
    ratings: pd.DataFrame,
    dataset_summary: dict,
    metrics_by_k: pd.DataFrame,
    examples: pd.DataFrame,
) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    run_dir = REPORT_ROOT / f"run_{timestamp}"
    plots_dir = run_dir / "plots"

    plots_dir.mkdir(parents=True, exist_ok=True)

    metrics_at_10 = metrics_by_k[metrics_by_k["k"] == 10].copy()
    hybrid_weights_at_10 = metrics_at_10[
        metrics_at_10["model"].str.startswith("hybrid")
    ].copy()

    save_json(run_dir / "dataset_summary.json", dataset_summary)
    pd.DataFrame([dataset_summary]).to_csv(
        run_dir / "dataset_summary.csv",
        index=False,
    )

    metrics_by_k.to_csv(run_dir / "metrics_by_k.csv", index=False)
    save_dataframe_json(run_dir / "metrics_by_k.json", metrics_by_k)

    metrics_at_10.to_csv(run_dir / "metrics_at_10.csv", index=False)
    save_dataframe_json(run_dir / "metrics_at_10.json", metrics_at_10)

    hybrid_weights_at_10.to_csv(
        run_dir / "hybrid_weights_at_10.csv",
        index=False,
    )

    examples.to_csv(run_dir / "recommendation_examples.csv", index=False)

    run_config = {
        "random_seed": RANDOM_SEED,
        "relevant_rating_threshold": RELEVANT_RATING_THRESHOLD,
        "test_fraction": TEST_FRACTION,
        "min_positive_ratings_per_user": MIN_POSITIVE_RATINGS_PER_USER,
        "k_values": K_VALUES,
        "hybrid_weights": HYBRID_WEIGHTS,
    }

    save_json(run_dir / "run_config.json", run_config)

    plot_metric_at_k(metrics_by_k, plots_dir, metric="precision", k=10)
    plot_metric_at_k(metrics_by_k, plots_dir, metric="recall", k=10)
    plot_metric_at_k(metrics_by_k, plots_dir, metric="ndcg", k=10)
    plot_metric_at_k(metrics_by_k, plots_dir, metric="map", k=10)

    plot_metric_by_k(metrics_by_k, plots_dir, metric="precision")
    plot_metric_by_k(metrics_by_k, plots_dir, metric="recall")
    plot_metric_by_k(metrics_by_k, plots_dir, metric="ndcg")
    plot_metric_by_k(metrics_by_k, plots_dir, metric="map")

    plot_dataset_summary(dataset_summary, plots_dir)
    plot_rating_distribution(ratings, plots_dir)

    create_report_notes(
        run_dir=run_dir,
        dataset_summary=dataset_summary,
        metrics_at_10=metrics_at_10,
    )

    latest_dir = REPORT_ROOT / "latest"

    if latest_dir.exists():
        shutil.rmtree(latest_dir)

    shutil.copytree(run_dir, latest_dir)

    return run_dir


def evaluate() -> None:
    print("Loading MovieLens dataset...")
    ratings, movies = load_movielens()

    print("Building per-user train/test split...")
    train_positive, train_user_items, test_user_items = build_per_user_train_test_split(
        ratings
    )

    print("Building content-based TF-IDF features...")
    movie_ids, movie_index, content_matrix = build_content_features(movies)

    print("Building item-based collaborative filtering model...")
    user_item_matrix, item_similarity, user_id_to_row = build_collaborative_model(
        train_positive=train_positive,
        movie_ids=movie_ids,
        movie_index=movie_index,
    )

    print("Evaluating content-based, collaborative and hybrid models...")
    metrics_by_k, examples = evaluate_models(
        movies=movies,
        ratings=ratings,
        train_positive=train_positive,
        train_user_items=train_user_items,
        test_user_items=test_user_items,
        movie_ids=movie_ids,
        movie_index=movie_index,
        content_matrix=content_matrix,
        user_item_matrix=user_item_matrix,
        item_similarity=item_similarity,
        user_id_to_row=user_id_to_row,
    )

    dataset_summary = build_dataset_summary(
        ratings=ratings,
        movies=movies,
        train_positive=train_positive,
        train_user_items=train_user_items,
        test_user_items=test_user_items,
    )

    run_dir = save_outputs(
        ratings=ratings,
        dataset_summary=dataset_summary,
        metrics_by_k=metrics_by_k,
        examples=examples,
    )

    print()
    print("Offline MovieLens evaluation completed.")
    print(f"Results saved to: {run_dir}")
    print(f"Latest copy saved to: {REPORT_ROOT / 'latest'}")
    print()
    print("Metrics at K=10:")
    print(
        metrics_by_k[metrics_by_k["k"] == 10]
        .sort_values("ndcg", ascending=False)
        .to_string(index=False)
    )


if __name__ == "__main__":
    evaluate()