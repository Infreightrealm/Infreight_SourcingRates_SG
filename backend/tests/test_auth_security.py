"""
Security and authentication unit tests for Infreight rate automation platform.
Tests compliance with AUTH-AND-ADMIN.md.
"""

import pytest
import time
from uuid import uuid4
from datetime import datetime, timedelta
from fastapi import HTTPException

from services.auth_service import (
    hash_password,
    verify_password,
    DUMMY_HASH,
    validate_username,
    validate_password,
    validate_display_name,
    hash_token,
    check_rate_limit,
    record_login_failure,
    clear_login_failures,
    public_user_dict,
)
from models.user import User, AuthSession


def test_scrypt_password_hashing_and_verification():
    """Verify scrypt hashing produces correct scheme, salt, and verifies securely."""
    pw = "SuperSecret_1234!"
    hashed = hash_password(pw)

    assert hashed.startswith("scrypt$")
    parts = hashed.split("$")
    assert len(parts) == 3
    salt_hex = parts[1]
    key_hex = parts[2]
    assert len(salt_hex) == 32  # 16 bytes = 32 hex chars
    assert len(key_hex) == 128  # 64 bytes = 128 hex chars

    # Correct password succeeds
    assert verify_password(pw, hashed) is True
    # Wrong password fails
    assert verify_password("WrongPassword99", hashed) is False
    # Empty or invalid hash fails gracefully
    assert verify_password(pw, None) is False
    assert verify_password(pw, "invalid_hash") is False


def test_dummy_hash_timing_mitigation():
    """Verify dummy hash exists and evaluates in constant time without throwing."""
    assert DUMMY_HASH.startswith("scrypt$")
    assert verify_password("arbitrary_password", DUMMY_HASH) is False


def test_username_validation():
    """Verify username pattern: ^[a-z0-9._-]{3,40}$ lowercased."""
    assert validate_username("Brian.Lee") == "brian.lee"
    assert validate_username("user_123-prod") == "user_123-prod"

    with pytest.raises(HTTPException) as exc:
        validate_username("ab")  # Too short
    assert exc.value.status_code == 400

    with pytest.raises(HTTPException) as exc:
        validate_username("bad username with spaces")
    assert exc.value.status_code == 400

    with pytest.raises(HTTPException) as exc:
        validate_username("bad@symbol!")
    assert exc.value.status_code == 400


def test_password_validation():
    """Verify password length: 8 to 200 characters."""
    validate_password("12345678")  # Minimum valid length
    validate_password("a" * 200)   # Maximum valid length

    with pytest.raises(HTTPException) as exc:
        validate_password("short")
    assert exc.value.status_code == 400

    with pytest.raises(HTTPException) as exc:
        validate_password("a" * 201)
    assert exc.value.status_code == 400


def test_display_name_validation():
    """Verify display name trims and checks length."""
    assert validate_display_name("  Brian  Logistics  ") == "Brian Logistics"

    with pytest.raises(HTTPException):
        validate_display_name("")

    with pytest.raises(HTTPException):
        validate_display_name("a" * 61)


def test_rate_limiting():
    """Verify in-memory rate limiter locks after 8 failures in 15 minutes."""
    ip = "192.168.1.100"
    user = "rate_limit_test_user"

    # Reset any prior failures
    clear_login_failures(ip, user)

    # 7 failures should pass check_rate_limit
    for _ in range(7):
        record_login_failure(ip, user)
        check_rate_limit(ip, user)

    # 8th failure should trigger HTTP 429
    record_login_failure(ip, user)
    with pytest.raises(HTTPException) as exc:
        check_rate_limit(ip, user)
    assert exc.value.status_code == 429

    # Successful login clears failures
    clear_login_failures(ip, user)
    check_rate_limit(ip, user)  # Should not raise


def test_token_hashing_and_public_user():
    """Verify token is hashed with SHA-256 and public_user_dict never reveals password_hash."""
    raw_token = "some_random_session_token_32_bytes_long"
    thash = hash_token(raw_token)
    assert len(thash) == 64  # SHA-256 hex length

    user = User(
        id=uuid4(),
        username="brian",
        display_name="Brian",
        name="Brian",
        password_hash="scrypt$dummy$secret",
        role="admin",
        status="active",
        is_active=True,
        created_at=datetime.utcnow(),
    )

    public = public_user_dict(user)
    assert "password_hash" not in public
    assert public["username"] == "brian"
    assert public["role"] == "admin"
    assert public["needs_password"] is False

    # Legacy user with None password
    legacy_user = User(
        id=uuid4(),
        username="legacy_brian",
        display_name="Legacy Brian",
        name="Legacy Brian",
        password_hash=None,
        role="admin",
        status="active",
        is_active=True,
    )
    public_legacy = public_user_dict(legacy_user)
    assert public_legacy["needs_password"] is True
