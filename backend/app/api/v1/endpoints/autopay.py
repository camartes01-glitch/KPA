"""
AutoPay Endpoints — eMandate Registration, Activation, Revocation, and Recurring Batch Deduction Execution.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.autopay import (
    ActivateMandateRequest,
    BatchDebitSummaryRead,
    CreateMandateRequest,
    MandateRead,
)
from app.schemas.common import APIResponse
from app.services.autopay_service import AutoPayService
from app.services.member_service import MemberService

router = APIRouter()


@router.post(
    "/mandate/create",
    response_model=APIResponse[MandateRead],
    summary="Register recurring AutoPay mandate",
)
async def create_mandate(
    payload: CreateMandateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initiate AutoPay eMandate for automatic ₹10 welfare mutual deductions."""
    member = await MemberService.get_member_by_user(db, current_user.id)
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")

    mandate = await AutoPayService.create_mandate(db, member, payload)
    return APIResponse(
        success=True,
        message="AutoPay mandate created and pending authorization",
        data=MandateRead.model_validate(mandate),
    )


@router.post(
    "/mandate/activate",
    response_model=APIResponse[MandateRead],
    summary="Activate AutoPay mandate upon gateway verification",
)
async def activate_mandate(
    payload: ActivateMandateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Confirm bank/UPI mandate authorization."""
    member = await MemberService.get_member_by_user(db, current_user.id)
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")

    mandate = await AutoPayService.activate_mandate(db, member, payload.gateway_mandate_id)
    return APIResponse(
        success=True,
        message="AutoPay mandate activated successfully",
        data=MandateRead.model_validate(mandate),
    )


@router.get(
    "/my-mandate",
    response_model=APIResponse[MandateRead],
    summary="Get current member's active AutoPay mandate",
)
async def get_my_mandate(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve active mandate details."""
    member = await MemberService.get_member_by_user(db, current_user.id)
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")

    mandate = await AutoPayService.get_active_mandate(db, member.id)
    if not mandate:
        raise HTTPException(status_code=404, detail="No active AutoPay mandate found")

    return APIResponse(
        success=True,
        message="Active mandate retrieved",
        data=MandateRead.model_validate(mandate),
    )


@router.post(
    "/mandate/{mandate_id}/cancel",
    response_model=APIResponse[MandateRead],
    summary="Cancel active AutoPay mandate",
)
async def cancel_mandate(
    mandate_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke recurring mandate."""
    member = await MemberService.get_member_by_user(db, current_user.id)
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")

    mandate = await AutoPayService.cancel_mandate(db, member, mandate_id)
    return APIResponse(
        success=True,
        message="AutoPay mandate cancelled successfully",
        data=MandateRead.model_validate(mandate),
    )


@router.post(
    "/batch-debit/{event_id}",
    response_model=APIResponse[BatchDebitSummaryRead],
    summary="Execute automated AutoPay batch deductions for event (STATE_HEAD only)",
)
async def execute_batch_debit(
    event_id: uuid.UUID,
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD)),
    db: AsyncSession = Depends(get_db),
):
    """Trigger automated ₹10 deductions across all members with active AutoPay mandates."""
    summary = await AutoPayService.execute_batch_recurring_debits(db, event_id)
    return APIResponse(
        success=True,
        message="AutoPay batch deduction completed",
        data=summary,
    )
