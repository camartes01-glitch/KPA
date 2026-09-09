"""
Member Endpoints — Photographer registration, verification approval, search, and digital cards.
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import enforce_geo_scope, get_current_user, get_db, require_roles
from app.models.member import Member, MemberStatus
from app.models.user import User, UserRole
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.member import (
    DigitalCardResponse,
    MemberApprovalRequest,
    MemberRead,
    MemberRejectionRequest,
    MemberRegisterRequest,
    MemberWithNomineesRead,
)
from app.services.member_service import MemberService

router = APIRouter()


@router.post(
    "/register",
    response_model=APIResponse[MemberRead],
    summary="Register membership profile for authenticated user",
)
async def register_member(
    payload: MemberRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register member details and nominee information."""
    member = await MemberService.register_member(db, current_user, payload)
    return APIResponse(
        success=True,
        message="Registration submitted for verification",
        data=MemberRead.model_validate(member),
    )


@router.get(
    "/me",
    response_model=APIResponse[MemberWithNomineesRead],
    summary="Get current user's member profile and nominee details",
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve logged-in member's profile."""
    member = await MemberService.get_member_by_user(db, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member profile has not been registered yet",
        )
    return APIResponse(
        success=True,
        message="Member profile retrieved",
        data=MemberWithNomineesRead.model_validate(member),
    )


@router.get(
    "/me/card",
    response_model=APIResponse[DigitalCardResponse],
    summary="Get digital membership ID card and verification QR",
)
async def get_my_digital_card(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve digital card details and base64 QR code image."""
    member = await MemberService.get_member_by_user(db, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member profile not found",
        )
    card_data = await MemberService.get_digital_card(db, member.id)
    return APIResponse(
        success=True,
        message="Digital card retrieved",
        data=card_data,
    )


@router.get(
    "",
    response_model=PaginatedResponse[MemberRead],
    summary="Search and filter members (Admins only)",
)
async def search_members(
    q: Optional[str] = Query(None, description="Search by name, ID, or studio"),
    district_id: Optional[uuid.UUID] = Query(None),
    taluka_id: Optional[uuid.UUID] = Query(None),
    member_status: Optional[MemberStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(
        require_roles(UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN, UserRole.TALUKA_ADMIN, UserRole.AUDITOR)
    ),
    db: AsyncSession = Depends(get_db),
):
    """Search member directory with geographic RBAC filtering."""
    # Enforce geographic scope for district/taluka admins
    if current_user.role == UserRole.DISTRICT_ADMIN:
        district_id = current_user.district_id
    elif current_user.role == UserRole.TALUKA_ADMIN:
        district_id = current_user.district_id
        taluka_id = current_user.taluka_id

    members, total = await MemberService.search_members(
        db=db,
        query=q,
        district_id=district_id,
        taluka_id=taluka_id,
        status_filter=member_status,
        page=page,
        page_size=page_size,
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse(
        success=True,
        data=[MemberRead.model_validate(m) for m in members],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{member_id}",
    response_model=APIResponse[MemberWithNomineesRead],
    summary="Get single member details (Admins only)",
)
async def get_member_details(
    member_id: uuid.UUID,
    current_user: User = Depends(
        require_roles(UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN, UserRole.TALUKA_ADMIN, UserRole.AUDITOR)
    ),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed member information."""
    member = await db.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    enforce_geo_scope(current_user, district_id=member.district_id, taluka_id=member.taluka_id)

    detailed_member = await MemberService.get_member_by_user(db, member.user_id)
    return APIResponse(
        success=True,
        message="Member details retrieved",
        data=MemberWithNomineesRead.model_validate(detailed_member),
    )


@router.post(
    "/{member_id}/approve",
    response_model=APIResponse[MemberRead],
    summary="Approve member registration and assign Membership ID",
)
async def approve_member(
    member_id: uuid.UUID,
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Approve member application, issue KPA-DIST-XXXXX ID, and activate user."""
    member = await db.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    enforce_geo_scope(current_user, district_id=member.district_id)

    approved = await MemberService.approve_member(db, member_id, current_user)
    return APIResponse(
        success=True,
        message="Member application approved successfully",
        data=MemberRead.model_validate(approved),
    )


@router.post(
    "/{member_id}/reject",
    response_model=APIResponse[MemberRead],
    summary="Reject member registration with reason",
)
async def reject_member(
    member_id: uuid.UUID,
    payload: MemberRejectionRequest,
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Reject member application."""
    member = await db.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    enforce_geo_scope(current_user, district_id=member.district_id)

    rejected = await MemberService.reject_member(db, member_id, current_user, payload.reason)
    return APIResponse(
        success=True,
        message="Member application rejected",
        data=MemberRead.model_validate(rejected),
    )
