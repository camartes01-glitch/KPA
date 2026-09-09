"""
Audit Log Endpoints — Administrative and Security Compliance Inspection.
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.audit import AuditLogRead
from app.schemas.common import PaginatedResponse
from app.services.audit_service import AuditService

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[AuditLogRead],
    summary="List immutable system audit logs (STATE_HEAD / AUDITOR only)",
)
async def list_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action keyword"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    user_id: Optional[uuid.UUID] = Query(None, description="Filter by actor user ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD, UserRole.AUDITOR)),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve audit trail logs with filtering and pagination."""
    logs, total = await AuditService.get_logs(
        db=db,
        action=action,
        resource_type=resource_type,
        user_id=user_id,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse(
        success=True,
        data=[AuditLogRead.model_validate(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
