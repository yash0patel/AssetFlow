"""
app/api/v1/auth.py
──────────────────
Authentication API router.
"""

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_token_from_header
from app.models.user import User
from app.repositories.user_repository import user_repo
from app.schemas.auth import (
    ForgotPasswordRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import auth_service

router = APIRouter()


class RefreshRequest(BaseModel):
    refresh_token: str


def build_user_response(user: User, role_name: str) -> UserResponse:
    """Helper to convert a User model and its role to UserResponse schema."""
    first_name = user.profile.first_name if user.profile else ""
    last_name = user.profile.last_name if user.profile else None
    name = f"{first_name} {last_name}".strip() if last_name else first_name
    
    return UserResponse(
        id=user.id,
        name=name or user.email,
        email=user.email,
        role=role_name,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account with default employee role and profile.
    Automatically logs the user in and starts a session.
    """
    user = await auth_service.register_user(
        db=db,
        fullName=payload.fullName,
        email=payload.email,
        password=payload.password,
    )
    
    # Establish session
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    access_token, refresh_token, _ = await auth_service.create_tokens_and_session(
        db=db,
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    role_name = await user_repo.get_user_role_name(db, user.id)
    user_data = build_user_response(user, role_name)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_data,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a user using email and password.
    Returns access and refresh tokens along with user profile metadata.
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Verify user credentials
    user = await auth_service.authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
        ip_address=ip_address,
    )
    
    # Create active database session
    access_token, refresh_token, _ = await auth_service.create_tokens_and_session(
        db=db,
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    role_name = await user_repo.get_user_role_name(db, user.id)
    user_data = build_user_response(user, role_name)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_data,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(get_token_from_header),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke the active database session of the user.
    """
    await auth_service.logout_user(db, token)
    return {"detail": "Successfully logged out."}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Provide a valid refresh token to get a new access token and rotate the refresh token.
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    access_token, refresh_token, user = await auth_service.refresh_session(
        db=db,
        refresh_token=payload.refresh_token,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    role_name = await user_repo.get_user_role_name(db, user.id)
    user_data = build_user_response(user, role_name)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_data,
    )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers password reset token generation.
    Returns 200 OK regardless of whether the email exists for privacy/security.
    """
    token = await auth_service.generate_password_reset_token(db, payload.email)
    if token:
        # In a real environment, we'd send an email. For local development/testing, we log it.
        print(f"\n[DEV MODE] Password reset token for {payload.email}: {token}\n")
        
    return {"detail": "If the email is registered, a password reset link has been sent."}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch the profile details of the currently authenticated user.
    """
    role_name = await user_repo.get_user_role_name(db, current_user.id)
    return build_user_response(current_user, role_name)
