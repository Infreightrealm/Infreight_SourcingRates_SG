"""
Authentication and security service for Infreight Sourcing.

Implements the security protocol described in AUTH-AND-ADMIN.md:
- Scrypt password hashing with random 16-byte salt (n=16384, r=8, p=1, dklen=64).
- Constant-time password verification (hmac.compare_digest).
- Dummy hash verification for non-existent users (timing attack mitigation).
- Cryptographic session tokens (32 bytes URL-safe), stored as SHA-256 hex hashes.
- In-memory rate limiting (max 8 failures per 15 minutes per IP + username).
- Audit logging for administrative and consequential user actions.
"""

import os
import re
import time
import secrets
import hashlib
import hmac
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Request

from models.user import User, AuthSession, AuditLog

SESSION_COOKIE = "infreight_session"
SESSION_TTL_DAYS = 14
SESSION_TTL_SECONDS = SESSION_TTL_DAYS * 24 * 60 * 60
LOGIN_WINDOW_SECONDS = 15 * 60  # 15 minutes
MAX_LOGIN_FAILURES = 8
USERNAME_PATTERN = re.compile(r"^[a-z0-9._-]{3,40}$")

# In-memory failure tracking: key -> list of timestamp floats
_login_failures: Dict[str, List[float]] = {}


def hash_password(password: str) -> str:
    """Hash a password using scrypt with a random 16-byte salt."""
    salt = secrets.token_bytes(16)
    key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        maxmem=0,
        dklen=64,
    )
    return f"scrypt${salt.hex()}${key.hex()}"


def verify_password(password: str, stored_hash: Optional[str]) -> bool:
    """Verify password against a stored scrypt hash using constant-time comparison."""
    if not stored_hash:
        return False
    parts = stored_hash.split("$")
    if len(parts) != 3 or parts[0] != "scrypt":
        return False
    try:
        salt = bytes.fromhex(parts[1])
        expected_key = bytes.fromhex(parts[2])
        actual_key = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=16384,
            r=8,
            p=1,
            maxmem=0,
            dklen=len(expected_key),
        )
        return hmac.compare_digest(actual_key, expected_key)
    except Exception:
        return False


# Precomputed dummy hash so unknown usernames still pay the scrypt cost
DUMMY_HASH = hash_password(secrets.token_hex(16))


def normalize_username(username: str) -> str:
    """Normalize username to trimmed lowercase."""
    return str(username or "").strip().lower()


def validate_username(username: str) -> str:
    """Validate username according to the security spec (3-40 lowercase letters, numbers, ., -, _)."""
    norm = normalize_username(username)
    if not USERNAME_PATTERN.match(norm):
        raise HTTPException(
            status_code=400,
            detail="Username must be 3–40 characters: lowercase letters, numbers, dot, dash, or underscore.",
        )
    return norm


def validate_password(password: str) -> None:
    """Validate password length (8-200 characters)."""
    if not isinstance(password, str) or len(password) < 8 or len(password) > 200:
        raise HTTPException(
            status_code=400,
            detail="Password must be between 8 and 200 characters.",
        )


def validate_display_name(display_name: str) -> str:
    """Validate user's display name."""
    clean = re.sub(r"\s+", " ", str(display_name or "").strip())
    if not clean or len(clean) > 60:
        raise HTTPException(
            status_code=400,
            detail="Display name is required (up to 60 characters).",
        )
    return clean


def hash_token(token: str) -> str:
    """Compute SHA-256 hex digest of a raw session token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def check_rate_limit(client_ip: str, username: str) -> None:
    """Enforce login attempt rate limiting: max 8 failures per 15 minutes."""
    key = f"{client_ip}|{normalize_username(username)}"
    now = time.time()
    failures = [t for t in _login_failures.get(key, []) if now - t < LOGIN_WINDOW_SECONDS]
    _login_failures[key] = failures
    if len(failures) >= MAX_LOGIN_FAILURES:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Please try again in 15 minutes.",
        )


def record_login_failure(client_ip: str, username: str) -> None:
    """Record a failed login attempt for rate limiting."""
    key = f"{client_ip}|{normalize_username(username)}"
    now = time.time()
    # Garbage collect if dict grows too large
    if len(_login_failures) > 5000:
        _login_failures.clear()
    failures = [t for t in _login_failures.get(key, []) if now - t < LOGIN_WINDOW_SECONDS]
    failures.append(now)
    _login_failures[key] = failures


def clear_login_failures(client_ip: str, username: str) -> None:
    """Clear failed login attempts upon successful authentication."""
    key = f"{client_ip}|{normalize_username(username)}"
    _login_failures.pop(key, None)


async def create_session(db_session: AsyncSession, user: User) -> str:
    """Generate a random 32-byte session token, store its SHA-256 hash in DB, and return raw token."""
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    expires_at = datetime.utcnow() + timedelta(days=SESSION_TTL_DAYS)

    session_record = AuthSession(
        token_hash=token_hash,
        user_id=user.id,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
    )
    db_session.add(session_record)
    user.last_login_at = datetime.utcnow()
    await db_session.commit()
    return raw_token


async def get_user_for_token(db_session: AsyncSession, token: str) -> Optional[User]:
    """Resolve raw session token to an active user. Deletes expired sessions."""
    if not token:
        return None
    token_hash = hash_token(token)
    query = select(AuthSession).where(AuthSession.token_hash == token_hash)
    result = await db_session.execute(query)
    session_record = result.scalar_one_or_none()

    if not session_record:
        return None

    if session_record.expires_at <= datetime.utcnow():
        await db_session.delete(session_record)
        await db_session.commit()
        return None

    user_query = select(User).where(User.id == session_record.user_id)
    user_res = await db_session.execute(user_query)
    user = user_res.scalar_one_or_none()

    if not user or user.status != "active" or not user.is_active:
        return None

    return user


async def revoke_session_token(db_session: AsyncSession, token: str) -> None:
    """Revoke a single session token."""
    if not token:
        return
    token_hash = hash_token(token)
    await db_session.execute(delete(AuthSession).where(AuthSession.token_hash == token_hash))
    await db_session.commit()


async def revoke_user_sessions(db_session: AsyncSession, user_id: UUID) -> None:
    """Revoke all sessions belonging to a user (used on disable, delete, or password reset)."""
    await db_session.execute(delete(AuthSession).where(AuthSession.user_id == user_id))
    await db_session.commit()


async def record_audit_event(
    db_session: AsyncSession,
    actor_username: str,
    action: str,
    detail: str = "",
) -> None:
    """Append an event to the audit log."""
    log_entry = AuditLog(
        actor_username=str(actor_username or "system"),
        action=str(action),
        detail=str(detail)[:500],
        created_at=datetime.utcnow(),
    )
    db_session.add(log_entry)
    await db_session.commit()


def get_client_ip(request: Request) -> str:
    """Extract client IP addressing forwarded proxy headers."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


def public_user_dict(user: User) -> dict:
    """Serialize a User for client consumption, omitting password_hash."""
    return {
        "id": str(user.id),
        "username": user.username or (user.name.lower() if user.name else ""),
        "display_name": user.display_name or user.name,
        "name": user.name or user.display_name,
        "role": user.role or "user",
        "status": user.status or ("active" if user.is_active else "disabled"),
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "approved_at": user.approved_at.isoformat() if user.approved_at else None,
        "approved_by": user.approved_by,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "needs_password": user.password_hash is None,
        "avatar_url": getattr(user, "avatar_url", None),
        "title_or_role_desc": getattr(user, "title_or_role_desc", None),
    }
