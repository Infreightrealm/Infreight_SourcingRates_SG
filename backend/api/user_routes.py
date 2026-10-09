from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from models.database import get_session
from models.user import User, AuditLog
from models.rate_search import RateSearch, CarrierSearchResult
from models.quote import Quote
from services.auth_service import (
    hash_password,
    validate_password,
    revoke_user_sessions,
    record_audit_event,
    public_user_dict,
)
from api.auth_routes import get_current_user_optional, get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


class UserSchema(BaseModel):
    id: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    name: Optional[str] = None
    role: str = "user"
    status: str = "pending"
    is_active: bool = True
    created_at: Optional[str] = None
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None
    last_login_at: Optional[str] = None
    needs_password: bool = False

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    name: str


class AdminLoginRequest(BaseModel):
    password: str


class PortsConfigResponse(BaseModel):
    popular_ports: List[str]
    boosted_countries: List[str]


class PortsConfigUpdateRequest(BaseModel):
    popular_ports: List[str]
    boosted_countries: List[str]


class RoleUpdateRequest(BaseModel):
    role: str = Field(..., pattern="^(admin|user)$")


class PasswordResetRequest(BaseModel):
    password: str = Field(..., min_length=8, max_length=200)


async def verify_admin_access(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_admin_password: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Verify that caller has admin privileges via session cookie, Bearer token, or legacy header."""
    # 1. Check authenticated user session
    user = await get_current_user_optional(request, authorization, session)
    if user and user.role == "admin" and user.status == "active":
        return user

    # 2. Backwards-compatibility fallback for legacy header brian_infreight
    if x_admin_password == "brian_infreight":
        query = select(User).where(User.role == "admin")
        admin_user = (await session.execute(query)).scalars().first()
        if admin_user:
            return admin_user
        # Dummy admin fallback
        return User(username="admin", display_name="Admin", role="admin", status="active")

    raise HTTPException(status_code=403, detail="Admin privileges required.")


@router.get("", response_model=List[UserSchema])
async def list_users(session: AsyncSession = Depends(get_session)):
    query = select(User).order_by(User.name, User.username)
    result = await session.execute(query)
    users = result.scalars().all()
    return [UserSchema(**public_user_dict(u)) for u in users]


@router.delete("/reset-all")
async def reset_all_users(
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Delete all user accounts except the acting administrator."""
    from sqlalchemy import delete
    from models.user import AuthSession

    await session.execute(delete(AuthSession).where(AuthSession.user_id != actor.id))
    await session.execute(delete(User).where(User.id != actor.id))
    await session.commit()

    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="reset_all_users",
        detail="Reset all user sessions and accounts except the active administrator.",
    )
    return {"status": "SUCCESS", "message": "All user accounts reset except acting admin."}


@router.post("/validate-session", response_model=UserSchema)
async def validate_session(request: UserCreateRequest, session: AsyncSession = Depends(get_session)):
    """Validate if an existing browser session user still exists in DB."""
    name = request.name.strip()
    if not name:
        raise HTTPException(400, "Name cannot be empty")

    query = select(User).where(
        (func.lower(User.username) == name.lower())
        | (func.lower(User.name) == name.lower())
    ).order_by(User.created_at.asc())
    user = (await session.execute(query)).scalars().first()

    if not user:
        raise HTTPException(404, "Session reset. Please log in fresh.")

    if not user.is_active or user.status != "active":
        raise HTTPException(403, "This user account has been deactivated.")

    return UserSchema(**public_user_dict(user))


@router.post("/login", response_model=UserSchema)
async def legacy_login_user(request: UserCreateRequest, session: AsyncSession = Depends(get_session)):
    """Legacy user name-only login endpoint with guidance to password setup."""
    name = request.name.strip()
    if not name:
        raise HTTPException(400, "Name cannot be empty")

    query = select(User).where(
        (func.lower(User.username) == name.lower())
        | (func.lower(User.name) == name.lower())
    ).order_by(User.created_at.asc())
    user = (await session.execute(query)).scalars().first()

    if not user:
        # Create as pending user
        user = User(
            username=name.lower(),
            display_name=name,
            name=name,
            role="user",
            status="pending",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    if user.password_hash is None:
        raise HTTPException(
            status_code=428,
            detail={
                "code": "NEEDS_PASSWORD",
                "username": user.username or name.lower(),
                "display_name": user.display_name or name,
                "message": "Password setup required: All existing accounts must set a new password to continue.",
            },
        )

    if not user.is_active or user.status != "active":
        raise HTTPException(403, "This user account has been deactivated.")

    return UserSchema(**public_user_dict(user))


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Delete a user account with self-protection guard."""
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(400, "Invalid user ID format")

    if actor.id == uid:
        raise HTTPException(400, "You cannot delete your own account from the admin dashboard.")

    query = select(User).where(User.id == uid)
    user = (await session.execute(query)).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    target_name = user.username or user.name or str(user.id)
    await revoke_user_sessions(session, user.id)
    await session.delete(user)
    await session.commit()

    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="delete_user",
        detail=f"Deleted account @{target_name}",
    )
    return {"status": "SUCCESS"}


# ============================================================
# Admin Management Router
# ============================================================
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])


@admin_router.post("/verify")
async def verify_admin(
    request: AdminLoginRequest,
    actor: User = Depends(verify_admin_access),
):
    """Admin verification endpoint."""
    return {"status": "SUCCESS"}


@admin_router.get("/overview")
async def get_admin_overview(
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Return consolidated user registry, pending requests, audit log, and platform stats."""
    # 1. All users
    users_query = select(User).order_by(desc(User.created_at))
    users_result = await session.execute(users_query)
    all_users = users_result.scalars().all()

    # 2. Platform stats
    total_searches = (await session.execute(select(func.count(RateSearch.id)))).scalar() or 0
    total_quotes = (await session.execute(select(func.count(Quote.id)))).scalar() or 0

    pending_count = sum(1 for u in all_users if u.status == "pending")
    active_count = sum(1 for u in all_users if u.status == "active" and u.is_active)

    # 3. Recent audit log entries (last 500)
    audit_query = select(AuditLog).order_by(desc(AuditLog.created_at)).limit(500)
    audit_res = await session.execute(audit_query)
    audit_logs = audit_res.scalars().all()

    return {
        "users": [public_user_dict(u) for u in all_users],
        "stats": {
            "totalUsers": len(all_users),
            "activeUsers": active_count,
            "pendingUsers": pending_count,
            "totalSearches": total_searches,
            "totalQuotes": total_quotes,
        },
        "audit": [
            {
                "id": str(a.id),
                "at": a.created_at.isoformat() if a.created_at else None,
                "actor": a.actor_username,
                "action": a.action,
                "detail": a.detail,
            }
            for a in audit_logs
        ],
        "me": public_user_dict(actor),
    }


@admin_router.post("/users/{user_id}/approve")
async def approve_user(
    user_id: str,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Approve a pending access request."""
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(400, "Invalid user ID")

    query = select(User).where(User.id == uid)
    user = (await session.execute(query)).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    if user.status != "pending":
        raise HTTPException(409, "User is not in pending status")

    user.status = "active"
    user.is_active = True
    user.approved_at = datetime.utcnow()
    user.approved_by = actor.username or "admin"
    await session.commit()

    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="approve_user",
        detail=f"Approved access for @{user.username or user.name}",
    )
    return {"status": "SUCCESS", "user": public_user_dict(user)}


@admin_router.post("/users/{user_id}/reject")
async def reject_user(
    user_id: str,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Reject and remove a pending user registration request."""
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(400, "Invalid user ID")

    if actor.id == uid:
        raise HTTPException(400, "You cannot reject your own account")

    query = select(User).where(User.id == uid)
    user = (await session.execute(query)).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    target_name = user.username or user.name
    await revoke_user_sessions(session, user.id)
    await session.delete(user)
    await session.commit()

    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="reject_user",
        detail=f"Rejected access request for @{target_name}",
    )
    return {"status": "SUCCESS", "message": f"Rejected request for @{target_name}"}


@admin_router.post("/users/{user_id}/disable")
async def disable_user(
    user_id: str,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Disable a user account and immediately revoke all active sessions."""
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(400, "Invalid user ID")

    if actor.id == uid:
        raise HTTPException(400, "You cannot disable your own account.")

    query = select(User).where(User.id == uid)
    user = (await session.execute(query)).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    user.status = "disabled"
    user.is_active = False
    await revoke_user_sessions(session, user.id)
    await session.commit()

    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="disable_user",
        detail=f"Disabled account @{user.username or user.name} and revoked active sessions",
    )
    return {"status": "SUCCESS", "user": public_user_dict(user)}


@admin_router.post("/users/{user_id}/enable")
async def enable_user(
    user_id: str,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Enable a previously disabled user account."""
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(400, "Invalid user ID")

    query = select(User).where(User.id == uid)
    user = (await session.execute(query)).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    user.status = "active"
    user.is_active = True
    await session.commit()

    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="enable_user",
        detail=f"Enabled account @{user.username or user.name}",
    )
    return {"status": "SUCCESS", "user": public_user_dict(user)}


@admin_router.post("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    request: RoleUpdateRequest,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Promote to admin or demote to user."""
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(400, "Invalid user ID")

    if actor.id == uid:
        raise HTTPException(400, "You cannot alter your own administrative role.")

    query = select(User).where(User.id == uid)
    user = (await session.execute(query)).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    user.role = request.role
    await session.commit()

    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="change_role",
        detail=f"Changed @{user.username or user.name} role to '{request.role}'",
    )
    return {"status": "SUCCESS", "user": public_user_dict(user)}


@admin_router.post("/users/{user_id}/password")
async def reset_user_password(
    user_id: str,
    request: PasswordResetRequest,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Admin-directed password reset. Sets new password and immediately revokes all active sessions."""
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(400, "Invalid user ID")

    query = select(User).where(User.id == uid)
    user = (await session.execute(query)).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    validate_password(request.password)
    user.password_hash = hash_password(request.password)
    await revoke_user_sessions(session, user.id)
    await session.commit()

    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="reset_password",
        detail=f"Reset password for @{user.username or user.name} and revoked active sessions",
    )
    return {"status": "SUCCESS", "message": f"Password reset for @{user.username or user.name}"}


@admin_router.delete("/users/{user_id}")
@admin_router.post("/users/{user_id}/delete")
async def admin_delete_user(
    user_id: str,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Admin-directed account deletion with self-protection guard and session revocation."""
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(400, "Invalid user ID format")

    if actor.id == uid:
        raise HTTPException(400, "You cannot delete your own account from the admin dashboard.")

    query = select(User).where(User.id == uid)
    user = (await session.execute(query)).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    target_name = user.username or user.name or str(user.id)
    await revoke_user_sessions(session, user.id)
    await session.delete(user)
    await session.commit()

    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="delete_user",
        detail=f"Deleted account @{target_name}",
    )
    return {"status": "SUCCESS", "message": f"User @{target_name} deleted."}


# ============================================================
# Existing System Config Routes (Protected by verify_admin_access)
# ============================================================

@admin_router.get("/config/ports", response_model=PortsConfigResponse)
async def get_ports_config(actor: User = Depends(verify_admin_access)):
    from services.port_manager import get_popular_ports_config
    return get_popular_ports_config()


@admin_router.post("/config/ports")
async def save_ports_config(
    request: PortsConfigUpdateRequest,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    from services.port_manager import update_popular_ports_config
    update_popular_ports_config(request.popular_ports, request.boosted_countries)
    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="update_ports_config",
        detail=f"Updated popular ports ({len(request.popular_ports)}) & boosted countries ({len(request.boosted_countries)})",
    )
    return {"status": "SUCCESS"}


class CarrierOverrideRequest(BaseModel):
    carrier: str
    key: str
    override_text: Optional[str] = None


@admin_router.get("/carrier-overrides")
async def fetch_carrier_overrides(
    carrier: Optional[str] = None,
    actor: User = Depends(verify_admin_access),
):
    from services.port_manager import get_carrier_overrides
    return get_carrier_overrides(carrier)


@admin_router.post("/carrier-overrides")
async def save_carrier_override(
    request: CarrierOverrideRequest,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    if not request.carrier or not request.key or not request.override_text:
        raise HTTPException(status_code=400, detail="carrier, key, and override_text are required")
    from services.port_manager import add_carrier_override
    add_carrier_override(request.carrier, request.key, request.override_text)
    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="save_carrier_override",
        detail=f"Override for {request.carrier.upper()}: '{request.key}' -> '{request.override_text}'",
    )
    return {"status": "SUCCESS"}


@admin_router.delete("/carrier-overrides")
async def delete_carrier_override_endpoint(
    request: CarrierOverrideRequest,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    if not request.carrier or not request.key:
        raise HTTPException(status_code=400, detail="carrier and key are required")
    from services.port_manager import delete_carrier_override
    delete_carrier_override(request.carrier, request.key)
    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="delete_carrier_override",
        detail=f"Deleted override for {request.carrier.upper()}: '{request.key}'",
    )
    return {"status": "SUCCESS"}


class CarrierSwitchRequest(BaseModel):
    enabled: bool
    reason: Optional[str] = None


@admin_router.put("/carriers/{carrier_code}")
async def switch_carrier(
    carrier_code: str,
    request: CarrierSwitchRequest,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Switch a carrier on or off for everyone, e.g. while its site is down."""
    from services.carrier_switches import set_switch
    try:
        entry = set_switch(carrier_code, request.enabled, request.reason, actor.username or "admin")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="switch_carrier",
        detail=f"{'Switched on' if request.enabled else 'Switched off'} {carrier_code.upper()}"
        + (f": {entry['reason']}" if entry.get("reason") else ""),
    )
    return entry


@admin_router.get("/workers")
async def list_workers(actor: User = Depends(verify_admin_access)):
    """Worker machines (e.g. the office laptop running Maersk) and whether they're online."""
    from services.remote_worker import online_workers
    try:
        return {"workers": await online_workers()}
    except Exception:
        return {"workers": []}


@admin_router.get("/carrier-session/{carrier}")
async def get_carrier_session(carrier: str, actor: User = Depends(verify_admin_access)):
    """The uploaded saved login for a carrier, or null."""
    from services.carrier_sessions import session_info
    return {"session": session_info(carrier.lower())}


@admin_router.post("/carrier-session/{carrier}")
async def upload_carrier_session(
    carrier: str,
    request: Request,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Upload a saved login (Playwright storage-state JSON from scripts/export_maersk_login.py)."""
    from services.carrier_sessions import save_session
    try:
        state = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="The file isn't valid JSON.")
    try:
        info = save_session(carrier.lower(), state, actor.username or "admin")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="upload_carrier_session",
        detail=f"Uploaded a saved {carrier.lower()} login ({info['cookies']} cookies)",
    )
    return {"session": info}


@admin_router.delete("/carrier-session/{carrier}")
async def remove_carrier_session(
    carrier: str,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    from services.carrier_sessions import delete_session
    removed = delete_session(carrier.lower())
    if removed:
        await record_audit_event(
            session,
            actor_username=actor.username or "admin",
            action="delete_carrier_session",
            detail=f"Removed the uploaded {carrier.lower()} login",
        )
    return {"removed": removed}


# Carrier codes on search results -> the keys port name fixes are stored under.
_FIX_CARRIER_KEYS = {
    "MAERSK": "maersk",
    "CMA_CGM": "cma",
    "ONE": "one",
    "HAPAG_LLOYD": "hapag",
    "HAPAG_LLOYD_API": "hapag",
    "MSC": "msc",
    "GREENX": "greenx",
    "OOCL": "oocl",
}


@admin_router.get("/port-fixes")
async def fetch_port_fixes(
    days: int = 14,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Saved port name fixes, marked built in or admin-added, and the ports each
    carrier's own search couldn't find in the last `days` days."""
    from services.port_manager import PortManager, CARRIER_PORT_OVERRIDES

    pm = PortManager()
    dynamic: Dict[str, Dict[str, str]] = pm.get_carrier_overrides() or {}
    user_saved: Dict[str, Dict[str, str]] = getattr(pm, "_user_carrier_overrides", {}) or {}

    def port_name(key: str) -> Optional[str]:
        if len(key) == 5 and key.isalpha():
            port = pm.get_port_by_code(key.upper())
            if port:
                return port.get("name")
        return None

    fixes = []
    for carrier, entries in dynamic.items():
        for key, text in (entries or {}).items():
            fixes.append({
                "carrier": carrier,
                "key": key,
                "text": text,
                "port_name": port_name(key),
                "source": "user" if user_saved.get(carrier, {}).get(key) == text else "built_in",
            })
    # Fixes written into the code; a saved fix for the same port takes precedence.
    for carrier, entries in CARRIER_PORT_OVERRIDES.items():
        for code, text in entries.items():
            if code.lower() not in (dynamic.get(carrier) or {}):
                fixes.append({"carrier": carrier, "key": code.lower(), "text": text, "port_name": port_name(code.lower()), "source": "built_in"})
    fixes.sort(key=lambda f: (f["carrier"], f["source"] != "user", f["port_name"] or f["key"]))

    def current_fix(carrier: str, key: str) -> Optional[str]:
        return (dynamic.get(carrier) or {}).get(key) or CARRIER_PORT_OVERRIDES.get(carrier, {}).get(key.upper())

    since = datetime.utcnow() - timedelta(days=max(1, min(days, 90)))
    rows = (await session.execute(
        select(CarrierSearchResult).where(
            CarrierSearchResult.unfound_port_side.is_not(None),
            CarrierSearchResult.completed_at >= since,
        )
    )).scalars().all()

    misses: Dict[tuple, Dict[str, Any]] = {}
    for r in rows:
        carrier = _FIX_CARRIER_KEYS.get(r.carrier, r.carrier.lower())
        is_origin = r.unfound_port_side == "origin"
        locode = r.resolved_origin_locode if is_origin else r.resolved_destination_locode
        name = (r.resolved_origin_name if is_origin else r.resolved_destination_name) or (r.raw_origin_input if is_origin else r.raw_destination_input) or ""
        key = (locode or name).strip().lower()
        if not key:
            continue
        m = misses.setdefault((carrier, key), {
            "carrier": carrier,
            "key": key,
            "locode": locode,
            "port_name": name,
            "typed": r.unfound_port_query,
            "searches": 0,
            "last_seen": None,
        })
        m["searches"] += 1
        if r.completed_at and (m["last_seen"] is None or r.completed_at.isoformat() > m["last_seen"]):
            m["last_seen"] = r.completed_at.isoformat()
            m["typed"] = r.unfound_port_query
    miss_list = sorted(misses.values(), key=lambda m: m["last_seen"] or "", reverse=True)
    for m in miss_list:
        m["fix"] = current_fix(m["carrier"], m["key"])

    return {"fixes": fixes, "misses": miss_list, "days": days}


class CustomPortRequest(BaseModel):
    code: str
    name: Optional[str] = None
    country: Optional[str] = None
    aliases: Optional[List[str]] = []


@admin_router.get("/custom-ports")
async def get_admin_custom_ports(actor: User = Depends(verify_admin_access)):
    from services.port_manager import get_custom_ports
    return get_custom_ports()


@admin_router.post("/custom-ports")
async def create_custom_port_endpoint(
    request: CustomPortRequest,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    if not request.code or not request.name or not request.country:
        raise HTTPException(status_code=400, detail="code, name, and country are required")
    from services.port_manager import add_custom_port
    try:
        res = add_custom_port(request.code, request.name, request.country, request.aliases)
        await record_audit_event(
            session,
            actor_username=actor.username or "admin",
            action="create_custom_port",
            detail=f"Created custom port {request.code.upper()} ({request.name})",
        )
        return {"status": "SUCCESS", "port": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@admin_router.delete("/custom-ports/{code}")
async def delete_custom_port_endpoint(
    code: str,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    from services.port_manager import delete_custom_port
    delete_custom_port(code)
    await record_audit_event(
        session,
        actor_username=actor.username or "admin",
        action="delete_custom_port",
        detail=f"Deleted custom port {code.upper()}",
    )
    return {"status": "SUCCESS"}


class ExchangeRateUpdateRequest(BaseModel):
    currency: str
    rate_per_usd: float


@admin_router.get("/exchange-rates")
async def get_exchange_rates_endpoint(actor: User = Depends(verify_admin_access)):
    from services.currency_service import get_all_exchange_rates
    return get_all_exchange_rates()


@admin_router.post("/exchange-rates")
async def update_exchange_rate_endpoint(
    request: ExchangeRateUpdateRequest,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    if not request.currency or request.rate_per_usd <= 0:
        raise HTTPException(status_code=400, detail="Valid currency code and rate_per_usd > 0 are required")
    from services.currency_service import update_exchange_rate
    try:
        updated = update_exchange_rate(request.currency, request.rate_per_usd)
        await record_audit_event(
            session,
            actor_username=actor.username or "admin",
            action="update_exchange_rate",
            detail=f"Updated {request.currency.upper()} rate to {request.rate_per_usd}",
        )
        return {"status": "SUCCESS", "currency": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class StorageCleanupRequest(BaseModel):
    max_age_days: Optional[int] = 7


@admin_router.post("/cleanup-storage")
async def manual_storage_cleanup_endpoint(
    request: StorageCleanupRequest = StorageCleanupRequest(),
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    from services.storage_cleanup import cleanup_old_debug_files
    try:
        res = cleanup_old_debug_files(max_age_days=request.max_age_days or 7)
        await record_audit_event(
            session,
            actor_username=actor.username or "admin",
            action="cleanup_storage",
            detail=f"Cleaned up debug screenshots older than {request.max_age_days or 7} days",
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.post("/reset-profile/{carrier}")
async def reset_carrier_profile_endpoint(
    carrier: str,
    actor: User = Depends(verify_admin_access),
    session: AsyncSession = Depends(get_session),
):
    """Purge master and temp browser profiles for a carrier across persistent volume and local paths."""
    from services.browser_cleanup import purge_carrier_profile
    try:
        purged = purge_carrier_profile(carrier)
        await record_audit_event(
            session,
            actor_username=actor.username or "admin",
            action="reset_carrier_profile",
            detail=f"Purged {len(purged)} browser profile(s) for carrier '{carrier}'",
        )
        return {
            "status": "SUCCESS",
            "carrier": carrier,
            "purged_directories": purged,
            "message": f"Successfully purged {len(purged)} profile directory(ies) for {carrier}."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
