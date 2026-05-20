from app.db.mongo import get_db
from pymongo import ASCENDING, DESCENDING

async def create_indexes() -> None:
    db = get_db()

    await db.media_items.create_index("category")
    await db.media_items.create_index("title")
    await db.media_items.create_index("year")
    await db.media_items.create_index(
        [("external_source", ASCENDING), ("external_id", ASCENDING)],
        unique=True,
    )

    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)

    await db.favorites.create_index("user_id")
    await db.favorites.create_index("item_id")
    await db.favorites.create_index(
        [("user_id", ASCENDING), ("item_id", ASCENDING)],
        unique=True,
    )

    await db.ratings.create_index("user_id")
    await db.ratings.create_index("item_id")
    await db.ratings.create_index(
        [("user_id", ASCENDING), ("item_id", ASCENDING)],
        unique=True,
    )

    await db.item_statuses.create_index("user_id")
    await db.item_statuses.create_index("item_id")
    await db.item_statuses.create_index("status")
    await db.item_statuses.create_index(
        [("user_id", ASCENDING), ("item_id", ASCENDING)],
        unique=True,
    )
    await db.item_statuses.create_index(
        [("user_id", ASCENDING), ("status", ASCENDING)],
    )

    await db.interactions.create_index("user_id")
    await db.interactions.create_index("item_id")
    await db.interactions.create_index("interaction_type")
    await db.interactions.create_index(
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
    )
    await db.interactions.create_index(
        [("item_id", ASCENDING), ("created_at", DESCENDING)],
    )

    await db.comments.create_index("item_id")
    await db.comments.create_index("user_id")
    await db.comments.create_index("parent_comment_id")
    await db.comments.create_index("created_at")
    await db.comments.create_index(
        [("item_id", ASCENDING), ("parent_comment_id", ASCENDING), ("created_at", ASCENDING)],
    )
    await db.comments.create_index(
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
    )

    await db.notifications.create_index("user_id")
    await db.notifications.create_index("is_read")
    await db.notifications.create_index("created_at")
    await db.notifications.create_index(
        [("user_id", ASCENDING), ("is_read", ASCENDING), ("created_at", DESCENDING)],
    )

    await db.forum_threads.create_index("user_id")
    await db.forum_threads.create_index("created_at")
    await db.forum_threads.create_index("last_activity_at")
    await db.forum_threads.create_index("score")
    await db.forum_threads.create_index(
        [("last_activity_at", DESCENDING)],
    )
    await db.forum_threads.create_index(
        [("score", DESCENDING), ("last_activity_at", DESCENDING)],
    )

    await db.forum_posts.create_index("thread_id")
    await db.forum_posts.create_index("user_id")
    await db.forum_posts.create_index("parent_post_id")
    await db.forum_posts.create_index("created_at")
    await db.forum_posts.create_index("score")
    await db.forum_posts.create_index(
        [("thread_id", ASCENDING), ("parent_post_id", ASCENDING), ("created_at", ASCENDING)],
    )
    await db.forum_posts.create_index(
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
    )

    await db.forum_votes.create_index("user_id")
    await db.forum_votes.create_index("target_type")
    await db.forum_votes.create_index("target_id")
    await db.forum_votes.create_index(
        [("user_id", ASCENDING), ("target_type", ASCENDING), ("target_id", ASCENDING)],
        unique=True,
    )