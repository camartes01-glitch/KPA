"""
Notification Endpoints — User Alerts, Bilingual Kannada/English Notifications, and Scoped Broadcasts.
"""
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.notification import (
    BroadcastCreateRequest,
    NotificationDetailedRead,
    NotificationRead,
)
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get(
    "/my",
    response_model=PaginatedResponse[NotificationRead],
    summary="Get user's notification feed (Supports English & Kannada)",
)
async def get_my_notifications(
    lang: str = Query("en", pattern="^(en|kn)$", description="Language preference: 'en' or 'kn'"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve personalized and geographically scoped announcements in preferred language."""
    notifs, total = await NotificationService.get_user_notifications(
        db=db,
        user=current_user,
        lang=lang,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse(
        success=True,
        data=notifs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post(
    "/{notification_id}/read",
    response_model=APIResponse[dict],
    summary="Mark notification as read",
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    await NotificationService.mark_as_read(db, notification_id, current_user.id)
    return APIResponse(
        success=True,
        message="Notification marked as read",
        data={"id": str(notification_id)},
    )


@router.post(
    "/broadcast",
    response_model=APIResponse[NotificationDetailedRead],
    summary="Send scoped broadcast announcement (Admins only)",
)
async def broadcast_announcement(
    payload: BroadcastCreateRequest,
    current_user: User = Depends(
        require_roles(UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN, UserRole.TALUKA_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
):
    """Send broadcast announcement respecting geographic jurisdiction."""
    notif = await NotificationService.broadcast_notification(db, current_user, payload)
    return APIResponse(
        success=True,
        message="Broadcast sent successfully",
        data=NotificationDetailedRead.model_validate(notif),
    )
