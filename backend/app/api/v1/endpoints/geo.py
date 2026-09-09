"""
Geographic Endpoints — Districts and Talukas across Karnataka.
"""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.common import APIResponse
from app.schemas.geo import DistrictCreate, DistrictRead, DistrictWithTalukasRead, TalukaCreate, TalukaRead
from app.services.geo_service import GeoService

router = APIRouter()


@router.get(
    "/districts",
    response_model=APIResponse[List[DistrictRead]],
    summary="List all Karnataka districts",
)
async def list_districts(
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all active districts in Karnataka."""
    districts = await GeoService.get_all_districts(db)
    return APIResponse(
        success=True,
        message="Districts retrieved successfully",
        data=[DistrictRead.model_validate(d) for d in districts],
    )


@router.get(
    "/districts/{district_id}",
    response_model=APIResponse[DistrictWithTalukasRead],
    summary="Get district with associated talukas",
)
async def get_district(
    district_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve district details and all contained talukas."""
    district = await GeoService.get_district_with_talukas(db, district_id)
    if not district:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="District not found",
        )
    return APIResponse(
        success=True,
        message="District details retrieved",
        data=DistrictWithTalukasRead.model_validate(district),
    )


@router.get(
    "/districts/{district_id}/talukas",
    response_model=APIResponse[List[TalukaRead]],
    summary="List talukas for a specific district",
)
async def list_talukas(
    district_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all talukas belonging to the specified district."""
    talukas = await GeoService.get_talukas_by_district(db, district_id)
    return APIResponse(
        success=True,
        message="Talukas retrieved successfully",
        data=[TalukaRead.model_validate(t) for t in talukas],
    )


@router.post(
    "/seed",
    response_model=APIResponse[dict],
    summary="Seed 31 Karnataka districts and administrative talukas",
)
async def seed_karnataka(
    db: AsyncSession = Depends(get_db),
):
    """Populate database with Karnataka official districts and talukas."""
    created = await GeoService.seed_karnataka_data(db)
    return APIResponse(
        success=True,
        message=f"Seeded {created} new districts with talukas",
        data={"districts_seeded": created},
    )


@router.post(
    "/districts",
    response_model=APIResponse[DistrictRead],
    summary="Create a district (STATE_HEAD only)",
)
async def create_district(
    payload: DistrictCreate,
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new district."""
    district = await GeoService.create_district(db, payload)
    return APIResponse(
        success=True,
        message="District created successfully",
        data=DistrictRead.model_validate(district),
    )


@router.post(
    "/talukas",
    response_model=APIResponse[TalukaRead],
    summary="Create a taluka (STATE_HEAD only)",
)
async def create_taluka(
    payload: TalukaCreate,
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new taluka."""
    taluka = await GeoService.create_taluka(db, payload)
    return APIResponse(
        success=True,
        message="Taluka created successfully",
        data=TalukaRead.model_validate(taluka),
    )
