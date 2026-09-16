from uuid import UUID
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, func, desc, or_, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_session
from models.user import User, DirectMessage
from models.rate_search import RateSearch
import models.quote  # Ensure Quote mapper is registered
from api.auth_routes import get_current_user
from services.auth_service import record_audit_event, public_user_dict

router = APIRouter(prefix="/api/social", tags=["social"])


class SendMessageRequest(BaseModel):
    recipient_id: str
    content: str = Field("", max_length=2500)
    # Pasted screenshot / uploaded image as a data URL (mirrors avatar upload).
    attachment_url: Optional[str] = Field(None, max_length=6_000_000)  # ~4.5MB image, base64-inflated
    attachment_type: Optional[str] = Field(None, max_length=20)


class UpdateAvatarRequest(BaseModel):
    avatar_url: str = Field(..., max_length=500000)  # Support base64 data URLs up to ~500KB


class UpdateTitleRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)


@router.get("/colleagues")
async def list_colleagues(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """List all team members with their search stats and unread message counters."""
    # 1. Fetch all active users
    users_q = select(User).where(
        and_(User.status == "active", User.is_active == True)
    ).order_by(User.name.asc(), User.username.asc())
    users_res = await session.execute(users_q)
    active_users = users_res.scalars().all()

    # 2. Get unread message counts for current user grouped by sender
    unread_q = (
        select(DirectMessage.sender_id, func.count(DirectMessage.id))
        .where(
            and_(
                DirectMessage.recipient_id == current_user.id,
                DirectMessage.read_at.is_(None),
            )
        )
        .group_by(DirectMessage.sender_id)
    )
    unread_res = await session.execute(unread_q)
    unread_map = {row[0]: row[1] for row in unread_res.fetchall()}

    # 3. Aggregate search stats for each user
    colleagues = []
    for u in active_users:
        u_name = (u.username or u.name or "").lower()
        d_name = (u.display_name or u.name or "").lower()

        # Searches count
        search_filter = or_(
            func.lower(RateSearch.user_name) == u_name,
            func.lower(RateSearch.user_name) == d_name,
        )

        count_q = select(func.count(RateSearch.id)).where(search_filter)
        total_searches = (await session.execute(count_q)).scalar() or 0

        # Top origin/destination pairs
        top_lanes_q = (
            select(RateSearch.origin, RateSearch.destination, func.count(RateSearch.id).label("cnt"))
            .where(search_filter)
            .group_by(RateSearch.origin, RateSearch.destination)
            .order_by(desc("cnt"))
            .limit(2)
        )
        top_lanes_res = await session.execute(top_lanes_q)
        top_lanes = [
            {"origin": row[0], "destination": row[1], "count": row[2]}
            for row in top_lanes_res.fetchall()
        ]

        # Last search timestamp
        last_search_q = select(func.max(RateSearch.created_at)).where(search_filter)
        last_search_at = (await session.execute(last_search_q)).scalar()

        is_self = u.id == current_user.id

        colleagues.append({
            "id": str(u.id),
            "username": u.username,
            "display_name": u.display_name or u.name,
            "name": u.name or u.display_name,
            "role": u.role,
            "title_or_role_desc": u.title_or_role_desc or ("Administrator" if u.role == "admin" else "Rate Specialist"),
            "avatar_url": u.avatar_url,
            "is_self": is_self,
            "unread_count": unread_map.get(u.id, 0),
            "stats": {
                "total_searches": total_searches,
                "top_lanes": top_lanes,
                "last_searched_at": last_search_at.isoformat() if last_search_at else None,
            },
        })

    # Sort so current user is at front or middle, rest alphabetical
    return colleagues


@router.get("/messages/{colleague_id}")
async def get_conversation(
    colleague_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Retrieve private direct messages with a colleague and mark incoming unread messages as read."""
    try:
        colleague_uuid = UUID(colleague_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid colleague ID format.")

    # 1. Mark unread messages from this colleague as read
    now = datetime.utcnow()
    await session.execute(
        update(DirectMessage)
        .where(
            and_(
                DirectMessage.sender_id == colleague_uuid,
                DirectMessage.recipient_id == current_user.id,
                DirectMessage.read_at.is_(None),
            )
        )
        .values(read_at=now)
    )
    await session.commit()

    # 2. Fetch conversation history (last 250 messages)
    q = (
        select(DirectMessage)
        .where(
            or_(
                and_(
                    DirectMessage.sender_id == current_user.id,
                    DirectMessage.recipient_id == colleague_uuid,
                ),
                and_(
                    DirectMessage.sender_id == colleague_uuid,
                    DirectMessage.recipient_id == current_user.id,
                ),
            )
        )
        .order_by(DirectMessage.created_at.asc())
        .limit(250)
    )
    res = await session.execute(q)
    messages = res.scalars().all()

    return [
        {
            "id": str(m.id),
            "sender_id": str(m.sender_id),
            "recipient_id": str(m.recipient_id),
            "content": m.content,
            "attachment_url": m.attachment_url,
            "attachment_type": m.attachment_type,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "read_at": m.read_at.isoformat() if m.read_at else None,
            "is_from_me": m.sender_id == current_user.id,
        }
        for m in messages
    ]


@router.post("/messages")
async def send_direct_message(
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Send a private text message to a colleague. Self-messaging is prohibited."""
    try:
        recipient_uuid = UUID(payload.recipient_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid recipient ID format.")

    if recipient_uuid == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot send direct messages to yourself.")

    # Verify recipient exists and is active
    recipient_q = select(User).where(
        and_(User.id == recipient_uuid, User.status == "active", User.is_active == True)
    )
    recipient = (await session.execute(recipient_q)).scalars().first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Colleague account not found or is currently inactive.")

    clean_content = payload.content.strip()
    attachment_url = (payload.attachment_url or "").strip() or None
    attachment_type = (payload.attachment_type or "").strip() or None

    if not clean_content and not attachment_url:
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    if attachment_url and not attachment_url.startswith("data:image/"):
        raise HTTPException(status_code=400, detail="Attachment must be an image data URL.")

    msg = DirectMessage(
        sender_id=current_user.id,
        recipient_id=recipient_uuid,
        content=clean_content,
        attachment_url=attachment_url,
        attachment_type=attachment_type,
        created_at=datetime.utcnow(),
    )
    session.add(msg)
    await session.commit()
    await session.refresh(msg)

    return {
        "id": str(msg.id),
        "sender_id": str(msg.sender_id),
        "recipient_id": str(msg.recipient_id),
        "content": msg.content,
        "attachment_url": msg.attachment_url,
        "attachment_type": msg.attachment_type,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
        "read_at": None,
        "is_from_me": True,
    }


@router.post("/users/{user_id}/avatar")
async def update_user_avatar(
    user_id: str,
    payload: UpdateAvatarRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update profile picture. Admins can update any user's picture; users can update their own."""
    try:
        target_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    if current_user.role != "admin" and current_user.id != target_uuid:
        raise HTTPException(status_code=403, detail="Only administrators can update avatars for other colleagues.")

    target_user = (await session.execute(select(User).where(User.id == target_uuid))).scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    target_user.avatar_url = payload.avatar_url
    await session.commit()

    await record_audit_event(
        session,
        actor_username=current_user.username or "system",
        action="update_avatar",
        detail=f"Updated profile photo for @{target_user.username}",
    )

    return {
        "status": "SUCCESS",
        "user_id": str(target_user.id),
        "avatar_url": target_user.avatar_url,
    }


@router.post("/users/{user_id}/title")
async def update_user_title(
    user_id: str,
    payload: UpdateTitleRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update a colleague's professional title description."""
    try:
        target_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    if current_user.role != "admin" and current_user.id != target_uuid:
        raise HTTPException(status_code=403, detail="Only administrators can update titles for other colleagues.")

    target_user = (await session.execute(select(User).where(User.id == target_uuid))).scalars().first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    target_user.title_or_role_desc = payload.title.strip()
    await session.commit()

    return {
        "status": "SUCCESS",
        "user_id": str(target_user.id),
        "title": target_user.title_or_role_desc,
    }
