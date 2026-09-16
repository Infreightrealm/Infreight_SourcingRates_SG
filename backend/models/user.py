import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Uuid, ForeignKey, Text
from .database import Base

class User(Base):
    """Represents a registered user of the system."""
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=True, index=True)
    display_name = Column(String(100), nullable=True)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(20), default="user", nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(50), nullable=True)
    last_login_at = Column(DateTime, nullable=True)


class AuthSession(Base):
    """Stores hashed active session tokens."""
    __tablename__ = "auth_sessions"

    token_hash = Column(String(64), primary_key=True)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)


class AuditLog(Base):
    """Stores security and operational audit trail entries."""
    __tablename__ = "audit_logs"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    actor_username = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    detail = Column(Text, nullable=True)
