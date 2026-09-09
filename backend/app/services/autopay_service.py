"""
AutoPay Service — eMandate Registration, State Transitions, and Recurring Batch Deduction Execution.
"""
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.autopay import AutoPayMandate, MandateStatus
from app.models.member import Member
from app.models.payment import Payment, PaymentStatus
from app.models.welfare import ContributionStatus, WelfareContribution, WelfareEvent
from app.schemas.autopay import BatchDebitSummaryRead, CreateMandateRequest
from app.services.welfare_service import WelfareService


class AutoPayService:
    @staticmethod
    async def create_mandate(
        db: AsyncSession,
        member: Member,
        data: CreateMandateRequest,
    ) -> AutoPayMandate:
        """Register a new recurring mandate for automatic mutual relief deductions."""
        # Check if already active
        stmt = select(AutoPayMandate).where(
            AutoPayMandate.member_id == member.id,
            AutoPayMandate.status == MandateStatus.ACTIVE,
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An active AutoPay mandate already exists for this member",
            )

        gateway_mandate_id = f"mandate_{secrets.token_hex(8)}"

        mandate = AutoPayMandate(
            member_id=member.id,
            gateway="RAZORPAY",
            gateway_mandate_id=gateway_mandate_id,
            auth_type=data.auth_type,
            max_amount=data.max_amount,
            status=MandateStatus.CREATED,
            vpa=data.vpa,
            bank_name=data.bank_name,
        )
        db.add(mandate)
        await db.commit()
        await db.refresh(mandate)
        return mandate

    @staticmethod
    async def activate_mandate(
        db: AsyncSession,
        member: Member,
        gateway_mandate_id: str,
    ) -> AutoPayMandate:
        """Confirm mandate authorization from bank/UPI."""
        stmt = select(AutoPayMandate).where(
            AutoPayMandate.member_id == member.id,
            AutoPayMandate.gateway_mandate_id == gateway_mandate_id,
        )
        mandate = (await db.execute(stmt)).scalar_one_or_none()
        if not mandate:
            raise HTTPException(status_code=404, detail="Mandate not found")

        mandate.status = MandateStatus.ACTIVE
        mandate.activated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(mandate)
        return mandate

    @staticmethod
    async def cancel_mandate(
        db: AsyncSession,
        member: Member,
        mandate_id: uuid.UUID,
    ) -> AutoPayMandate:
        """Revoke active AutoPay mandate."""
        mandate = await db.get(AutoPayMandate, mandate_id)
        if not mandate or mandate.member_id != member.id:
            raise HTTPException(status_code=404, detail="Mandate not found")

        mandate.status = MandateStatus.CANCELLED
        mandate.cancelled_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(mandate)
        return mandate

    @staticmethod
    async def get_active_mandate(
        db: AsyncSession,
        member_id: uuid.UUID,
    ) -> Optional[AutoPayMandate]:
        """Retrieve active mandate for a member."""
        stmt = select(AutoPayMandate).where(
            AutoPayMandate.member_id == member_id,
            AutoPayMandate.status == MandateStatus.ACTIVE,
        )
        return (await db.execute(stmt)).scalar_one_or_none()

    @classmethod
    async def execute_batch_recurring_debits(
        cls,
        db: AsyncSession,
        event_id: uuid.UUID,
    ) -> BatchDebitSummaryRead:
        """Batch debit all members with active AutoPay mandates for a welfare event."""
        event = await db.get(WelfareEvent, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Welfare event not found")

        # Find pending contributions for this event
        stmt = select(WelfareContribution).where(
            WelfareContribution.event_id == event_id,
            WelfareContribution.status == ContributionStatus.PENDING,
        )
        pending_contribs = (await db.execute(stmt)).scalars().all()

        total_eligible = len(pending_contribs)
        debited_count = 0
        total_amount = 0.0

        for contrib in pending_contribs:
            mandate = await cls.get_active_mandate(db, contrib.member_id)
            if mandate:
                receipt_no = f"AUTOPAY-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
                gateway_order_id = f"sub_order_{secrets.token_hex(8)}"
                gateway_payment_id = f"pay_auto_{secrets.token_hex(8)}"

                payment = Payment(
                    contribution_id=contrib.id,
                    member_id=contrib.member_id,
                    gateway="RAZORPAY",
                    gateway_order_id=gateway_order_id,
                    gateway_payment_id=gateway_payment_id,
                    amount=float(contrib.amount),
                    currency="INR",
                    status=PaymentStatus.CAPTURED,
                    payment_method="AUTOPAY",
                    receipt_no=receipt_no,
                )
                db.add(payment)

                await WelfareService.record_contribution_payment(
                    db=db,
                    contribution_id=contrib.id,
                    payment_method="AUTOPAY",
                )
                debited_count += 1
                total_amount += float(contrib.amount)

        await db.commit()

        return BatchDebitSummaryRead(
            event_id=event_id,
            total_eligible_members=total_eligible,
            autopay_active_count=debited_count,
            debited_count=debited_count,
            total_amount_debited=total_amount,
        )
