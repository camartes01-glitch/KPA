"""
Member Service — Registration, Approvals, Sequential ID Generation, and Digital Cards with QR.
"""
import base64
import io
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

import qrcode
from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.geo import District, Taluka
from app.models.member import Member, MemberStatus, Nominee
from app.models.user import User, UserRole, UserStatus
from app.schemas.member import DigitalCardResponse, MemberRegisterRequest


class MemberService:
    @staticmethod
    async def register_member(
        db: AsyncSession,
        user: User,
        data: MemberRegisterRequest,
    ) -> Member:
        """Register a member profile with primary nominee."""
        # Check if already registered
        stmt = select(Member).where(Member.user_id == user.id)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Member profile already registered for this account",
            )

        # Verify district & taluka exist
        district = await db.get(District, data.district_id)
        taluka = await db.get(Taluka, data.taluka_id)
        if not district or not taluka:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid District or Taluka specified",
            )
        if taluka.district_id != district.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected Taluka does not belong to the selected District",
            )

        # Create member record
        member = Member(
            user_id=user.id,
            full_name=data.full_name,
            father_or_spouse_name=data.father_or_spouse_name,
            gender=data.gender,
            dob=data.dob,
            blood_group=data.blood_group,
            studio_name=data.studio_name,
            experience_years=data.experience_years,
            photo_url=data.photo_url,
            address_line=data.address_line,
            pincode=data.pincode,
            district_id=data.district_id,
            taluka_id=data.taluka_id,
            status=MemberStatus.PENDING,
        )
        db.add(member)
        await db.flush()

        # Create nominee
        nominee_data = data.nominee
        nominee = Nominee(
            member_id=member.id,
            name=nominee_data.name,
            relationship_to_member=nominee_data.relationship_to_member,
            phone=nominee_data.phone,
            dob=nominee_data.dob,
            aadhaar_last_4=nominee_data.aadhaar_last_4,
            bank_account_no=nominee_data.bank_account_no,
            bank_ifsc=nominee_data.bank_ifsc,
            bank_name=nominee_data.bank_name,
            is_primary=True,
        )
        db.add(nominee)

        # Update user name & geographic scopes
        user.name = data.full_name
        user.district_id = data.district_id
        user.taluka_id = data.taluka_id

        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def approve_member(
        db: AsyncSession,
        member_id: uuid.UUID,
        approver: User,
    ) -> Member:
        """Approve member application and generate unique Membership Number."""
        stmt = (
            select(Member)
            .where(Member.id == member_id)
            .options(selectinload(Member.district), selectinload(Member.user))
        )
        member = (await db.execute(stmt)).scalar_one_or_none()

        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        if member.status == MemberStatus.APPROVED:
            return member

        # Generate unique membership number: KPA-{DIST_CODE}-{SEQ:05d}
        dist_code = member.district.code.replace("_", "")
        count_stmt = select(func.count(Member.id)).where(
            Member.district_id == member.district_id,
            Member.status == MemberStatus.APPROVED,
        )
        approved_count = (await db.execute(count_stmt)).scalar() or 0
        seq = approved_count + 1
        membership_no = f"KPA-{dist_code}-{seq:05d}"

        # Setup digital card QR signature payload
        qr_payload = {
            "iss": "Karnataka Photography Association",
            "kpa_id": membership_no,
            "name": member.full_name,
            "district": member.district.name_en,
            "verified": True,
        }

        now = datetime.now(timezone.utc)
        member.membership_no = membership_no
        member.status = MemberStatus.APPROVED
        member.approved_by_id = approver.id
        member.approved_at = now
        member.id_card_qr_data = json.dumps(qr_payload)

        # Update user status to ACTIVE
        if member.user:
            member.user.status = UserStatus.ACTIVE

        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def reject_member(
        db: AsyncSession,
        member_id: uuid.UUID,
        approver: User,
        reason: str,
    ) -> Member:
        """Reject member registration with documented reason."""
        member = await db.get(Member, member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        member.status = MemberStatus.REJECTED
        member.approved_by_id = approver.id
        member.rejection_reason = reason

        await db.commit()
        await db.refresh(member)
        return member

    @staticmethod
    async def get_member_by_user(db: AsyncSession, user_id: uuid.UUID) -> Optional[Member]:
        """Fetch member profile for a user with nominees, district, and taluka."""
        stmt = (
            select(Member)
            .where(Member.user_id == user_id)
            .options(
                selectinload(Member.nominees),
                selectinload(Member.district),
                selectinload(Member.taluka),
            )
        )
        return (await db.execute(stmt)).scalar_one_or_none()

    @staticmethod
    async def search_members(
        db: AsyncSession,
        query: Optional[str] = None,
        district_id: Optional[uuid.UUID] = None,
        taluka_id: Optional[uuid.UUID] = None,
        status_filter: Optional[MemberStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Member], int]:
        """Search and filter members with pagination."""
        stmt = select(Member).options(
            selectinload(Member.district),
            selectinload(Member.taluka),
        )

        if query:
            stmt = stmt.where(
                or_(
                    Member.full_name.ilike(f"%{query}%"),
                    Member.membership_no.ilike(f"%{query}%"),
                    Member.studio_name.ilike(f"%{query}%"),
                )
            )
        if district_id:
            stmt = stmt.where(Member.district_id == district_id)
        if taluka_id:
            stmt = stmt.where(Member.taluka_id == taluka_id)
        if status_filter:
            stmt = stmt.where(Member.status == status_filter)

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        # Pagination
        stmt = stmt.order_by(Member.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        members = (await db.execute(stmt)).scalars().all()
        return members, total

    @staticmethod
    def generate_card_qr_base64(qr_data_str: str) -> str:
        """Render QR code to Base64 PNG image."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(qr_data_str)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0d3b66", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"

    @classmethod
    async def get_digital_card(
        cls,
        db: AsyncSession,
        member_id: uuid.UUID,
    ) -> DigitalCardResponse:
        """Return digital card payload with generated base64 QR code."""
        stmt = (
            select(Member)
            .where(Member.id == member_id)
            .options(selectinload(Member.district), selectinload(Member.taluka))
        )
        member = (await db.execute(stmt)).scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        if member.status != MemberStatus.APPROVED or not member.membership_no:
            raise HTTPException(
                status_code=400,
                detail="Digital card is only available for approved members",
            )

        qr_data = member.id_card_qr_data or f"kpa://verify/{member.membership_no}"
        qr_b64 = cls.generate_card_qr_base64(qr_data)

        issue_str = member.approved_at.strftime("%d-%m-%Y") if member.approved_at else "—"

        return DigitalCardResponse(
            membership_no=member.membership_no,
            member_name=member.full_name,
            district_name=member.district.name_en,
            taluka_name=member.taluka.name_en,
            blood_group=member.blood_group,
            status=member.status.value,
            issue_date=issue_str,
            qr_data=qr_data,
            qr_code_base64=qr_b64,
        )
