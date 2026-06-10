from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel

from models.database import get_session
from models.user import User

router = APIRouter(prefix="/api/users", tags=["users"])

class UserSchema(BaseModel):
    id: str
    name: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True

class UserCreateRequest(BaseModel):
    name: str

class AdminLoginRequest(BaseModel):
    password: str

@router.get("", response_model=List[UserSchema])
async def list_users(session: AsyncSession = Depends(get_session)):
    query = select(User).order_by(User.name)
    result = await session.execute(query)
    users = result.scalars().all()
    
    return [
        UserSchema(
            id=str(u.id),
            name=u.name,
            is_active=u.is_active,
            created_at=u.created_at.isoformat() if u.created_at else ""
        ) for u in users
    ]

@router.post("/login", response_model=UserSchema)
async def login_user(request: UserCreateRequest, session: AsyncSession = Depends(get_session)):
    """Find a user by name, or create one if it doesn't exist."""
    name = request.name.strip()
    if not name:
        raise HTTPException(400, "Name cannot be empty")
        
    query = select(User).where(User.name == name)
    user = (await session.execute(query)).scalar_one_or_none()
    
    if not user:
        user = User(name=name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
    if not user.is_active:
        raise HTTPException(403, "This user account has been deactivated.")
        
    return UserSchema(
        id=str(user.id),
        name=user.name,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else ""
    )

@router.delete("/{user_id}")
async def delete_user(user_id: str, session: AsyncSession = Depends(get_session)):
    query = select(User).where(User.id == user_id)
    user = (await session.execute(query)).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
        
    await session.delete(user)
    await session.commit()
    return {"status": "SUCCESS"}

# Admin route
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

@admin_router.post("/verify")
async def verify_admin(request: AdminLoginRequest):
    if request.password == "brian_infreight":
        return {"status": "SUCCESS"}
    raise HTTPException(401, "Invalid password")
