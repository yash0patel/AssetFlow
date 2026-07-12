"""
app/services/auth_service.py
────────────────────────────
Business logic layer for user signup, login, session management, token refresh, and password recovery.
"""

from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from typing import Optional, Tuple
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserSession
from app.repositories.user_repository import user_repo


def hash_token(token: str) -> str:
    """Return the SHA-256 hash of a token string for secure DB storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    async def authenticate_user(
        self, db: AsyncSession, email: str, password: str, ip_address: Optional[str] = None
    ) -> User:
        """
        Authenticate a user by email and password.
        Enforces account locking after 5 consecutive failures.
        """
        user = await user_repo.get_by_email(db, email)
        if not user:
            # Audit log user enumeration attempt safely
            await user_repo.log_login_attempt(
                db, email=email, was_successful=False, failure_reason="User not found", ip_address=ip_address
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Check account lock status
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            time_left_mins = int((user.locked_until - datetime.now(timezone.utc)).total_seconds() / 60) + 1
            await user_repo.log_login_attempt(
                db, email=email, was_successful=False, failure_reason="Account locked", ip_address=ip_address, user_id=user.id
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is locked. Try again in {time_left_mins} minutes.",
            )

        # Verify password
        if not verify_password(password, user.password_hash):
            user.failed_login_count += 1
            failure_reason = "Incorrect password"
            
            # Lock account if failures exceed threshold
            if user.failed_login_count >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
                failure_reason = "Incorrect password - Account locked"
                print(f"User account locked due to excessive failures: {email}")

            await user_repo.log_login_attempt(
                db, email=email, was_successful=False, failure_reason=failure_reason, ip_address=ip_address, user_id=user.id
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Clear login tracking on success
        user.failed_login_count = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        
        await user_repo.log_login_attempt(
            db, email=email, was_successful=True, ip_address=ip_address, user_id=user.id
        )
        return user

    async def create_tokens_and_session(
        self, db: AsyncSession, user: User, ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> Tuple[str, str, datetime]:
        """Generate a new JWT pair and log the active session in the database."""
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        access_hash = hash_token(access_token)
        refresh_hash = hash_token(refresh_token)
        
        # Access token expiration time
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        await user_repo.create_session(
            db=db,
            user_id=user.id,
            access_token_hash=access_hash,
            refresh_token_hash=refresh_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return access_token, refresh_token, expires_at

    async def register_user(
        self, db: AsyncSession, fullName: str, email: str, password: str
    ) -> User:
        """Register a new user with default 'employee' privileges."""
        existing_user = await user_repo.get_by_email(db, email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is already registered.",
            )

        # Split full name
        name_parts = fullName.strip().split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else None

        password_hash = hash_password(password)
        
        # Create user + profile
        user = await user_repo.create_user_with_profile(
            db=db,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name
        )

        # Assign default 'employee' role
        await user_repo.assign_role_to_user(
            db=db,
            user_id=user.id,
            role_name="employee",
            assigner_id=user.id  # self-assigned during sign-up
        )

        return user

    async def refresh_session(
        self, db: AsyncSession, refresh_token: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> Tuple[str, str, User]:
        """Validate refresh token, revoke current session, and issue a fresh session/token pair."""
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
            user_id = UUID(payload.get("sub"))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        refresh_hash = hash_token(refresh_token)
        session = await user_repo.get_session_by_refresh_token(db, refresh_hash)
        if not session or session.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is expired or revoked",
            )

        # Revoke old session
        await user_repo.revoke_refresh_session(db, refresh_hash)

        # Fetch user
        user = await user_repo.get_by_id(db, user_id)
        if not user or user.status != "Active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive or deleted",
            )

        # Create new tokens & session
        new_access_token, new_refresh_token, _ = await self.create_tokens_and_session(
            db=db,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return new_access_token, new_refresh_token, user

    async def logout_user(self, db: AsyncSession, access_token: str) -> None:
        """Revoke the current active session associated with the access token."""
        token_hash = hash_token(access_token)
        await user_repo.revoke_session(db, token_hash)

    async def generate_password_reset_token(self, db: AsyncSession, email: str) -> Optional[str]:
        """Generate a random reset token and register it for the user if email exists."""
        user = await user_repo.get_by_email(db, email)
        if not user:
            return None # Safe no-op to prevent email harvesting

        token = secrets.token_urlsafe(32)
        token_hash = hash_token(token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        await user_repo.create_password_reset_token(
            db=db,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        return token


# Instantiate singleton auth service
auth_service = AuthService()
