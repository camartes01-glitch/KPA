"""
Google Authentication Service — Google ID Token verification, user provisioning, and session generation.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models.user import DeviceSession, User, UserRole, UserStatus
from app.schemas.auth import TokenResponse, UserRead
from app.services.audit_service import AuditService
from app.services.auth_service import hash_token


class GoogleAuthService:
    @staticmethod
    def verify_google_id_token(id_token_str: str) -> Dict[str, Any]:
        """
        Verify a Google OAuth2 ID token using Google's public keys.
        Validates signature, issuer, audience, and expiration.
        """
        try:
            req = google_requests.Request()
            audience = settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None
            
            # verify_oauth2_token checks signature, exp, and optionally aud
            payload = google_id_token.verify_oauth2_token(
                id_token_str,
                req,
                audience=audience,
            )

            # Validate issuer
            issuer = payload.get("iss", "")
            if issuer not in ("accounts.google.com", "https://accounts.google.com"):
                raise ValueError(f"Invalid token issuer: {issuer}")

            sub = payload.get("sub")
            email = payload.get("email")

            if not sub or not email:
                raise ValueError("Token missing required claims ('sub' or 'email')")

            return {
                "sub": str(sub),
                "email": str(email).lower().strip(),
                "email_verified": bool(payload.get("email_verified", False)),
                "name": payload.get("name"),
                "picture": payload.get("picture"),
            }

        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google ID token: {str(exc)}",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to verify Google ID token. Please try signing in again.",
            )

    @classmethod
    async def authenticate_with_google(
        cls,
        db: AsyncSession,
        id_token_str: str,
        device_name: Optional[str] = None,
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """
        Verify Google ID token, link or provision user, and issue KPA JWT tokens.
        """
        now = datetime.now(timezone.utc)
        token_info = cls.verify_google_id_token(id_token_str)

        # Enforce verified email
        if not token_info.get("email_verified"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your Google email address is not verified by Google.",
            )

        email = token_info["email"]
        google_sub = token_info["sub"]

        # Enforce @gmail.com only policy if configured
        if settings.GOOGLE_GMAIL_ONLY and not email.endswith("@gmail.com"):
            await AuditService.log_action(
                db=db,
                action="AUTH_GOOGLE_LOGIN_FAILED",
                resource_type="USER",
                payload={"reason": "Non-gmail domain rejected", "email": email},
                ip_address=ip_address,
                user_agent=user_agent,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only @gmail.com accounts are permitted to sign in.",
            )

        # Step 1: Look for existing user by google_sub first
        stmt = select(User).where(User.google_sub == google_sub)
        user = (await db.execute(stmt)).scalar_one_or_none()

        # Step 2: If not found by google_sub, look by email (linking account)
        if not user:
            stmt = select(User).where(User.email == email)
            user = (await db.execute(stmt)).scalar_one_or_none()
            if user:
                user.google_sub = google_sub

        # Step 3: If still not found, provision new user
        if not user:
            user = User(
                google_sub=google_sub,
                email=email,
                name=token_info.get("name"),
                role=UserRole.MEMBER,
                status=UserStatus.PENDING,
                is_active=True,
                last_login_at=now,
            )
            db.add(user)
            await db.flush()
        else:
            # Check user active status
            if not user.is_active:
                await AuditService.log_action(
                    db=db,
                    action="AUTH_GOOGLE_LOGIN_FAILED",
                    resource_type="USER",
                    resource_id=str(user.id),
                    user_id=user.id,
                    payload={"reason": "User account deactivated", "email": email},
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your account has been deactivated. Please contact an administrator.",
                )

            if user.status in (UserStatus.SUSPENDED, UserStatus.REJECTED):
                await AuditService.log_action(
                    db=db,
                    action="AUTH_GOOGLE_LOGIN_FAILED",
                    resource_type="USER",
                    resource_id=str(user.id),
                    user_id=user.id,
                    payload={"reason": f"Account status is {user.status.value}", "email": email},
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Your account is {user.status.value.lower()}. Access denied.",
                )

            user.last_login_at = now
            if not user.google_sub:
                user.google_sub = google_sub
            if not user.email:
                user.email = email
            if not user.name and token_info.get("name"):
                user.name = token_info.get("name")

        # Step 4: Issue standard KPA access and refresh JWT tokens
        access_token = create_access_token(
            subject=str(user.id),
            role=user.role.value,
            extra_claims={"email": user.email, "phone": user.phone or ""},
        )
        refresh_token = create_refresh_token(subject=str(user.id))

        # Step 5: Create device session
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

        # Step 6: Log successful login audit event
        await AuditService.log_action(
            db=db,
            action="AUTH_GOOGLE_LOGIN_SUCCESS",
            resource_type="USER",
            resource_id=str(user.id),
            user_id=user.id,
            payload={"email": user.email, "role": user.role.value},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserRead.model_validate(user),
        )
