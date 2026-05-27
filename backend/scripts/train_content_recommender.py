from __future__ import annotations

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

from app.db.mongo import close_mongo_connection, connect_to_mongo, get_db
from app.ml.recommendations.feature_builder import build_item_feature_text

MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "recommendations"


def _metadata_for_item(item: dict) -> dict:
    return {
        "id": str(item["_id"]),
        "title": item.get("title"),
        "category": item.get("category"),
        "year": item.get("year"),
        "genres": item.get("genres", []),
        "external_source": item.get("external_source"),
        "external_id": item.get("external_id"),
    }


async def train_content_recommender() -> None:
    await connect_to_mongo()

    try:
        db = get_db()
        items = await db.media_items.find({}).to_list(length=10000)

        if len(items) < 2:
            raise RuntimeError("Need at least 2 media items to train the content recommender.")

        item_ids = [str(item["_id"]) for item in items]
        feature_texts = [build_item_feature_text(item) for item in items]

        vectorizer = TfidfVectorizer(
            max_features=12000,
            ngram_range=(1, 2),
            min_df=1,
            stop_words="english",
        )
        item_matrix = vectorizer.fit_transform(feature_texts)

        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(vectorizer, MODEL_DIR / "tfidf_vectorizer.joblib")
        sparse.save_npz(MODEL_DIR / "item_matrix.npz", item_matrix)

        with (MODEL_DIR / "item_ids.json").open("w", encoding="utf-8") as file:
            json.dump(item_ids, file, ensure_ascii=False, indent=2)

        metadata = {str(item["_id"]): _metadata_for_item(item) for item in items}
        with (MODEL_DIR / "item_metadata.json").open("w", encoding="utf-8") as file:
            json.dump(metadata, file, ensure_ascii=False, indent=2)

        info = {
            "trained_at": datetime.now(UTC).isoformat(),
            "items_count": len(items),
            "features_count": int(item_matrix.shape[1]),
            "model_type": "content_based_tfidf",
        }
        with (MODEL_DIR / "model_info.json").open("w", encoding="utf-8") as file:
            json.dump(info, file, ensure_ascii=False, indent=2)

        print("Content recommender trained successfully.")
        print(json.dumps(info, ensure_ascii=False, indent=2))

    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(train_content_recommender())
