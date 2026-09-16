"""
Payment Service — Razorpay Order Creation, HMAC SHA-256 Signature Verification,
Asynchronous Webhook Settlement, and Receipts Management.
"""
import hashlib
import hmac
import logging
import math
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.member import Member
from app.models.payment import Payment, PaymentStatus
from app.models.user import User, UserRole
from app.models.welfare import ContributionStatus, WelfareContribution, WelfareEvent
from app.schemas.payment import OrderResponse, PaymentReceiptRead
from app.services.audit_service import AuditService
from app.services.welfare_service import WelfareService

logger = logging.getLogger(__name__)

# Initialize Razorpay Client conditionally
razorpay_client = None
if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
    try:
        import razorpay
        razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        logger.info("Razorpay Client initialized with configured credentials.")
    except Exception as e:
        logger.error(f"Failed to initialize Razorpay Client: {e}")


class PaymentService:
    @staticmethod
    def verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
        """Verify Razorpay payment signature using HMAC SHA256."""
        secret = settings.RAZORPAY_KEY_SECRET or "dev-secret-key"
        msg = f"{order_id}|{payment_id}".encode("utf-8")
        generated_signature = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        return hmac.compare_digest(generated_signature, signature)

    @staticmethod
    def verify_webhook_signature(raw_body: bytes, signature: str) -> bool:
        """Verify Razorpay webhook signature header X-Razorpay-Signature."""
        secret = settings.RAZORPAY_WEBHOOK_SECRET or settings.RAZORPAY_KEY_SECRET or "dev-webhook-secret"
        generated_signature = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(generated_signature, signature)

    @classmethod
    async def create_contribution_order(
        cls,
        db: AsyncSession,
        member: Member,
        contribution_id: uuid.UUID,
    ) -> OrderResponse:
        """Create a payment gateway order for a ₹10 welfare contribution."""
        contrib = await db.get(WelfareContribution, contribution_id)
        if not contrib:
            raise HTTPException(status_code=404, detail="Contribution obligation not found")
        if contrib.member_id != member.id:
            raise HTTPException(status_code=403, detail="Cannot pay for another member's obligation")
        if contrib.status == ContributionStatus.SUCCESS:
            raise HTTPException(status_code=400, detail="Contribution is already paid")

        amount_inr = float(contrib.amount)
        amount_paise = int(amount_inr * 100)

        # Generate unique receipt number
        receipt_no = f"RCP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"

        gateway_order_id: str
        if razorpay_client:
            try:
                order_params = {
                    "amount": amount_paise,
                    "currency": "INR",
                    "receipt": receipt_no,
                    "notes": {
                        "member_id": str(member.id),
                        "contribution_id": str(contribution_id),
                        "membership_no": member.membership_no or "",
                    },
                }
                rzp_order = razorpay_client.order.create(order_params)
                gateway_order_id = rzp_order["id"]
                logger.info(f"Created real Razorpay order {gateway_order_id} for contribution {contribution_id}")
            except Exception as e:
                logger.error(f"Error creating Razorpay order: {e}")
                if settings.is_production:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Payment gateway communication failure",
                    )
                gateway_order_id = f"order_{secrets.token_hex(8)}"
        else:
            if settings.is_production:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Razorpay credentials not configured in production",
                )
            gateway_order_id = f"order_{secrets.token_hex(8)}"
            logger.warning(f"Using sandbox simulated order {gateway_order_id}")

        payment = Payment(
            contribution_id=contrib.id,
            member_id=member.id,
            gateway="RAZORPAY",
            gateway_order_id=gateway_order_id,
            amount=amount_inr,
            currency="INR",
            status=PaymentStatus.CREATED,
            receipt_no=receipt_no,
        )
        db.add(payment)
        await db.commit()

        return OrderResponse(
            order_id=gateway_order_id,
            amount=amount_inr,
            amount_paise=amount_paise,
            currency="INR",
            receipt_no=receipt_no,
            key_id=settings.RAZORPAY_KEY_ID or "rzp_test_kpa_sandbox",
        )

    @classmethod
    async def verify_and_settle_payment(
        cls,
        db: AsyncSession,
        member: Member,
        gateway_order_id: str,
        gateway_payment_id: str,
        signature: str,
        actor_user: Optional[User] = None,
    ) -> PaymentReceiptRead:
        """Verify HMAC signature, settle payment with row-level locking, update ledger, and return receipt."""
        stmt = (
            select(Payment)
            .where(Payment.gateway_order_id == gateway_order_id)
            .with_for_update()
            .options(
                selectinload(Payment.member),
                selectinload(Payment.contribution).selectinload(WelfareContribution.event),
            )
        )
        payment = (await db.execute(stmt)).scalar_one_or_none()

        if not payment:
            raise HTTPException(status_code=404, detail="Order not found")
        if payment.member_id != member.id:
            raise HTTPException(status_code=403, detail="Unauthorized access to order")
        if payment.status == PaymentStatus.CAPTURED:
            # Idempotent response if already settled
            return cls._build_receipt_read(payment)

        # Signature verification
        is_valid = cls.verify_razorpay_signature(gateway_order_id, gateway_payment_id, signature)
        allow_mock = not settings.is_production and signature == "mock-valid-signature"

        if not is_valid and not allow_mock:
            payment.status = PaymentStatus.FAILED
            payment.error_description = "Invalid gateway signature"
            await db.commit()
            if actor_user:
                await AuditService.log_action(
                    db=db,
                    action="PAYMENT_VERIFICATION_FAILED",
                    resource_type="PAYMENT",
                    resource_id=str(payment.id),
                    user_id=actor_user.id,
                    payload={"order_id": gateway_order_id, "payment_id": gateway_payment_id},
                )
            raise HTTPException(status_code=400, detail="Invalid payment signature")

        # Settle payment
        payment.status = PaymentStatus.CAPTURED
        payment.gateway_payment_id = gateway_payment_id
        payment.signature = signature
        payment.payment_method = "UPI_RAZORPAY"

        # Update welfare ledger
        if payment.contribution_id:
            await WelfareService.record_contribution_payment(
                db=db,
                contribution_id=payment.contribution_id,
                payment_method="UPI_RAZORPAY",
            )

        await db.commit()

        # Record audit log
        user_id = actor_user.id if actor_user else member.user_id
        await AuditService.log_action(
            db=db,
            action="PAYMENT_SETTLED",
            resource_type="PAYMENT",
            resource_id=str(payment.id),
            user_id=user_id,
            payload={
                "order_id": gateway_order_id,
                "payment_id": gateway_payment_id,
                "amount": float(payment.amount),
                "receipt_no": payment.receipt_no,
            },
        )

        return await cls.get_receipt(db, payment.receipt_no)

    @classmethod
    async def process_webhook_event(
        cls,
        db: AsyncSession,
        raw_body: bytes,
        signature: Optional[str],
        event_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Process asynchronous Razorpay webhook events with signature validation and idempotency."""
        # 1. Validate signature
        if not signature:
            logger.warning("Webhook received without X-Razorpay-Signature header.")
            raise HTTPException(status_code=400, detail="Missing webhook signature")

        if not cls.verify_webhook_signature(raw_body, signature):
            # Allow dev bypass strictly in non-production if configured
            if settings.is_production or signature != "dev-mock-webhook-signature":
                logger.error("Invalid Razorpay webhook signature.")
                raise HTTPException(status_code=400, detail="Invalid webhook signature")

        event_type = event_payload.get("event")
        payload = event_payload.get("payload", {})

        if event_type == "payment.captured":
            payment_entity = payload.get("payment", {}).get("entity", {})
            gateway_order_id = payment_entity.get("order_id")
            gateway_payment_id = payment_entity.get("id")

            if not gateway_order_id:
                return {"status": "ignored", "reason": "no_order_id"}

            stmt = (
                select(Payment)
                .where(Payment.gateway_order_id == gateway_order_id)
                .with_for_update()
            )
            payment = (await db.execute(stmt)).scalar_one_or_none()
            if not payment:
                logger.warning(f"Webhook payment.captured: order {gateway_order_id} not found")
                return {"status": "not_found"}

            if payment.status == PaymentStatus.CAPTURED:
                logger.info(f"Webhook payment.captured: order {gateway_order_id} already settled")
                return {"status": "already_settled"}

            payment.status = PaymentStatus.CAPTURED
            payment.gateway_payment_id = gateway_payment_id
            payment.payment_method = payment_entity.get("method", "RAZORPAY_WEBHOOK")

            if payment.contribution_id:
                await WelfareService.record_contribution_payment(
                    db=db,
                    contribution_id=payment.contribution_id,
                    payment_method="RAZORPAY_WEBHOOK",
                )

            await db.commit()

            await AuditService.log_action(
                db=db,
                action="WEBHOOK_PAYMENT_CAPTURED",
                resource_type="PAYMENT",
                resource_id=str(payment.id),
                payload={"order_id": gateway_order_id, "payment_id": gateway_payment_id},
            )
            return {"status": "settled", "payment_id": str(payment.id)}

        elif event_type == "payment.failed":
            payment_entity = payload.get("payment", {}).get("entity", {})
            gateway_order_id = payment_entity.get("order_id")
            if gateway_order_id:
                stmt = select(Payment).where(Payment.gateway_order_id == gateway_order_id).with_for_update()
                payment = (await db.execute(stmt)).scalar_one_or_none()
                if payment and payment.status != PaymentStatus.CAPTURED:
                    payment.status = PaymentStatus.FAILED
                    payment.error_description = payment_entity.get("error_description", "Payment failed at gateway")
                    await db.commit()
                    await AuditService.log_action(
                        db=db,
                        action="WEBHOOK_PAYMENT_FAILED",
                        resource_type="PAYMENT",
                        resource_id=str(payment.id),
                        payload={"order_id": gateway_order_id},
                    )

            return {"status": "recorded_failure"}

        return {"status": "unhandled_event", "event": event_type}

    @staticmethod
    def _build_receipt_read(payment: Payment) -> PaymentReceiptRead:
        event_title = None
        if payment.contribution and payment.contribution.event:
            event_title = payment.contribution.event.title

        return PaymentReceiptRead(
            id=payment.id,
            receipt_no=payment.receipt_no,
            amount=float(payment.amount),
            currency=payment.currency,
            status=payment.status,
            payment_method=payment.payment_method,
            gateway_order_id=payment.gateway_order_id,
            gateway_payment_id=payment.gateway_payment_id,
            member_name=payment.member.full_name if payment.member else "Unknown",
            membership_no=payment.member.membership_no if payment.member else None,
            event_title=event_title,
            paid_at=payment.updated_at if payment.status == PaymentStatus.CAPTURED else None,
            created_at=payment.created_at,
        )

    @classmethod
    async def get_receipt(cls, db: AsyncSession, receipt_no: str) -> PaymentReceiptRead:
        """Fetch receipt by receipt number."""
        stmt = (
            select(Payment)
            .where(Payment.receipt_no == receipt_no)
            .options(
                selectinload(Payment.member),
                selectinload(Payment.contribution).selectinload(WelfareContribution.event),
            )
        )
        payment = (await db.execute(stmt)).scalar_one_or_none()
        if not payment:
            raise HTTPException(status_code=404, detail="Receipt not found")
        return cls._build_receipt_read(payment)

    @classmethod
    async def get_receipts(
        cls,
        db: AsyncSession,
        current_user: User,
        search: Optional[str] = None,
        status_filter: Optional[PaymentStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[PaymentReceiptRead], int]:
        """Fetch paginated, filtered list of official receipts scoped by user permissions."""
        stmt = (
            select(Payment)
            .join(Payment.member)
            .options(
                selectinload(Payment.member),
                selectinload(Payment.contribution).selectinload(WelfareContribution.event),
            )
        )

        # Scoping
        if current_user.role == UserRole.MEMBER:
            stmt = stmt.where(Payment.member_id == current_user.id)
        elif current_user.role == UserRole.DISTRICT_ADMIN and current_user.district_id:
            stmt = stmt.where(Member.district_id == current_user.district_id)
        elif current_user.role == UserRole.TALUKA_ADMIN and current_user.taluka_id:
            stmt = stmt.where(Member.taluka_id == current_user.taluka_id)

        if status_filter:
            stmt = stmt.where(Payment.status == status_filter)

        if search:
            search_pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Payment.receipt_no.ilike(search_pattern),
                    Member.full_name.ilike(search_pattern),
                    Member.membership_no.ilike(search_pattern),
                    Payment.gateway_order_id.ilike(search_pattern),
                )
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = stmt.order_by(Payment.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        payments = (await db.execute(stmt)).scalars().all()

        results = [cls._build_receipt_read(p) for p in payments]
        return results, total
