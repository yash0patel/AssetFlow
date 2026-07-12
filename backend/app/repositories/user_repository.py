"""
app/repositories/user_repository.py
───────────────────────────────────
Repository layer for User, UserProfile, UserRole, UserSession, and related security models.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import (
    User,
    UserProfile,
    Role,
    UserRole,
    UserSession,
    PasswordResetToken,
    LoginAttempt,
)
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Fetch a user by email, eagerly loading profile and roles.
        Converts email to lowercase to match case-insensitive index behavior.
        """
        stmt = (
            select(User)
            .where(User.email == email.lower())
            .options(
                selectinload(User.profile),
                selectinload(User.user_roles).selectinload(UserRole.role),
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Fetch a user by UUID, eagerly loading profile and roles."""
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.profile),
                selectinload(User.user_roles).selectinload(UserRole.role),
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_user_with_profile(
        self, db: AsyncSession, email: str, password_hash: str, first_name: str, last_name: Optional[str]
    ) -> User:
        """Create a new User record and its associated UserProfile."""
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            status="Active"
        )
        db.add(user)
        await db.flush()  # obtain user.id

        profile = UserProfile(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name
        )
        db.add(profile)
        await db.flush()
        
        # Reload to populate relationship attributes
        stmt = select(User).where(User.id == user.id).options(selectinload(User.profile))
        res = await db.execute(stmt)
        return res.scalar_one()

    async def assign_role_to_user(
        self, db: AsyncSession, user_id: UUID, role_name: str, assigner_id: UUID
    ) -> UserRole:
        """Query Role by name and create a UserRole assignment for the user."""
        stmt = select(Role).where(Role.name == role_name)
        res = await db.execute(stmt)
        role = res.scalar_one_or_none()
        if not role:
            raise ValueError(f"Role {role_name} does not exist")

        # Deactivate any existing active role of same type
        stmt_revoke = (
            update(UserRole)
            .where((UserRole.user_id == user_id) & (UserRole.role_id == role.id) & (UserRole.revoked_at.is_(None)))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await db.execute(stmt_revoke)

        user_role = UserRole(
            user_id=user_id,
            role_id=role.id,
            assigned_by=assigner_id
        )
        db.add(user_role)
        await db.flush()
        return user_role

    async def get_user_role_name(self, db: AsyncSession, user_id: UUID) -> str:
        """Find the user's primary active role name. Default to 'employee' if none."""
        stmt = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where((UserRole.user_id == user_id) & (UserRole.revoked_at.is_(None)))
            .limit(1)
        )
        res = await db.execute(stmt)
        role_name = res.scalar_one_or_none()
        return role_name or "employee"

    # ── Sessions ───────────────────────────────────────────────────────────────
    async def create_session(
        self,
        db: AsyncSession,
        user_id: UUID,
        access_token_hash: str,
        refresh_token_hash: Optional[str],
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSession:
        """Create a new database user session tracker."""
        session = UserSession(
            user_id=user_id,
            access_token_hash=access_token_hash,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(session)
        await db.flush()
        return session

    async def get_session_by_access_token(
        self, db: AsyncSession, access_token_hash: str
    ) -> Optional[UserSession]:
        """Fetch session by access token hash, ensuring it is not revoked or expired."""
        stmt = select(UserSession).where(
            (UserSession.access_token_hash == access_token_hash)
            & (UserSession.revoked_at.is_(None))
            & (UserSession.expires_at > datetime.now(timezone.utc))
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_session_by_refresh_token(
        self, db: AsyncSession, refresh_token_hash: str
    ) -> Optional[UserSession]:
        """Fetch session by refresh token hash, ensuring it is not revoked."""
        stmt = select(UserSession).where(
            (UserSession.refresh_token_hash == refresh_token_hash)
            & (UserSession.revoked_at.is_(None))
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def revoke_session(self, db: AsyncSession, access_token_hash: str) -> bool:
        """Mark a session as revoked."""
        stmt = (
            update(UserSession)
            .where(UserSession.access_token_hash == access_token_hash)
            .values(revoked_at=datetime.now(timezone.utc))
        )
        res = await db.execute(stmt)
        return res.rowcount > 0

    async def revoke_refresh_session(self, db: AsyncSession, refresh_token_hash: str) -> bool:
        """Mark a session as revoked using its refresh token hash."""
        stmt = (
            update(UserSession)
            .where(UserSession.refresh_token_hash == refresh_token_hash)
            .values(revoked_at=datetime.now(timezone.utc))
        )
        res = await db.execute(stmt)
        return res.rowcount > 0

    # ── Login Security & Reset Tokens ──────────────────────────────────────────
    async def log_login_attempt(
        self,
        db: AsyncSession,
        email: str,
        was_successful: bool,
        failure_reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ) -> LoginAttempt:
        """Log a user login attempt for auditing and lock analysis."""
        attempt = LoginAttempt(
            user_id=user_id,
            email=email.lower(),
            was_successful=was_successful,
            failure_reason=failure_reason,
            ip_address=ip_address
        )
        db.add(attempt)
        await db.flush()
        return attempt

    async def create_password_reset_token(
        self, db: AsyncSession, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> PasswordResetToken:
        """Insert a password reset token."""
        reset_token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        db.add(reset_token)
        await db.flush()
        return reset_token

    async def get_valid_reset_token(
        self, db: AsyncSession, token_hash: str
    ) -> Optional[PasswordResetToken]:
        """Fetch password reset token if it hasn't expired and hasn't been used."""
        stmt = select(PasswordResetToken).where(
            (PasswordResetToken.token_hash == token_hash)
            & (PasswordResetToken.used_at.is_(None))
            & (PasswordResetToken.expires_at > datetime.now(timezone.utc))
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()


# Instantiate singleton repository
user_repo = UserRepository()
