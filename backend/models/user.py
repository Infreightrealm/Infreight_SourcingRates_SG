import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Uuid
from .database import Base

class User(Base):
    """Represents a registered user of the system."""
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
