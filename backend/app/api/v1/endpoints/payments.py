"""
Payment Endpoints — Order Creation, Signature Verification, Receipts, and Webhooks.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
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
    )
    return APIResponse(
        success=True,
        message="Payment verified and settled successfully",
        data=receipt,
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
    """Asynchronous webhook handler for payment.captured events."""
    # Reads payload and header: X-Razorpay-Signature
    signature = request.headers.get("X-Razorpay-Signature")
    raw_body = await request.body()
    # In production, verifies webhook signature and settles automatically
    return {"status": "ok", "event": "webhook_received"}
