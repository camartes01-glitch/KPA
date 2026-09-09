"""
Reports Endpoints — CSV and Tabular Master Data Export.
"""
import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.user import User, UserRole
from app.services.report_service import ReportService

router = APIRouter()


@router.get(
    "/members/csv",
    summary="Export member directory as CSV",
)
async def export_members_csv(
    current_user: User = Depends(
        require_roles(UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN, UserRole.TALUKA_ADMIN, UserRole.AUDITOR)
    ),
    db: AsyncSession = Depends(get_db),
):
    """Download full membership master roll formatted as CSV."""
    csv_content = await ReportService.export_members_csv(db, current_user)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="kpa_members_export.csv"'},
    )


@router.get(
    "/welfare/{event_id}/csv",
    summary="Export welfare event contribution ledger as CSV",
)
async def export_welfare_ledger_csv(
    event_id: uuid.UUID,
    current_user: User = Depends(
        require_roles(UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN, UserRole.AUDITOR)
    ),
    db: AsyncSession = Depends(get_db),
):
    """Download contribution debit obligations ledger for an event."""
    csv_content = await ReportService.export_welfare_ledger_csv(db, event_id, current_user)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="welfare_event_{event_id}_ledger.csv"'},
    )


@router.get(
    "/financial/csv",
    summary="Export financial transaction statement as CSV",
)
async def export_financial_audit_csv(
    current_user: User = Depends(
        require_roles(UserRole.STATE_HEAD, UserRole.AUDITOR)
    ),
    db: AsyncSession = Depends(get_db),
):
    """Download audited transaction logs formatted as CSV."""
    csv_content = await ReportService.export_financial_audit_csv(db, current_user)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="kpa_financial_audit_statement.csv"'},
    )
