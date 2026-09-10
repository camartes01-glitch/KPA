"""
KPA Welfare Management System -- DEVELOPMENT DEMO SEED SCRIPT
==============================================================
Seeds four demo admin/member accounts plus realistic demo data so
every role and workflow can be experienced locally.

WARNING: DEVELOPMENT / DEMO USE ONLY
    This script:
      - Is guarded to refuse to run if APP_ENV == "production"
      - Creates accounts that ONLY work in development (fixed OTP)
      - Contains NO real personal information
      - Should NEVER be run against a production database

Demo accounts created (all use OTP: 123456 in dev mode):
  9900000001  STATE_HEAD       -- Full state-level administration
  9900000002  DISTRICT_ADMIN   -- Bengaluru Urban district scope
  9900000003  TALUKA_ADMIN     -- Bengaluru North taluka scope
  9900000004  MEMBER           -- Individual member experience

Usage:
    cd D:\\KPA\\backend
    python -m scripts.seed_demo

Requirements:
    - .env configured (APP_ENV=development, DATABASE_URL=sqlite+aiosqlite:///./kpa_dev.db)
    - Dependencies installed (pip install -r requirements.txt)
"""

import asyncio
import io
import os
import sys
from datetime import date, datetime, timezone, timedelta

# Force UTF-8 on Windows terminals (needed for Kannada notification text)
if hasattr(sys.stdout, "buffer") and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Ensure backend root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole, UserStatus
from app.models.member import Member, MemberStatus, Nominee
from app.models.geo import District, Taluka
from app.models.welfare import WelfareEvent, WelfareContribution, WelfareEventStatus, ContributionStatus
from app.models.payment import Payment, PaymentStatus
from app.models.notification import Notification, NotificationChannel, NotificationType


# ---------------------------------------------------------------------------
# Safety guard -- never run against production
# ---------------------------------------------------------------------------
def _check_not_production():
    if settings.is_production:
        print("\n[ABORT] seed_demo.py MUST NOT be run in production.")
        print("  Set APP_ENV=development in your .env file.")
        sys.exit(1)
    print(f"[OK] Environment: {settings.APP_ENV} -- safe to seed demo data.")


# ---------------------------------------------------------------------------
# Demo account definitions
# ---------------------------------------------------------------------------
DEMO_ACCOUNTS = [
    {
        "phone": "+919900000001",
        "name": "[DEMO] Rajesh Kumar - State Head",
        "email": "demo.statehead@kpa-dev.local",
        "role": UserRole.STATE_HEAD,
        "status": UserStatus.ACTIVE,
        "district_id": None,  # STATE_HEAD sees all Karnataka
        "taluka_id": None,
    },
    {
        "phone": "+919900000002",
        "name": "[DEMO] Suresh Nayak - District Admin",
        "email": "demo.districtadmin@kpa-dev.local",
        "role": UserRole.DISTRICT_ADMIN,
        "status": UserStatus.ACTIVE,
        "district_code": "BLR_U",   # Bengaluru Urban
        "taluka_id": None,
    },
    {
        "phone": "+919900000003",
        "name": "[DEMO] Anitha Gowda - Taluka Admin",
        "email": "demo.talukaadmin@kpa-dev.local",
        "role": UserRole.TALUKA_ADMIN,
        "status": UserStatus.ACTIVE,
        "district_code": "BLR_U",
        "taluka_code": "BLR_N",     # Bengaluru North
    },
    {
        "phone": "+919900000004",
        "name": "[DEMO] Prakash Hegde - Member",
        "email": "demo.member@kpa-dev.local",
        "role": UserRole.MEMBER,
        "status": UserStatus.ACTIVE,
        "district_code": "BLR_U",
        "taluka_code": "BLR_N",
    },
]

# Demo members for the district (beyond the MEMBER demo account)
DEMO_MEMBERS_DATA = [
    # The one linked to demo account 9900000004
    {
        "phone": "+919900000004",
        "full_name": "[DEMO] Prakash Hegde",
        "father_or_spouse_name": "Ramesh Hegde",
        "gender": "Male",
        "dob": date(1985, 6, 15),
        "blood_group": "O+",
        "studio_name": "Hegde Photography Studio",
        "experience_years": 12,
        "address_line": "45, MG Road, Bengaluru North",
        "pincode": "560001",
        "district_code": "BLR_U",
        "taluka_code": "BLR_N",
        "status": MemberStatus.APPROVED,
        "nominee": {
            "name": "[DEMO] Kavitha Hegde",
            "relationship": "Spouse",
            "phone": "+919900000041",
            "dob": date(1988, 3, 22),
            "aadhaar_last_4": "0001",
        },
    },
    # Additional approved members for dashboard/welfare event data
    {
        "phone": "+919900000005",
        "full_name": "[DEMO] Venkatesh Murthy",
        "father_or_spouse_name": "Krishna Murthy",
        "gender": "Male",
        "dob": date(1978, 9, 10),
        "blood_group": "A+",
        "studio_name": "Murthy Clicks",
        "experience_years": 18,
        "address_line": "12, Commercial Street, Bengaluru South",
        "pincode": "560002",
        "district_code": "BLR_U",
        "taluka_code": "BLR_S",
        "status": MemberStatus.APPROVED,
    },
    {
        "phone": "+919900000006",
        "full_name": "[DEMO] Lakshmi Devi",
        "father_or_spouse_name": "Srinivas Rao",
        "gender": "Female",
        "dob": date(1990, 12, 5),
        "blood_group": "B+",
        "studio_name": "Lakshmi Portraits",
        "experience_years": 8,
        "address_line": "78, Rajajinagar, Bengaluru North",
        "pincode": "560010",
        "district_code": "BLR_U",
        "taluka_code": "BLR_N",
        "status": MemberStatus.APPROVED,
    },
    {
        "phone": "+919900000007",
        "full_name": "[DEMO] Mohammed Ashraf",
        "father_or_spouse_name": "Abdul Karim",
        "gender": "Male",
        "dob": date(1982, 4, 20),
        "blood_group": "AB+",
        "studio_name": "Ashraf Digital Studio",
        "experience_years": 15,
        "address_line": "23, Shivajinagar, Bengaluru East",
        "pincode": "560051",
        "district_code": "BLR_U",
        "taluka_code": "BLR_E",
        "status": MemberStatus.APPROVED,
    },
    # A pending member (not yet approved)
    {
        "phone": "+919900000008",
        "full_name": "[DEMO] Ravi Shankar (PENDING)",
        "father_or_spouse_name": "Shankar Rao",
        "gender": "Male",
        "dob": date(1995, 7, 7),
        "blood_group": "O-",
        "studio_name": "Ravi Photography",
        "experience_years": 3,
        "address_line": "5, Yelahanka New Town",
        "pincode": "560064",
        "district_code": "BLR_U",
        "taluka_code": "YLH",
        "status": MemberStatus.PENDING,
    },
    # The DECEASED demo member -- welfare event will be created for this member
    {
        "phone": "+919900000009",
        "full_name": "[DEMO] Gopal Reddy (DECEASED - Demo)",
        "father_or_spouse_name": "Narasimha Reddy",
        "gender": "Male",
        "dob": date(1965, 2, 28),
        "blood_group": "A-",
        "studio_name": "Reddy Creations",
        "experience_years": 25,
        "address_line": "99, Old Airport Road, Bengaluru East",
        "pincode": "560017",
        "district_code": "BLR_U",
        "taluka_code": "BLR_E",
        "status": MemberStatus.APPROVED,  # will become SUSPENDED via welfare event
        "is_deceased_for_demo": True,
    },
]


async def _upsert_user(db: AsyncSession, account: dict, district_map: dict, taluka_map: dict) -> User:
    """Create or update a demo user account."""
    stmt = select(User).where(User.phone == account["phone"])
    user = (await db.execute(stmt)).scalar_one_or_none()

    district_id = None
    taluka_id = None
    if account.get("district_code"):
        district_id = district_map.get(account["district_code"])
    if account.get("taluka_code"):
        taluka_id = taluka_map.get(account["taluka_code"])

    if not user:
        user = User(
            phone=account["phone"],
            name=account["name"],
            email=account["email"],
            role=account["role"],
            status=account["status"],
            is_active=True,
            district_id=district_id,
            taluka_id=taluka_id,
        )
        db.add(user)
        print(f"  [+] Created user: {account['phone']} ({account['role'].value})")
    else:
        user.name = account["name"]
        user.email = account["email"]
        user.role = account["role"]
        user.status = account["status"]
        user.is_active = True
        user.district_id = district_id
        user.taluka_id = taluka_id
        print(f"  [~] Updated user: {account['phone']} ({account['role'].value})")

    await db.flush()
    return user


async def _upsert_supporting_user(db: AsyncSession, phone: str, name: str) -> User:
    """Create a minimal supporting user for a demo member."""
    stmt = select(User).where(User.phone == phone)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        user = User(
            phone=phone,
            name=name,
            role=UserRole.MEMBER,
            status=UserStatus.ACTIVE,
            is_active=True,
        )
        db.add(user)
        await db.flush()
    return user


async def _upsert_member(
    db: AsyncSession,
    user: User,
    mdata: dict,
    district_map: dict,
    taluka_map: dict,
    approved_by: User,
) -> Member:
    """Create or update a demo member record."""
    stmt = select(Member).where(Member.user_id == user.id)
    member = (await db.execute(stmt)).scalar_one_or_none()

    district_id = district_map[mdata["district_code"]]
    taluka_id = taluka_map[mdata["taluka_code"]]

    # Generate a stable demo membership number
    short_code = mdata["district_code"].replace("_", "")
    demo_seq = abs(hash(mdata["phone"])) % 90000 + 10000
    membership_no = f"KPA-{short_code}-{demo_seq:05d}"

    is_approved = mdata["status"] == MemberStatus.APPROVED

    if not member:
        member = Member(
            user_id=user.id,
            membership_no=membership_no if is_approved else None,
            full_name=mdata["full_name"],
            father_or_spouse_name=mdata.get("father_or_spouse_name"),
            gender=mdata["gender"],
            dob=mdata["dob"],
            blood_group=mdata.get("blood_group"),
            studio_name=mdata.get("studio_name"),
            experience_years=mdata.get("experience_years", 0),
            address_line=mdata.get("address_line"),
            pincode=mdata.get("pincode"),
            district_id=district_id,
            taluka_id=taluka_id,
            status=mdata["status"],
            approved_by_id=approved_by.id if is_approved else None,
            approved_at=datetime.now(timezone.utc) - timedelta(days=60) if is_approved else None,
        )
        db.add(member)
        print(f"  [+] Created member: {mdata['full_name']}")
    else:
        member.status = mdata["status"]
        member.district_id = district_id
        member.taluka_id = taluka_id
        if is_approved and not member.membership_no:
            member.membership_no = membership_no
            member.approved_by_id = approved_by.id
            member.approved_at = datetime.now(timezone.utc) - timedelta(days=60)
        print(f"  [~] Updated member: {mdata['full_name']}")

    await db.flush()

    # Add nominee if specified and none exists
    if mdata.get("nominee"):
        nom_stmt = select(Nominee).where(Nominee.member_id == member.id)
        existing_nom = (await db.execute(nom_stmt)).scalar_one_or_none()
        if not existing_nom:
            n = mdata["nominee"]
            nominee = Nominee(
                member_id=member.id,
                name=n["name"],
                relationship_to_member=n["relationship"],
                phone=n["phone"],
                dob=n.get("dob"),
                aadhaar_last_4=n.get("aadhaar_last_4"),
                is_primary=True,
            )
            db.add(nominee)
            print(f"     [+] Nominee: {n['name']}")

    return member


async def _create_welfare_event_and_contributions(
    db: AsyncSession,
    deceased_member: Member,
    active_members: list,
    state_head_user: User,
) -> tuple:
    """Create a demo welfare event with contributions for active members."""
    # Check if already exists
    stmt = select(WelfareEvent).where(WelfareEvent.deceased_member_id == deceased_member.id)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        print(f"  [~] Welfare event already exists for {deceased_member.full_name}")
        return existing, []

    # Mark deceased member as SUSPENDED
    deceased_member.status = MemberStatus.SUSPENDED

    eligible = [m for m in active_members if m.id != deceased_member.id]
    target_amount = float(len(eligible) * 10.0)

    event = WelfareEvent(
        deceased_member_id=deceased_member.id,
        title=f"[DEMO] Welfare Relief -- {deceased_member.full_name}",
        death_date=date(2026, 8, 15),
        cause_of_death="Natural causes (demo event - not a real person)",
        target_amount=target_amount,
        collected_amount=0.0,
        status=WelfareEventStatus.ACTIVE,
        created_by_id=state_head_user.id,
    )
    db.add(event)
    await db.flush()

    contributions = []
    for m in eligible:
        contrib = WelfareContribution(
            event_id=event.id,
            member_id=m.id,
            amount=10.00,
            status=ContributionStatus.PENDING,
        )
        db.add(contrib)
        contributions.append(contrib)

    print(f"  [+] Welfare event created: {event.title}")
    print(f"      {len(contributions)} pending INR 10 contributions generated")
    return event, contributions


async def _mark_one_contribution_paid(
    db: AsyncSession,
    contributions: list,
    member: Member,
    event: WelfareEvent,
) -> None:
    """Mark one demo member's contribution as paid with a demo payment record."""
    # Find the contribution for the demo member
    target_contrib = None
    for c in contributions:
        if c.member_id == member.id:
            target_contrib = c
            break

    if not target_contrib:
        # Try to load from DB
        stmt = select(WelfareContribution).where(
            WelfareContribution.member_id == member.id,
            WelfareContribution.event_id == event.id,
        )
        target_contrib = (await db.execute(stmt)).scalar_one_or_none()

    if not target_contrib or target_contrib.status == ContributionStatus.SUCCESS:
        print("  [~] Demo payment already recorded, skipping.")
        return

    now = datetime.now(timezone.utc) - timedelta(days=2)
    target_contrib.status = ContributionStatus.SUCCESS
    target_contrib.payment_method = "DEMO_UPI"
    target_contrib.paid_at = now

    event.collected_amount = float(event.collected_amount) + 10.0

    # Create a demo payment record
    receipt_no = f"KPA-DEMO-RCP-{abs(hash(str(member.id))) % 999999:06d}"
    stmt = select(Payment).where(Payment.receipt_no == receipt_no)
    existing_payment = (await db.execute(stmt)).scalar_one_or_none()
    if not existing_payment:
        payment = Payment(
            contribution_id=target_contrib.id,
            member_id=member.id,
            gateway="DEMO",
            gateway_order_id=f"demo_order_{abs(hash(str(member.id))):016x}",
            gateway_payment_id=f"demo_pay_{abs(hash(str(member.id))):016x}",
            amount=10.00,
            currency="INR",
            status=PaymentStatus.CAPTURED,
            payment_method="UPI",
            receipt_no=receipt_no,
            signature="demo-development-only-signature",
            raw_payload='{"source": "demo_seed", "env": "development"}',
        )
        db.add(payment)
        print(f"  [+] Demo payment recorded: {receipt_no} (INR 10.00 CAPTURED)")


async def _create_notifications(
    db: AsyncSession,
    state_head_user: User,
    member_user: User,
    district_id,
    taluka_id,
) -> None:
    """Create demo bilingual in-app notifications."""
    now = datetime.now(timezone.utc)

    demo_notifications = [
        # Welfare alert -- state-wide broadcast
        Notification(
            user_id=None,
            district_id=None,
            taluka_id=None,
            channel=NotificationChannel.IN_APP,
            type=NotificationType.WELFARE_ALERT,
            title_en="[DEMO] Welfare Relief Event -- Gopal Reddy",
            title_kn="[DEMO] \u0c95\u0cb2\u0ccd\u0caf\u0cbe\u0ca3 \u0caa\u0cb0\u0cbf\u0cb9\u0cbe\u0cb0 \u0c98\u0c9f\u0ca8\u0cc6 -- \u0c97\u0ccb\u0caa\u0cbe\u0cb2 \u0cb0\u0cc6\u0ca1\u0ccd\u0ca1\u0cbf",
            body_en=(
                "[DEMO DATA] A welfare relief event has been initiated for the family of Shri Gopal Reddy. "
                "All active members are required to contribute INR 10. This is demo data only."
            ),
            body_kn=(
                "[DEMO \u0ca1\u0cc7\u0c9f\u0cbe] \u0cb6\u0ccd\u0cb0\u0cc0 \u0c97\u0ccb\u0caa\u0cbe\u0cb2 \u0cb0\u0cc6\u0ca1\u0ccd\u0ca1\u0cbf \u0c85\u0cb5\u0cb0 \u0c95\u0cc1\u0c9f\u0cc1\u0c82\u0cac\u0c95\u0ccd\u0c95\u0cc6 \u0c95\u0cb2\u0ccd\u0caf\u0cbe\u0ca3 \u0caa\u0cb0\u0cbf\u0cb9\u0cbe\u0cb0 \u0c95\u0cbe\u0cb0\u0ccd\u0caf\u0c95\u0ccd\u0cb0\u0cae \u0c86\u0cb0\u0c82\u0cad\u0cb5\u0cbe\u0c97\u0cbf\u0ca6\u0cc6. "
                "\u0c8e\u0cb2\u0ccd\u0cb2\u0cbe \u0cb8\u0c95\u0ccd\u0cb0\u0cbf\u0caf \u0cb8\u0ca6\u0cb8\u0ccd\u0caf\u0cb0\u0cc1 INR 10 \u0c95\u0ccb\u0ca1\u0cc1\u0c97\u0cc6 \u0ca8\u0cc0\u0ca1\u0cac\u0cc7\u0c95\u0cc1. \u0c87\u0ca6\u0cc1 \u0ca1\u0cc6\u0cae\u0ccb \u0ca1\u0cc7\u0c9f\u0cbe \u0cae\u0cbe\u0ca4\u0ccd\u0cb0."
            ),
            is_read=False,
            sent_at=now - timedelta(days=3),
        ),
        # Payment receipt -- for the specific member
        Notification(
            user_id=member_user.id,
            district_id=None,
            taluka_id=None,
            channel=NotificationChannel.IN_APP,
            type=NotificationType.PAYMENT_RECEIPT,
            title_en="[DEMO] Payment Receipt -- INR 10 Welfare Contribution",
            title_kn="[DEMO] \u0caa\u0cbe\u0cb5\u0ca4\u0cbf \u0cb0\u0cb8\u0cc0\u0ca4\u0cbf -- INR 10 \u0c95\u0cb2\u0ccd\u0caf\u0cbe\u0ca3 \u0c95\u0ccb\u0ca1\u0cc1\u0c97\u0cc6",
            body_en=(
                "[DEMO DATA] Your welfare contribution of INR 10 for the Gopal Reddy relief fund "
                "has been successfully recorded via UPI. Receipt: KPA-DEMO-RCP. This is demo data only."
            ),
            body_kn=(
                "[DEMO \u0ca1\u0cc7\u0c9f\u0cbe] \u0c97\u0ccb\u0caa\u0cbe\u0cb2 \u0cb0\u0cc6\u0ca1\u0ccd\u0ca1\u0cbf \u0caa\u0cb0\u0cbf\u0cb9\u0cbe\u0cb0 \u0ca8\u0cbf\u0ca7\u0cbf\u0c97\u0cc6 INR 10 \u0c95\u0cb2\u0ccd\u0caf\u0cbe\u0ca3 \u0c95\u0ccb\u0ca1\u0cc1\u0c97\u0cc6 UPI \u0cae\u0cc2\u0cb2\u0c95 \u0caf\u0cb6\u0cb8\u0ccd\u0cb5\u0cbf\u0caf\u0cbe\u0c97\u0cbf \u0ca6\u0cbe\u0c96\u0cb2\u0cbe\u0c97\u0cbf\u0ca6\u0cc6. "
                "\u0cb0\u0cb8\u0cc0\u0ca4\u0cbf: KPA-DEMO-RCP. \u0c87\u0ca6\u0cc1 \u0ca1\u0cc6\u0cae\u0ccb \u0ca1\u0cc7\u0c9f\u0cbe \u0cae\u0cbe\u0ca4\u0ccd\u0cb0."
            ),
            is_read=True,
            sent_at=now - timedelta(days=2),
        ),
        # District broadcast
        Notification(
            user_id=None,
            district_id=district_id,
            taluka_id=None,
            channel=NotificationChannel.IN_APP,
            type=NotificationType.GENERAL_BROADCAST,
            title_en="[DEMO] District Photography Meet -- Bengaluru Urban",
            title_kn="[DEMO] \u0c9c\u0cbf\u0cb2\u0ccd\u0cb2\u0cbe \u0ced\u0cbe\u0caf\u0cbe\u0c97\u0ccd\u0cb0\u0cb9\u0ca3 \u0cb8\u0cad\u0cc6 -- \u0cac\u0cc6\u0c82\u0c97\u0cb3\u0cc2\u0cb0\u0cc1 \u0ca8\u0c97\u0cb0",
            body_en=(
                "[DEMO DATA] The annual district photography meet for Bengaluru Urban members "
                "is scheduled for October 15th at Town Hall, Bengaluru. All members are invited. "
                "This is demo data only."
            ),
            body_kn=(
                "[DEMO \u0ca1\u0cc7\u0c9f\u0cbe] \u0cac\u0cc6\u0c82\u0c97\u0cb3\u0cc2\u0cb0\u0cc1 \u0ca8\u0c97\u0cb0 \u0c9c\u0cbf\u0cb2\u0ccd\u0cb2\u0cc6\u0caf \u0cb5\u0cbe\u0cb0\u0ccd\u0cb7\u0cbf\u0c95 \u0ced\u0cbe\u0caf\u0cbe\u0c97\u0ccd\u0cb0\u0cb9\u0ca3 \u0cb8\u0cad\u0cc6\u0caf\u0cc1 \u0c85\u0c95\u0ccd\u0c9f\u0ccb\u0cac\u0cb0\u0ccd 15 \u0cb0\u0c82\u0ca6\u0cc1 \u0c9f\u0ccc\u0ca8\u0ccd \u0cb9\u0cbe\u0cb2\u0ccd\u0ca8\u0cb2\u0ccd\u0cb2\u0cbf \u0ca8\u0cbf\u0c97\u0ca6\u0cbf\u0caa\u0ca1\u0cbf\u0cb8\u0cb2\u0cbe\u0c97\u0cbf\u0ca6\u0cc6. "
                "\u0c8e\u0cb2\u0ccd\u0cb2\u0cbe \u0cb8\u0ca6\u0cb8\u0ccd\u0caf\u0cb0\u0ca8\u0ccd\u0ca8\u0cc1 \u0c86\u0cb9\u0ccd\u0cb5\u0cbe\u0ca8\u0cbf\u0cb8\u0cb2\u0cbe\u0c97\u0cbf\u0ca6\u0cc6. \u0c87\u0ca6\u0cc1 \u0ca1\u0cc6\u0cae\u0ccb \u0ca1\u0cc7\u0c9f\u0cbe \u0cae\u0cbe\u0ca4\u0ccd\u0cb0."
            ),
            is_read=False,
            sent_at=now - timedelta(days=5),
        ),
        # KYC update for state head
        Notification(
            user_id=state_head_user.id,
            district_id=None,
            taluka_id=None,
            channel=NotificationChannel.IN_APP,
            type=NotificationType.KYC_UPDATE,
            title_en="[DEMO] New Member Approval Pending -- Ravi Shankar",
            title_kn="[DEMO] \u0cb9\u0cca\u0cb8 \u0cb8\u0ca6\u0cb8\u0ccd\u0caf\u0cb0 \u0c85\u0ca8\u0cc1\u0cae\u0ccb\u0ca6\u0ca8\u0cc6 \u0cac\u0cbe\u0c95\u0cbf -- \u0cb0\u0cb5\u0cbf \u0cb6\u0c82\u0c95\u0cb0",
            body_en=(
                "[DEMO DATA] A new member application from Ravi Shankar (Bengaluru Urban - Yelahanka) "
                "is pending your review and approval. This is demo data only."
            ),
            body_kn=(
                "[DEMO \u0ca1\u0cc7\u0c9f\u0cbe] \u0cb0\u0cb5\u0cbf \u0cb6\u0c82\u0c95\u0cb0 (\u0cac\u0cc6\u0c82\u0c97\u0cb3\u0cc2\u0cb0\u0cc1 \u0ca8\u0c97\u0cb0 - \u0caf\u0cb2\u0cb9\u0c82\u0c95) \u0c85\u0cb5\u0cb0 \u0cb9\u0cca\u0cb8 \u0cb8\u0ca6\u0cb8\u0ccd\u0caf \u0c85\u0cb0\u0ccd\u0c9c\u0cbf\u0caf\u0cc1 \u0ca8\u0cbf\u0cae\u0ccd\u0cae \u0caa\u0cb0\u0cbf\u0cb6\u0cc0\u0cb2\u0ca8\u0cc6 \u0cae\u0ca4\u0ccd\u0ca4\u0cc1 \u0c85\u0ca8\u0cc1\u0cae\u0ccb\u0ca6\u0ca8\u0cc6\u0c97\u0cbe\u0c97\u0cbf \u0cac\u0cbe\u0c95\u0cbf\u0caf\u0cbf\u0ca6\u0cc6. "
                "\u0c87\u0ca6\u0cc1 \u0ca1\u0cc6\u0cae\u0ccb \u0ca1\u0cc7\u0c9f\u0cbe \u0cae\u0cbe\u0ca4\u0ccd\u0cb0."
            ),
            is_read=False,
            sent_at=now - timedelta(hours=6),
        ),
        # Taluka broadcast
        Notification(
            user_id=None,
            district_id=district_id,
            taluka_id=taluka_id,
            channel=NotificationChannel.IN_APP,
            type=NotificationType.GENERAL_BROADCAST,
            title_en="[DEMO] Taluka Committee Meeting -- Bengaluru North",
            title_kn="[DEMO] \u0ca4\u0cbe\u0cb2\u0cc2\u0c95\u0cc1 \u0cb8\u0cae\u0cbf\u0ca4\u0cbf \u0cb8\u0cad\u0cc6 -- \u0cac\u0cc6\u0c82\u0c97\u0cb3\u0cc2\u0cb0\u0cc1 \u0c89\u0ca4\u0ccd\u0ca4\u0cb0",
            body_en=(
                "[DEMO DATA] Monthly taluka committee meeting for Bengaluru North is scheduled "
                "for September 20th at KPA office. This is demo data only."
            ),
            body_kn=(
                "[DEMO \u0ca1\u0cc7\u0c9f\u0cbe] \u0cac\u0cc6\u0c82\u0c97\u0cb3\u0cc2\u0cb0\u0cc1 \u0c89\u0ca4\u0ccd\u0ca4\u0cb0 \u0ca4\u0cbe\u0cb2\u0ccd\u0cb2\u0cc2\u0c95\u0cc1 \u0cb8\u0cae\u0cbf\u0ca4\u0cbf\u0caf \u0cae\u0cbe\u0cb8\u0cbf\u0c95 \u0cb8\u0cad\u0cc6 \u0cb8\u0cc6\u0caa\u0ccd\u0c9f\u0cc6\u0c82\u0cac\u0cb0\u0ccd 20 \u0cb0\u0c82\u0ca6\u0cc1 KPA \u0c95\u0c9a\u0cc7\u0cb0\u0cbf\u0caf\u0cb2\u0ccd\u0cb2\u0cbf \u0ca8\u0cbf\u0c97\u0ca6\u0cbf\u0caa\u0ca1\u0cbf\u0cb8\u0cb2\u0cbe\u0c97\u0cbf\u0ca6\u0cc6. "
                "\u0c87\u0ca6\u0cc1 \u0ca1\u0cc6\u0cae\u0ccb \u0ca1\u0cc7\u0c9f\u0cbe \u0cae\u0cbe\u0ca4\u0ccd\u0cb0."
            ),
            is_read=False,
            sent_at=now - timedelta(days=1),
        ),
    ]

    # Only insert notifications that don't already exist (check by title_en)
    added = 0
    for notif in demo_notifications:
        stmt = select(Notification).where(Notification.title_en == notif.title_en)
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if not existing:
            db.add(notif)
            added += 1

    print(f"  [+] Created {added} demo notifications (EN + KN bilingual)")


async def seed():
    """Main seed entrypoint."""
    _check_not_production()

    print("\n" + "=" * 60)
    print("  KPA WELFARE SYSTEM -- DEMO SEED")
    print("  WARNING: DEVELOPMENT / DEMO DATA ONLY")
    print("=" * 60)

    # ── Step 0: Auto-create database schema ────────────────────────────
    print("\n[Step 0] Ensuring database schema is up to date...")
    from app.core.database import engine, Base
    import app.models  # noqa: F401 -- registers all models with Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("  [OK] Schema ready")

    async with AsyncSessionLocal() as db:
        # ── Step 1: Verify geographic master data exists ────────────────
        print("\n[Step 1] Verifying geographic master data...")
        district_stmt = select(District)
        districts = (await db.execute(district_stmt)).scalars().all()

        if not districts:
            print("  [!] No districts found -- seeding Karnataka geography now...")
            from app.services.geo_service import GeoService
            await GeoService.seed_karnataka_data(db)
            districts = (await db.execute(district_stmt)).scalars().all()

        district_map = {d.code: d.id for d in districts}
        print(f"  [OK] Found {len(districts)} districts")

        taluka_stmt = select(Taluka)
        talukas = (await db.execute(taluka_stmt)).scalars().all()
        taluka_map = {t.code: t.id for t in talukas}
        print(f"  [OK] Found {len(talukas)} talukas")

        # Validate required geographic data
        required_district = "BLR_U"
        required_talukas = ["BLR_N", "BLR_S", "BLR_E", "YLH"]
        if required_district not in district_map:
            print(f"  [ERR] Required district '{required_district}' not found.")
            sys.exit(1)
        missing = [t for t in required_talukas if t not in taluka_map]
        if missing:
            print(f"  [ERR] Required talukas missing: {missing}")
            sys.exit(1)

        # ── Step 2: Upsert demo admin/user accounts ─────────────────────
        print("\n[Step 2] Upserting demo user accounts...")
        demo_users = {}
        for account in DEMO_ACCOUNTS:
            user = await _upsert_user(db, account, district_map, taluka_map)
            demo_users[account["phone"]] = user

        await db.commit()

        # ── Step 3: Upsert demo member records ──────────────────────────
        print("\n[Step 3] Upserting demo member records...")
        state_head_user = demo_users["+919900000001"]
        member_user = demo_users["+919900000004"]

        demo_members = {}
        for mdata in DEMO_MEMBERS_DATA:
            phone = mdata["phone"]
            if phone in demo_users:
                user = demo_users[phone]
            else:
                user = await _upsert_supporting_user(db, phone, mdata["full_name"])

            member = await _upsert_member(
                db=db,
                user=user,
                mdata=mdata,
                district_map=district_map,
                taluka_map=taluka_map,
                approved_by=state_head_user,
            )
            demo_members[phone] = member

        await db.commit()

        # ── Step 4: Create welfare event + contributions ─────────────────
        print("\n[Step 4] Creating demo welfare event...")
        deceased_member = demo_members.get("+919900000009")

        if deceased_member:
            eligible_active = [
                m for phone, m in demo_members.items()
                if m.status == MemberStatus.APPROVED and m.id != deceased_member.id
            ]
            event, contributions = await _create_welfare_event_and_contributions(
                db=db,
                deceased_member=deceased_member,
                active_members=eligible_active,
                state_head_user=state_head_user,
            )
            await db.commit()

            # ── Step 5: Mark demo member contribution as paid ────────────
            print("\n[Step 5] Recording demo payment for member account (9900000004)...")
            demo_main_member = demo_members.get("+919900000004")
            if demo_main_member and event:
                await _mark_one_contribution_paid(
                    db=db,
                    contributions=contributions,
                    member=demo_main_member,
                    event=event,
                )
                await db.commit()
        else:
            print("  [SKIP] No deceased demo member found -- skipping welfare event.")

        # ── Step 6: Create demo notifications ────────────────────────────
        print("\n[Step 6] Creating demo bilingual notifications...")
        blr_u_district_id = district_map.get("BLR_U")
        blr_n_taluka_id = taluka_map.get("BLR_N")
        await _create_notifications(
            db=db,
            state_head_user=state_head_user,
            member_user=member_user,
            district_id=blr_u_district_id,
            taluka_id=blr_n_taluka_id,
        )
        await db.commit()

    # ── Summary ────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  [DONE] DEMO SEED COMPLETE")
    print("=" * 60)
    print()
    print("  WARNING: DEVELOPMENT / DEMO ONLY -- NOT FOR PRODUCTION USE")
    print()
    print("  Demo Accounts (all use OTP: 123456 in dev mode)")
    print("  +-------------+------------------+--------------------------------------------+")
    print("  | Mobile      | Role             | Geographic Scope                           |")
    print("  +-------------+------------------+--------------------------------------------+")
    print("  | 9900000001  | STATE_HEAD       | All Karnataka                              |")
    print("  | 9900000002  | DISTRICT_ADMIN   | Bengaluru Urban district only              |")
    print("  | 9900000003  | TALUKA_ADMIN     | Bengaluru North taluka only                |")
    print("  | 9900000004  | MEMBER           | Own member profile only                    |")
    print("  +-------------+------------------+--------------------------------------------+")
    print()
    print("  Demo Data:")
    print("   - 6 demo members (4 approved, 1 pending, 1 deceased/suspended)")
    print("   - 1 active welfare event (INR 10 contributions for eligible members)")
    print("   - 1 completed contribution + demo UPI payment receipt (account 9900000004)")
    print("   - 5 demo in-app notifications (English + Kannada bilingual)")
    print()
    print("  To start the backend (in a new terminal):")
    print("   cd D:\\KPA\\backend")
    print("   uvicorn app.main:app --reload --port 8000")
    print()
    print("  Web app is already running at: http://localhost:5173/login")
    print()


if __name__ == "__main__":
    asyncio.run(seed())
