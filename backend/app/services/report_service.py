"""
Report Service — CSV & Tabular Data Export Generation for Members, Welfare, and Audit Statements.
"""
import csv
import io
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.member import Member
from app.models.payment import Payment, PaymentStatus
from app.models.user import User, UserRole
from app.models.welfare import WelfareContribution, WelfareEvent


class ReportService:
    @staticmethod
    async def export_members_csv(db: AsyncSession, user: User) -> str:
        """Export member directory as CSV."""
        stmt = select(Member).options(selectinload(Member.district), selectinload(Member.taluka))

        if user.role == UserRole.DISTRICT_ADMIN:
            stmt = stmt.where(Member.district_id == user.district_id)
        elif user.role == UserRole.TALUKA_ADMIN:
            stmt = stmt.where(Member.taluka_id == user.taluka_id)

        members = (await db.execute(stmt)).scalars().all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Membership No",
            "Full Name",
            "Gender",
            "Studio Name",
            "District",
            "Taluka",
            "Status",
            "Registration Date",
        ])

        for m in members:
            writer.writerow([
                m.membership_no or "PENDING",
                m.full_name,
                m.gender,
                m.studio_name or "—",
                m.district.name_en if m.district else "—",
                m.taluka.name_en if m.taluka else "—",
                m.status.value,
                m.created_at.strftime("%Y-%m-%d"),
            ])

        return output.getvalue()

    @staticmethod
    async def export_welfare_ledger_csv(
        db: AsyncSession,
        event_id: uuid.UUID,
        user: User,
    ) -> str:
        """Export welfare contribution ledger for an event as CSV."""
        stmt = (
            select(WelfareContribution)
            .where(WelfareContribution.event_id == event_id)
            .options(
                selectinload(WelfareContribution.member).selectinload(Member.district),
                selectinload(WelfareContribution.event),
            )
        )
        contributions = (await db.execute(stmt)).scalars().all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Contribution ID",
            "Member Name",
            "Membership No",
            "District",
            "Amount (INR)",
            "Status",
            "Payment Method",
            "Paid At",
        ])

        for c in contributions:
            writer.writerow([
                str(c.id),
                c.member.full_name if c.member else "—",
                c.member.membership_no if c.member else "—",
                c.member.district.name_en if c.member and c.member.district else "—",
                float(c.amount),
                c.status.value,
                c.payment_method or "—",
                c.paid_at.strftime("%Y-%m-%d %H:%M") if c.paid_at else "—",
            ])

        return output.getvalue()

    @staticmethod
    async def export_financial_audit_csv(db: AsyncSession, user: User) -> str:
        """Export financial payments transaction history as CSV."""
        stmt = select(Payment).options(
            selectinload(Payment.member),
            selectinload(Payment.contribution).selectinload(WelfareContribution.event),
        )
        payments = (await db.execute(stmt)).scalars().all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Receipt No",
            "Member Name",
            "Membership No",
            "Event Title",
            "Amount (INR)",
            "Gateway",
            "Order ID",
            "Payment ID",
            "Status",
            "Timestamp",
        ])

        for p in payments:
            event_title = "—"
            if p.contribution and p.contribution.event:
                event_title = p.contribution.event.title

            writer.writerow([
                p.receipt_no,
                p.member.full_name if p.member else "—",
                p.member.membership_no if p.member else "—",
                event_title,
                float(p.amount),
                p.gateway,
                p.gateway_order_id,
                p.gateway_payment_id or "—",
                p.status.value,
                p.created_at.strftime("%Y-%m-%d %H:%M"),
            ])

        return output.getvalue()
