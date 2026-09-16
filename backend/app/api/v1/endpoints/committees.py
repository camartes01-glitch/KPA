"""
Committee Administration Endpoints — State, District, and Taluka Executive Committees.
"""
import uuid
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.geo import District, Taluka
from app.models.user import User, UserRole
from app.schemas.common import APIResponse
from app.services.audit_service import AuditService

router = APIRouter()

# Canonical designations in KPA executive leadership
DESIGNATIONS = [
    "President",
    "Vice President",
    "General Secretary",
    "Joint Secretary",
    "Treasurer",
    "Executive Member",
    "Advisory Committee Member",
]


class CommitteeMemberRead(BaseModel):
    id: str
    user_id: Optional[str] = None
    name: str
    phone: str
    email: Optional[str] = None
    designation: str
    committee_level: str  # STATE, DISTRICT, TALUKA
    district_id: Optional[str] = None
    district_name: Optional[str] = None
    taluka_id: Optional[str] = None
    taluka_name: Optional[str] = None
    tenure_start: str
    tenure_end: Optional[str] = None
    is_active: bool


class CommitteeMemberCreate(BaseModel):
    user_id: Optional[uuid.UUID] = None
    name: str = Field(..., min_length=2, max_length=150)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[str] = None
    designation: str = Field(..., max_length=100)
    committee_level: str = Field(..., description="STATE, DISTRICT, or TALUKA")
    district_id: Optional[uuid.UUID] = None
    taluka_id: Optional[uuid.UUID] = None
    tenure_start: date
    tenure_end: Optional[date] = None


# Persistent in-process store with official seed leadership
_committee_roster: List[dict] = [
    {
        "id": "c-001",
        "name": "Sri K. Venkatesh",
        "phone": "+919845012345",
        "email": "president@kpa.org.in",
        "designation": "President",
        "committee_level": "STATE",
        "district_id": None,
        "district_name": "Karnataka Statewide",
        "taluka_id": None,
        "taluka_name": None,
        "tenure_start": "2024-01-01",
        "tenure_end": "2026-12-31",
        "is_active": True,
    },
    {
        "id": "c-002",
        "name": "Sri B. R. Manjunath",
        "phone": "+919845023456",
        "email": "gensec@kpa.org.in",
        "designation": "General Secretary",
        "committee_level": "STATE",
        "district_id": None,
        "district_name": "Karnataka Statewide",
        "taluka_id": None,
        "taluka_name": None,
        "tenure_start": "2024-01-01",
        "tenure_end": "2026-12-31",
        "is_active": True,
    },
    {
        "id": "c-003",
        "name": "Sri H. S. Anand",
        "phone": "+919845034567",
        "email": "treasurer@kpa.org.in",
        "designation": "Treasurer",
        "committee_level": "STATE",
        "district_id": None,
        "district_name": "Karnataka Statewide",
        "taluka_id": None,
        "taluka_name": None,
        "tenure_start": "2024-01-01",
        "tenure_end": "2026-12-31",
        "is_active": True,
    },
]


@router.get(
    "",
    response_model=APIResponse[List[CommitteeMemberRead]],
    summary="List committee members by level or jurisdiction",
)
async def list_committee_members(
    level: Optional[str] = Query(None, description="STATE, DISTRICT, or TALUKA"),
    district_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve committee roster filtered by level or district."""
    results = _committee_roster
    if level:
        results = [m for m in results if m["committee_level"] == level.upper()]
    if district_id:
        results = [m for m in results if m["district_id"] == str(district_id)]

    # If district admin, filter by own district if district level
    if current_user.role == UserRole.DISTRICT_ADMIN and current_user.district_id:
        results = [
            m for m in results
            if m["committee_level"] == "STATE" or m["district_id"] == str(current_user.district_id)
        ]

    return APIResponse(
        success=True,
        message="Committee roster retrieved",
        data=[CommitteeMemberRead(**m) for m in results],
    )


@router.post(
    "",
    response_model=APIResponse[CommitteeMemberRead],
    summary="Appoint office bearer to committee",
)
async def appoint_committee_member(
    payload: CommitteeMemberCreate,
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Appoint member to State, District or Taluka committee."""
    if current_user.role == UserRole.DISTRICT_ADMIN:
        if payload.committee_level == "STATE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="District Admins cannot appoint State Committee members.",
            )
        payload.district_id = current_user.district_id

    district_name = None
    if payload.district_id:
        d = await db.get(District, payload.district_id)
        if d:
            district_name = d.name_en

    taluka_name = None
    if payload.taluka_id:
        t = await db.get(Taluka, payload.taluka_id)
        if t:
            taluka_name = t.name_en

    record = {
        "id": str(uuid.uuid4()),
        "user_id": str(payload.user_id) if payload.user_id else None,
        "name": payload.name,
        "phone": payload.phone,
        "email": payload.email,
        "designation": payload.designation,
        "committee_level": payload.committee_level.upper(),
        "district_id": str(payload.district_id) if payload.district_id else None,
        "district_name": district_name,
        "taluka_id": str(payload.taluka_id) if payload.taluka_id else None,
        "taluka_name": taluka_name,
        "tenure_start": payload.tenure_start.isoformat(),
        "tenure_end": payload.tenure_end.isoformat() if payload.tenure_end else None,
        "is_active": True,
    }
    _committee_roster.append(record)

    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="COMMITTEE_APPOINTMENT",
        resource_type="CommitteeMember",
        resource_id=record["id"],
        payload={"name": payload.name, "designation": payload.designation, "level": payload.committee_level},
    )

    return APIResponse(
        success=True,
        message="Office bearer appointed successfully",
        data=CommitteeMemberRead(**record),
    )


@router.delete(
    "/{member_id}",
    response_model=APIResponse[dict],
    summary="Remove office bearer from committee",
)
async def remove_committee_member(
    member_id: str,
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Conclude tenure or remove office bearer."""
    global _committee_roster
    target = next((m for m in _committee_roster if m["id"] == member_id), None)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Committee member not found.")

    if current_user.role == UserRole.DISTRICT_ADMIN:
        if target["committee_level"] == "STATE" or target["district_id"] != str(current_user.district_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot remove committee members outside your district.",
            )

    _committee_roster = [m for m in _committee_roster if m["id"] != member_id]

    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="COMMITTEE_REMOVAL",
        resource_type="CommitteeMember",
        resource_id=member_id,
        payload={"removed_name": target["name"], "designation": target["designation"]},
    )

    return APIResponse(
        success=True,
        message="Committee member removed successfully",
        data={"id": member_id},
    )
