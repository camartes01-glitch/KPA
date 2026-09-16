"""
Payment Endpoints — Order Creation, Signature Verification, Receipts, and Webhooks.
"""
import json
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.payment import PaymentStatus
from app.models.user import User
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.payment import (
    CreateOrderRequest,
    OrderResponse,
    PaymentReceiptRead,
    VerifyPaymentRequest,
)
from app.services.member_service import MemberService
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post(
    "/create-order",
    response_model=APIResponse[OrderResponse],
    summary="Create Razorpay order for welfare contribution",
)
async def create_payment_order(
    payload: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initiate gateway checkout order for the ₹10 welfare mutual debit."""
    member = await MemberService.get_member_by_user(db, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member profile not registered",
        )

    order = await PaymentService.create_contribution_order(
        db=db,
        member=member,
        contribution_id=payload.contribution_id,
    )
    return APIResponse(
        success=True,
        message="Order created successfully",
        data=order,
    )


@router.post(
    "/verify",
    response_model=APIResponse[PaymentReceiptRead],
    summary="Verify gateway signature and settle contribution",
)
async def verify_payment(
    payload: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify cryptographic HMAC signature, settle debit obligation, and issue official receipt."""
    member = await MemberService.get_member_by_user(db, current_user.id)
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")

    receipt = await PaymentService.verify_and_settle_payment(
        db=db,
        member=member,
        gateway_order_id=payload.gateway_order_id,
        gateway_payment_id=payload.gateway_payment_id,
        signature=payload.signature,
        actor_user=current_user,
    )
    return APIResponse(
        success=True,
        message="Payment verified and settled successfully",
        data=receipt,
    )


@router.get(
    "/receipts",
    response_model=PaginatedResponse[PaymentReceiptRead],
    summary="List official payment receipts with search and filters",
)
async def list_receipts(
    search: Optional[str] = Query(None, description="Search by receipt number, member name, or membership ID"),
    status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve paginated and filtered list of verified receipts."""
    receipts, total = await PaymentService.get_receipts(
        db=db,
        current_user=current_user,
        search=search,
        status_filter=status,
        page=page,
        page_size=page_size,
    )
    total_pages = max(1, math.ceil(total / page_size))
    return PaginatedResponse(
        success=True,
        data=receipts,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/receipt/{receipt_no}",
    response_model=APIResponse[PaymentReceiptRead],
    summary="Get official payment receipt",
)
async def get_receipt(
    receipt_no: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve receipt details by receipt number."""
    receipt = await PaymentService.get_receipt(db, receipt_no)
    return APIResponse(
        success=True,
        message="Receipt retrieved",
        data=receipt,
    )


@router.post(
    "/webhook",
    summary="Razorpay asynchronous webhook listener",
)
async def razorpay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Asynchronous webhook handler with cryptographic signature verification and idempotency."""
    signature = request.headers.get("X-Razorpay-Signature")
    raw_body = await request.body()
    try:
        event_payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    result = await PaymentService.process_webhook_event(
        db=db,
        raw_body=raw_body,
        signature=signature,
        event_payload=event_payload,
    )
    return {"status": "ok", "result": result}
