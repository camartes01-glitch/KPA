"""
Welfare Event Endpoints — Event creation, contribution ledgers, and member obligations.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.user import User, UserRole
from app.models.welfare import WelfareEventStatus
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.welfare import (
    WelfareEventCreate,
    WelfareEventRead,
    WelfareObligationRead,
)
from app.services.member_service import MemberService
from app.services.welfare_service import WelfareService

router = APIRouter()


@router.post(
    "",
    response_model=APIResponse[WelfareEventRead],
    summary="Create a new Welfare Event (STATE_HEAD only)",
)
async def create_welfare_event(
    payload: WelfareEventCreate,
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD)),
    db: AsyncSession = Depends(get_db),
):
    """Initiate welfare relief event and generate ₹10 obligations for all active members."""
    event = await WelfareService.create_welfare_event(db, current_user, payload)
    return APIResponse(
        success=True,
        message="Welfare event created and member contributions generated",
        data=WelfareEventRead.model_validate(event),
    )


@router.get(
    "",
    response_model=PaginatedResponse[WelfareEventRead],
    summary="List all welfare events",
)
async def list_welfare_events(
    status_filter: Optional[WelfareEventStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Fetch paginated welfare events."""
    events, total = await WelfareService.get_events(db, status_filter, page, page_size)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse(
        success=True,
        data=[WelfareEventRead.model_validate(e) for e in events],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/my-obligations",
    response_model=APIResponse[List[WelfareObligationRead]],
    summary="Get current member's contribution obligations",
)
async def get_my_obligations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch all pending and settled ₹10 mutual relief debits for authenticated member."""
    member = await MemberService.get_member_by_user(db, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member profile not registered",
        )
    obligations = await WelfareService.get_member_obligations(db, member.id)
    return APIResponse(
        success=True,
        message="Obligations retrieved",
        data=obligations,
    )


@router.get(
    "/{event_id}",
    response_model=APIResponse[WelfareEventRead],
    summary="Get welfare event details",
)
async def get_welfare_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Fetch specific welfare event by ID."""
    event = await WelfareService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Welfare event not found")
    return APIResponse(
        success=True,
        message="Welfare event details retrieved",
        data=WelfareEventRead.model_validate(event),
    )
