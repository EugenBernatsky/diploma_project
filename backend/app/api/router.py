from fastapi import APIRouter

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.items import router as items_router
from app.api.endpoints.users import router as users_router
from app.api.endpoints.favorites import router as favorites_router
from app.api.endpoints.ratings import router as ratings_router
from app.api.endpoints.statuses import router as statuses_router
from app.api.endpoints.interactions import router as interactions_router
from app.api.endpoints.comments import router as comments_router
from app.api.endpoints.admin_comments import router as admin_comments_router
from app.api.endpoints.notifications import router as notifications_router
from app.api.endpoints.forum import router as forum_router
from app.api.endpoints.admin_forum import router as admin_forum_router
from app.api.endpoints.admin_items import router as admin_items_router
from app.api.endpoints.profile import router as profile_router
from app.api.endpoints.recommendations import router as recommendations_router
from app.api.endpoints.admin_dashboard import router as admin_dashboard_router

api_router = APIRouter()

api_router.include_router(items_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(favorites_router)
api_router.include_router(ratings_router)
api_router.include_router(statuses_router)
api_router.include_router(interactions_router)
api_router.include_router(comments_router)
api_router.include_router(admin_comments_router)
api_router.include_router(notifications_router)
api_router.include_router(forum_router)
api_router.include_router(admin_forum_router)
api_router.include_router(admin_items_router)
api_router.include_router(profile_router)
api_router.include_router(recommendations_router)
api_router.include_router(admin_dashboard_router)