from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin
from app.schemas.admin import AdminDashboardStatsResponse
from app.schemas.user import UserPublic
from app.services.admin_service import get_admin_dashboard_stats

router = APIRouter(prefix="/admin/dashboard", tags=["admin-dashboard"])


@router.get("/stats", response_model=AdminDashboardStatsResponse)
async def read_admin_dashboard_stats(
    current_admin: UserPublic = Depends(get_current_admin),
):
    return await get_admin_dashboard_stats()