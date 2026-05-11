"""
SQLAlchemy models for rate searches and carrier search results.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text, Uuid
from sqlalchemy.orm import relationship
from .database import Base


class RateSearch(Base):
    """Represents a rate search request from an employee."""
    __tablename__ = "rate_searches"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    origin = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    service_term = Column(String(50), nullable=False, default="CY/CY")
    container_type = Column(String(50), nullable=False)
    container_quantity = Column(Integer, nullable=False, default=1)
    weight_per_container_kg = Column(Float, nullable=False, default=20000)
    commodity = Column(String(255), nullable=False)
    departure_date = Column(String(50), nullable=False)  # "tomorrow" or ISO date
    search_window_days = Column(Integer, nullable=False, default=14)
    selected_carriers = Column(JSON, nullable=False)  # List of carrier codes
    status = Column(String(50), nullable=False, default="QUEUED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    carrier_results = relationship("CarrierSearchResult", back_populates="rate_search", cascade="all, delete-orphan")


class CarrierSearchResult(Base):
    """Tracks the result of searching a specific carrier for a rate search."""
    __tablename__ = "carrier_search_results"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    search_id = Column(Uuid, ForeignKey("rate_searches.id"), nullable=False)
    carrier = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="QUEUED")
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    rate_search = relationship("RateSearch", back_populates="carrier_results")
    quotes = relationship("Quote", back_populates="carrier_result", cascade="all, delete-orphan")
