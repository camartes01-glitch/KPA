"""
Welfare Service — Event Creation, Idempotent Contribution Batch Generation, and Ledger Tracking.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.member import Member, MemberStatus
from app.models.user import User
from app.models.welfare import ContributionStatus, WelfareContribution, WelfareEvent, WelfareEventStatus
from app.schemas.welfare import WelfareEventCreate, WelfareObligationRead


class WelfareService:
    @staticmethod
    async def create_welfare_event(
        db: AsyncSession,
        creator: User,
        data: WelfareEventCreate,
    ) -> WelfareEvent:
        """Create a welfare event and generate idempotent ₹10 contributions for all active members."""
        # Validate deceased member
        deceased = await db.get(Member, data.deceased_member_id)
        if not deceased:
            raise HTTPException(status_code=404, detail="Deceased member not found")
        if deceased.status != MemberStatus.APPROVED:
            raise HTTPException(
                status_code=400,
                detail="Welfare events can only be created for approved members",
            )

        # Check if an active event already exists for this member
        existing_stmt = select(WelfareEvent).where(
            WelfareEvent.deceased_member_id == data.deceased_member_id,
        )
        existing = (await db.execute(existing_stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="A welfare event has already been registered for this member",
            )

        # Mark deceased member status as suspended / deceased
        deceased.status = MemberStatus.SUSPENDED

        # Create event
        event = WelfareEvent(
            deceased_member_id=data.deceased_member_id,
            title=data.title,
            death_date=data.death_date,
            cause_of_death=data.cause_of_death,
            death_certificate_url=data.death_certificate_url,
            target_amount=0.00,
            collected_amount=0.00,
            status=WelfareEventStatus.ACTIVE,
            created_by_id=creator.id,
        )
        db.add(event)
        await db.flush()

        # Query all approved members excluding the deceased
        stmt = select(Member.id).where(
            Member.status == MemberStatus.APPROVED,
            Member.id != data.deceased_member_id,
        )
        eligible_member_ids = (await db.execute(stmt)).scalars().all()

        # Batch insert ₹10 contributions
        contributions = []
        for m_id in eligible_member_ids:
            contributions.append(
                WelfareContribution(
                    event_id=event.id,
                    member_id=m_id,
                    amount=10.00,
                    status=ContributionStatus.PENDING,
                )
            )

        if contributions:
            db.add_all(contributions)

        event.target_amount = float(len(eligible_member_ids) * 10.0)

        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def get_events(
        db: AsyncSession,
        status_filter: Optional[WelfareEventStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[WelfareEvent], int]:
        """Fetch paginated welfare events."""
        stmt = select(WelfareEvent)
        if status_filter:
            stmt = stmt.where(WelfareEvent.status == status_filter)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = stmt.order_by(WelfareEvent.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        events = (await db.execute(stmt)).scalars().all()
        return events, total

    @staticmethod
    async def get_event_by_id(db: AsyncSession, event_id: uuid.UUID) -> Optional[WelfareEvent]:
        """Fetch single event with deceased member details."""
        stmt = (
            select(WelfareEvent)
            .where(WelfareEvent.id == event_id)
            .options(selectinload(WelfareEvent.deceased_member))
        )
        return (await db.execute(stmt)).scalar_one_or_none()

    @staticmethod
    async def get_member_obligations(
        db: AsyncSession,
        member_id: uuid.UUID,
    ) -> List[WelfareObligationRead]:
        """Fetch pending and past ₹10 contribution obligations for a member."""
        stmt = (
            select(WelfareContribution)
            .where(WelfareContribution.member_id == member_id)
            .options(
                selectinload(WelfareContribution.event).selectinload(WelfareEvent.deceased_member)
            )
            .order_by(WelfareContribution.created_at.desc())
        )
        contributions = (await db.execute(stmt)).scalars().all()

        obligations = []
        for c in contributions:
            obligations.append(
                WelfareObligationRead(
                    contribution_id=c.id,
                    event_id=c.event_id,
                    event_title=c.event.title,
                    deceased_member_name=c.event.deceased_member.full_name,
                    amount=float(c.amount),
                    status=c.status,
                    created_at=c.created_at,
                )
            )
        return obligations

    @staticmethod
    async def record_contribution_payment(
        db: AsyncSession,
        contribution_id: uuid.UUID,
        payment_method: str = "MANUAL_UPI",
    ) -> WelfareContribution:
        """Mark contribution paid and increment event collected amount."""
        contrib = await db.get(WelfareContribution, contribution_id)
        if not contrib:
            raise HTTPException(status_code=404, detail="Contribution record not found")
        if contrib.status == ContributionStatus.SUCCESS:
            return contrib

        now = datetime.now(timezone.utc)
        contrib.status = ContributionStatus.SUCCESS
        contrib.payment_method = payment_method
        contrib.paid_at = now

        # Increment event collected amount
        event = await db.get(WelfareEvent, contrib.event_id)
        if event:
            event.collected_amount = float(event.collected_amount) + float(contrib.amount)

        await db.commit()
        await db.refresh(contrib)
        return contrib
