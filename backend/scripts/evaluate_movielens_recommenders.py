from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split

DATASET_DIR = Path(__file__).resolve().parents[1] / "datasets" / "ml-latest-small"
REPORT_DIR = Path(__file__).resolve().parents[1] / "models" / "recommendations"


def precision_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    if not recommended:
        return 0.0
    return len(set(recommended[:k]) & relevant) / k


def recall_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(recommended[:k]) & relevant) / len(relevant)


def ndcg_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    dcg = 0.0
    for index, item_id in enumerate(recommended[:k]):
        if item_id in relevant:
            dcg += 1.0 / math.log2(index + 2)

    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(index + 2) for index in range(ideal_hits))
    return dcg / idcg if idcg > 0 else 0.0


def evaluate() -> None:
    ratings_path = DATASET_DIR / "ratings.csv"
    movies_path = DATASET_DIR / "movies.csv"

    if not ratings_path.exists() or not movies_path.exists():
        raise FileNotFoundError(
            "MovieLens files not found. Download ml-latest-small.zip from GroupLens, "
            "unzip it into backend/datasets/ml-latest-small/, then run this script again."
        )

    ratings = pd.read_csv(ratings_path)
    movies = pd.read_csv(movies_path)

    positive_ratings = ratings[ratings["rating"] >= 4.0].copy()
    train, test = train_test_split(positive_ratings, test_size=0.2, random_state=42, stratify=positive_ratings["userId"])

    movie_ids = movies["movieId"].tolist()
    movie_index = {movie_id: index for index, movie_id in enumerate(movie_ids)}

    movies["feature_text"] = (movies["title"].fillna("") + " " + movies["genres"].fillna("").str.replace("|", " ", regex=False)).str.lower()
    vectorizer = TfidfVectorizer(max_features=8000, ngram_range=(1, 2), stop_words="english")
    content_matrix = vectorizer.fit_transform(movies["feature_text"])

    train_user_items = train.groupby("userId")["movieId"].apply(list).to_dict()
    test_user_items = test.groupby("userId")["movieId"].apply(set).to_dict()

    # Item-based collaborative similarity from train ratings.
    row_indexes = train["userId"].astype("category").cat.codes.to_numpy()
    user_categories = train["userId"].astype("category").cat.categories
    user_id_to_row = {user_id: idx for idx, user_id in enumerate(user_categories)}
    col_indexes = train["movieId"].map(movie_index).to_numpy()
    values = train["rating"].to_numpy(dtype=float)
    user_item_matrix = sparse.csr_matrix((values, (row_indexes, col_indexes)), shape=(len(user_categories), len(movie_ids)))
    item_similarity = cosine_similarity(user_item_matrix.T, dense_output=False)

    k = 10
    rows = []

    for algorithm in ["content_based", "collaborative", "hybrid"]:
        precisions = []
        recalls = []
        ndcgs = []

        for user_id, relevant in test_user_items.items():
            history = [movie_id for movie_id in train_user_items.get(user_id, []) if movie_id in movie_index]
            if not history:
                continue

            history_indexes = [movie_index[movie_id] for movie_id in history]
            seen = set(history)

            content_scores = np.asarray(content_matrix[history_indexes].mean(axis=0) @ content_matrix.T).ravel()

            collab_scores = np.zeros(len(movie_ids))
            if user_id in user_id_to_row:
                user_row = user_item_matrix[user_id_to_row[user_id]]
                collab_scores = np.asarray(user_row @ item_similarity).ravel()

            if algorithm == "content_based":
                scores = content_scores
            elif algorithm == "collaborative":
                scores = collab_scores
            else:
                content_max = content_scores.max() or 1.0
                collab_max = collab_scores.max() or 1.0
                scores = 0.55 * (content_scores / content_max) + 0.45 * (collab_scores / collab_max)

            ranked_indexes = np.argsort(scores)[::-1]
            recommended = []
            for index in ranked_indexes:
                movie_id = movie_ids[int(index)]
                if movie_id in seen:
                    continue
                recommended.append(movie_id)
                if len(recommended) >= k:
                    break

            precisions.append(precision_at_k(recommended, relevant, k))
            recalls.append(recall_at_k(recommended, relevant, k))
            ndcgs.append(ndcg_at_k(recommended, relevant, k))

        rows.append(
            {
                "algorithm": algorithm,
                "precision_at_10": round(float(np.mean(precisions)), 4),
                "recall_at_10": round(float(np.mean(recalls)), 4),
                "ndcg_at_10": round(float(np.mean(ndcgs)), 4),
            }
        )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "movielens_metrics_report.json"
    with report_path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)

    print(json.dumps(rows, ensure_ascii=False, indent=2))
    print(f"Saved report to: {report_path}")


if __name__ == "__main__":
    evaluate()
