"""
Authentication routes for Infreight Sourcing.

Provides:
- POST /api/auth/signup: Register new user (or initial admin)
- POST /api/auth/login: Authenticate with username and password
- POST /api/auth/setup-password: Set mandatory password for legacy user accounts
- POST /api/auth/logout: Revoke active session
- GET  /api/auth/me: Inspect currently authenticated user
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Header
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_session
from models.user import User
from services.auth_service import (
    SESSION_COOKIE,
    SESSION_TTL_SECONDS,
    hash_password,
    verify_password,
    DUMMY_HASH,
    normalize_username,
    validate_username,
    validate_password,
    validate_display_name,
    create_session,
    get_user_for_token,
    revoke_session_token,
    check_rate_limit,
    record_login_failure,
    clear_login_failures,
    record_audit_event,
    get_client_ip,
    public_user_dict,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class SignupRequest(BaseModel):
    displayName: str = Field(..., max_length=60)
    username: str = Field(..., min_length=3, max_length=40)
    password: str = Field(..., min_length=8, max_length=200)


class LoginRequest(BaseModel):
    username: str
    password: str


class SetupPasswordRequest(BaseModel):
    username: str
    password: str = Field(..., min_length=8, max_length=200)
    confirm_password: Optional[str] = None


def set_session_cookie(response: Response, request: Request, token: str) -> None:
    """Set the HttpOnly session cookie on the outgoing response."""
    is_secure = (
        request.headers.get("x-forwarded-proto") == "https"
        or request.url.scheme == "https"
    )
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        samesite="lax",
        secure=is_secure,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    """Clear session cookie on logout."""
    response.delete_cookie(key=SESSION_COOKIE, path="/")


async def get_current_user_optional(
    request: Request,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """Dependency that returns the current User if valid token is provided, or None."""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    if not token:
        token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    return await get_user_for_token(session, token)


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    """Dependency that strictly requires an authenticated active member."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return user


async def require_admin(
    user: User = Depends(get_current_user),
) -> User:
    """Dependency that strictly requires an active admin user."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    return user


@router.post("/signup")
async def signup(
    request_data: SignupRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    """Register an account. If no accounts exist, the first account becomes an active admin."""
    norm_username = validate_username(request_data.username)
    display_name = validate_display_name(request_data.displayName)
    validate_password(request_data.password)

    # Check for username collision
    existing = await session.execute(
        select(User).where(
            func.lower(User.username) == norm_username
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="That username is already taken.")

    # Check if this is the first account on the platform
    count_res = await session.execute(select(func.count(User.id)))
    total_users = count_res.scalar() or 0
    is_first = total_users == 0

    role = "admin" if is_first else "user"
    status = "active" if is_first else "pending"
    now = datetime.utcnow()

    hashed_pw = hash_password(request_data.password)
    user = User(
        username=norm_username,
        display_name=display_name,
        name=display_name,
        password_hash=hashed_pw,
        role=role,
        status=status,
        is_active=(status == "active"),
        created_at=now,
        approved_at=now if is_first else None,
        approved_by="system" if is_first else None,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    await record_audit_event(
        session,
        actor_username=user.username,
        action="signup",
        detail=f"Registered account (role: {role}, status: {status})",
    )

    if status == "active":
        token = await create_session(session, user)
        set_session_cookie(response, request, token)
        return {
            "user": public_user_dict(user),
            "token": token,
            "message": "Account created and activated as Administrator.",
        }

    return {
        "user": public_user_dict(user),
        "token": None,
        "message": "Access request submitted. An admin will review and approve your account.",
    }


@router.post("/login")
async def login(
    request_data: LoginRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    """Authenticate with username and password."""
    client_ip = get_client_ip(request)
    norm_username = normalize_username(request_data.username)
    check_rate_limit(client_ip, norm_username)

    # Search by username or display name safely
    query = select(User).where(
        (func.lower(User.username) == norm_username)
        | (func.lower(User.name) == norm_username)
    ).order_by(User.created_at.asc())
    result = await session.execute(query)
    matched_users = result.scalars().all()

    exact_match = [u for u in matched_users if u.username and u.username.lower() == norm_username]
    candidates = exact_match if exact_match else matched_users

    user = None
    if candidates:
        for c in candidates:
            if c.password_hash and verify_password(request_data.password, c.password_hash):
                user = c
                break
        if not user:
            user = candidates[0]

    # If user doesn't exist, compute dummy hash to prevent timing attack
    if not user:
        verify_password(request_data.password, DUMMY_HASH)
        record_login_failure(client_ip, norm_username)
        raise HTTPException(status_code=401, detail="Incorrect username or password.")

    # Check if this is a legacy account requiring mandatory password creation
    if user.password_hash is None:
        raise HTTPException(
            status_code=428,
            detail={
                "code": "NEEDS_PASSWORD",
                "username": user.username or norm_username,
                "display_name": user.display_name or user.name,
                "message": "Password setup required: All existing accounts must set a new password to continue.",
            },
        )

    # Verify password against scrypt hash
    if not verify_password(request_data.password, user.password_hash):
        record_login_failure(client_ip, norm_username)
        raise HTTPException(status_code=401, detail="Incorrect username or password.")

    clear_login_failures(client_ip, norm_username)

    if user.status == "pending":
        raise HTTPException(
            status_code=403,
            detail="Your account is waiting for admin approval.",
        )
    if user.status != "active" or not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Your account has been disabled. Contact an administrator.",
        )

    token = await create_session(session, user)
    set_session_cookie(response, request, token)

    await record_audit_event(
        session,
        actor_username=user.username,
        action="login",
        detail=f"Signed in from {client_ip}",
    )

    return {
        "user": public_user_dict(user),
        "token": token,
        "message": "Signed in successfully.",
    }


@router.post("/setup-password")
async def setup_password(
    request_data: SetupPasswordRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    """Set mandatory password for legacy user accounts that currently lack a password."""
    norm_username = normalize_username(request_data.username)
    if request_data.confirm_password and request_data.password != request_data.confirm_password:
        raise HTTPException(status_code=400, detail="The passwords do not match.")

    validate_password(request_data.password)

    query = select(User).where(
        (func.lower(User.username) == norm_username)
        | (func.lower(User.name) == norm_username)
    ).order_by(User.created_at.asc())
    result = await session.execute(query)
    matched_users = result.scalars().all()

    if not matched_users:
        raise HTTPException(status_code=404, detail="User account not found.")

    exact_match = [u for u in matched_users if u.username and u.username.lower() == norm_username]
    candidates = exact_match if exact_match else matched_users

    # Select candidate that still needs a password setup, else fallback to first candidate
    user = next((u for u in candidates if u.password_hash is None), candidates[0])

    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    if user.password_hash is not None:
        raise HTTPException(
            status_code=400,
            detail="A password is already set for this account. Please sign in or contact an admin.",
        )

    # Set password
    user.password_hash = hash_password(request_data.password)
    user.status = "active"
    user.is_active = True
    if not user.username:
        user.username = norm_username
    if not user.display_name:
        user.display_name = user.name or norm_username.capitalize()

    token = await create_session(session, user)
    set_session_cookie(response, request, token)

    await record_audit_event(
        session,
        actor_username=user.username,
        action="setup_password",
        detail="Initialized password for existing account",
    )

    return {
        "user": public_user_dict(user),
        "token": token,
        "message": "Password set successfully! You are now signed in.",
    }


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
):
    """Revoke active session and delete session cookie."""
    token = request.cookies.get(SESSION_COOKIE)
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
    if token:
        await revoke_session_token(session, token)
    clear_session_cookie(response)
    return {"status": "SUCCESS", "message": "Signed out successfully."}


@router.get("/me")
async def get_me(
    user: User = Depends(get_current_user),
):
    """Get profile of currently signed-in user."""
    return {"user": public_user_dict(user)}
