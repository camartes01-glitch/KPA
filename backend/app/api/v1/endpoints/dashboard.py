"""
Dashboard Endpoints — Aggregated Analytics & Live KPIs.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.dashboard import DashboardMetricsRead
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get(
    "/metrics",
    response_model=APIResponse[DashboardMetricsRead],
    summary="Get role-aware dashboard analytical KPIs",
)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve summarized metrics and breakdown statistics according to user permissions."""
    metrics = await DashboardService.get_metrics(db, current_user)
    return APIResponse(
        success=True,
        message="Dashboard metrics retrieved",
        data=metrics,
    )
