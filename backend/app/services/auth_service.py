"""
Auth Service — OTP lifecycle, user provisioning, JWT tokens, session rotation, and logout.
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token, generate_otp
from app.models.user import DeviceSession, OTPVerification, User, UserRole, UserStatus
from app.schemas.auth import TokenResponse, UserRead


def hash_token(token: str) -> str:
    """SHA-256 hash for secure token fingerprinting."""
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    @staticmethod
    async def request_otp(db: AsyncSession, phone: str) -> dict:
        """Generate and record OTP for a phone number."""
        now = datetime.now(timezone.utc)

        # Check rate limit: count OTP requests in the past hour
        one_hour_ago = now - timedelta(hours=1)
        stmt = select(OTPVerification).where(
            OTPVerification.phone == phone,
            OTPVerification.created_at >= one_hour_ago,
        )
        recent_requests = (await db.execute(stmt)).scalars().all()
        if len(recent_requests) >= settings.OTP_RATE_LIMIT_PER_HOUR:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OTP requests. Please try again later.",
            )

        code = generate_otp()
        expires_at = now + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)

        otp_record = OTPVerification(
            phone=phone,
            otp_code=code,
            expires_at=expires_at,
            attempts=0,
            is_used=False,
        )
        db.add(otp_record)
        await db.commit()

        # In production, dispatch through MSG91 / SMS gateway worker
        # In dev mode, return code in response for testing
        response_data = {
            "phone": phone,
            "message": "OTP sent successfully",
            "expires_in_seconds": settings.OTP_EXPIRY_MINUTES * 60,
        }
        if settings.OTP_DEV_MODE and not settings.is_production:
            response_data["dev_code"] = code


        return response_data

    @staticmethod
    async def verify_otp(
        db: AsyncSession,
        phone: str,
        otp: str,
        device_name: Optional[str] = None,
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Verify OTP, provision or fetch user, and issue tokens."""
        now = datetime.now(timezone.utc)

        # Look up latest unused OTP for phone
        stmt = (
            select(OTPVerification)
            .where(
                OTPVerification.phone == phone,
                OTPVerification.is_used == False,
                OTPVerification.expires_at > now,
            )
            .order_by(OTPVerification.created_at.desc())
        )
        otp_record = (await db.execute(stmt)).scalar_one_or_none()

        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired or was not requested",
            )

        if otp_record.attempts >= settings.OTP_MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Max OTP attempts exceeded. Please request a new OTP.",
            )

        if otp_record.otp_code != otp:
            otp_record.attempts += 1
            await db.commit()
            remaining = settings.OTP_MAX_ATTEMPTS - otp_record.attempts
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid OTP code. {remaining} attempt(s) remaining.",
            )

        # Mark OTP as consumed
        otp_record.is_used = True

        # Find or create user
        user_stmt = select(User).where(User.phone == phone)
        user = (await db.execute(user_stmt)).scalar_one_or_none()

        if not user:
            # New user registration
            user = User(
                phone=phone,
                role=UserRole.MEMBER,
                status=UserStatus.PENDING,
                is_active=True,
                last_login_at=now,
            )
            db.add(user)
            await db.flush()
        else:
            user.last_login_at = now

        # Generate tokens
        access_token = create_access_token(
            subject=str(user.id),
            role=user.role.value,
            extra_claims={"phone": user.phone},
        )
        refresh_token = create_refresh_token(subject=str(user.id))

        # Store session with hashed refresh token
        refresh_hash = hash_token(refresh_token)
        session_expires = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        session = DeviceSession(
            user_id=user.id,
            refresh_token_hash=refresh_hash,
            device_name=device_name,
            device_id=device_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=session_expires,
            is_revoked=False,
        )
        db.add(session)
        await db.commit()
        await db.refresh(user)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserRead.model_validate(user),
        )

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token_str: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """Rotate refresh token and issue a fresh access token."""
        try:
            payload = decode_token(refresh_token_str)
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )
            user_id = payload.get("sub")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        old_hash = hash_token(refresh_token_str)
        now = datetime.now(timezone.utc)

        # Find active session
        stmt = select(DeviceSession).where(
            DeviceSession.refresh_token_hash == old_hash,
            DeviceSession.is_revoked == False,
            DeviceSession.expires_at > now,
        )
        session = (await db.execute(stmt)).scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or revoked",
            )

        # Revoke old session (Rotation)
        session.is_revoked = True

        # Fetch user
        user = await db.get(User, session.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive or not found",
            )

        # Issue new tokens
        new_access = create_access_token(subject=str(user.id), role=user.role.value)
        new_refresh = create_refresh_token(subject=str(user.id))

        # Create new session
        new_session = DeviceSession(
            user_id=user.id,
            refresh_token_hash=hash_token(new_refresh),
            device_name=session.device_name,
            device_id=session.device_id,
            ip_address=ip_address or session.ip_address,
            user_agent=user_agent or session.user_agent,
            expires_at=now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            is_revoked=False,
        )
        db.add(new_session)
        await db.commit()

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserRead.model_validate(user),
        )

    @staticmethod
    async def logout(db: AsyncSession, refresh_token_str: Optional[str] = None):
        """Revoke device session upon logout."""
        if refresh_token_str:
            token_hash = hash_token(refresh_token_str)
            stmt = (
                update(DeviceSession)
                .where(DeviceSession.refresh_token_hash == token_hash)
                .values(is_revoked=True)
            )
            await db.execute(stmt)
            await db.commit()
