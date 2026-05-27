from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
from scipy import sparse


MODEL_DIR = Path(__file__).resolve().parents[3] / "models" / "recommendations"


@dataclass(frozen=True)
class RecommendationArtifacts:
    vectorizer: object
    item_matrix: sparse.csr_matrix
    item_ids: list[str]
    item_metadata: dict[str, dict]
    model_info: dict


def model_files_exist(model_dir: Path = MODEL_DIR) -> bool:
    return all(
        [
            (model_dir / "tfidf_vectorizer.joblib").exists(),
            (model_dir / "item_matrix.npz").exists(),
            (model_dir / "item_ids.json").exists(),
            (model_dir / "item_metadata.json").exists(),
        ]
    )


def load_recommendation_artifacts(model_dir: Path = MODEL_DIR) -> RecommendationArtifacts:
    if not model_files_exist(model_dir):
        raise FileNotFoundError(
            "Recommendation model artifacts were not found. "
            "Run: python scripts/train_content_recommender.py"
        )

    vectorizer = joblib.load(model_dir / "tfidf_vectorizer.joblib")
    item_matrix = sparse.load_npz(model_dir / "item_matrix.npz").tocsr()

    with (model_dir / "item_ids.json").open("r", encoding="utf-8") as file:
        item_ids = json.load(file)

    with (model_dir / "item_metadata.json").open("r", encoding="utf-8") as file:
        item_metadata = json.load(file)

    info_path = model_dir / "model_info.json"
    model_info = {}
    if info_path.exists():
        with info_path.open("r", encoding="utf-8") as file:
            model_info = json.load(file)

    return RecommendationArtifacts(
        vectorizer=vectorizer,
        item_matrix=item_matrix,
        item_ids=item_ids,
        item_metadata=item_metadata,
        model_info=model_info,
    )
