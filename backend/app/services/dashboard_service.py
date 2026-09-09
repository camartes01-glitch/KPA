"""
Dashboard Service — Role-Aware Aggregated Metrics and Analytical Summaries.
"""
from datetime import datetime, timezone
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.autopay import AutoPayMandate, MandateStatus
from app.models.geo import District
from app.models.member import Member, MemberStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User, UserRole
from app.models.welfare import ContributionStatus, WelfareContribution, WelfareEvent, WelfareEventStatus
from app.schemas.dashboard import DashboardMetricsRead, DistrictMetricItem


class DashboardService:
    @staticmethod
    async def get_metrics(
        db: AsyncSession,
        user: User,
    ) -> DashboardMetricsRead:
        """Calculate role-scoped live metrics for dashboard view."""
        # 1. Base Member Counts
        m_stmt = select(func.count(Member.id))
        appr_stmt = select(func.count(Member.id)).where(Member.status == MemberStatus.APPROVED)
        pend_stmt = select(func.count(Member.id)).where(Member.status == MemberStatus.PENDING)

        # Apply geographic role scoping
        if user.role == UserRole.DISTRICT_ADMIN:
            m_stmt = m_stmt.where(Member.district_id == user.district_id)
            appr_stmt = appr_stmt.where(Member.district_id == user.district_id)
            pend_stmt = pend_stmt.where(Member.district_id == user.district_id)
        elif user.role == UserRole.TALUKA_ADMIN:
            m_stmt = m_stmt.where(Member.taluka_id == user.taluka_id)
            appr_stmt = appr_stmt.where(Member.taluka_id == user.taluka_id)
            pend_stmt = pend_stmt.where(Member.taluka_id == user.taluka_id)

        total_members = (await db.execute(m_stmt)).scalar() or 0
        active_members = (await db.execute(appr_stmt)).scalar() or 0
        pending_approvals = (await db.execute(pend_stmt)).scalar() or 0

        # 2. Welfare Events
        w_stmt = select(func.count(WelfareEvent.id)).where(WelfareEvent.status == WelfareEventStatus.ACTIVE)
        active_welfare_events = (await db.execute(w_stmt)).scalar() or 0

        target_stmt = select(func.sum(WelfareEvent.target_amount)).where(
            WelfareEvent.status == WelfareEventStatus.ACTIVE
        )
        total_welfare_target = float((await db.execute(target_stmt)).scalar() or 0.0)

        # 3. Financial Collections
        pay_stmt = select(func.sum(Payment.amount)).where(Payment.status == PaymentStatus.CAPTURED)
        total_collected = float((await db.execute(pay_stmt)).scalar() or 0.0)

        # 4. Pending Dues
        due_stmt = select(func.sum(WelfareContribution.amount)).where(
            WelfareContribution.status == ContributionStatus.PENDING
        )
        if user.role == UserRole.DISTRICT_ADMIN:
            due_stmt = due_stmt.join(Member, WelfareContribution.member_id == Member.id).where(
                Member.district_id == user.district_id
            )
        elif user.role == UserRole.TALUKA_ADMIN:
            due_stmt = due_stmt.join(Member, WelfareContribution.member_id == Member.id).where(
                Member.taluka_id == user.taluka_id
            )
        total_pending_dues = float((await db.execute(due_stmt)).scalar() or 0.0)

        # 5. AutoPay Mandates
        auto_stmt = select(func.count(AutoPayMandate.id)).where(
            AutoPayMandate.status == MandateStatus.ACTIVE
        )
        autopay_active_members = (await db.execute(auto_stmt)).scalar() or 0

        # 6. District breakdown (for STATE_HEAD)
        district_breakdown = []
        if user.role == UserRole.STATE_HEAD:
            districts = (await db.execute(select(District).order_by(District.name_en))).scalars().all()
            for d in districts[:6]:  # top districts summary
                d_total = (
                    await db.execute(select(func.count(Member.id)).where(Member.district_id == d.id))
                ).scalar() or 0
                d_appr = (
                    await db.execute(
                        select(func.count(Member.id)).where(
                            Member.district_id == d.id, Member.status == MemberStatus.APPROVED
                        )
                    )
                ).scalar() or 0
                district_breakdown.append(
                    DistrictMetricItem(
                        district_name=d.name_en,
                        total_members=d_total,
                        approved_members=d_appr,
                        total_collected=0.0,
                        pending_dues=0.0,
                    )
                )

        return DashboardMetricsRead(
            total_members=total_members,
            active_members=active_members,
            pending_approvals=pending_approvals,
            active_welfare_events=active_welfare_events,
            total_welfare_target=total_welfare_target,
            total_collected_today=total_collected,
            total_collected_monthly=total_collected,
            total_pending_dues=total_pending_dues,
            autopay_active_members=autopay_active_members,
            district_breakdown=district_breakdown if user.role == UserRole.STATE_HEAD else None,
        )
