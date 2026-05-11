"""
SQLAlchemy models for quotes and individual charge line items.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text, JSON, Uuid
from sqlalchemy.orm import relationship
from .database import Base


class Quote(Base):
    """Represents a single freight quote from a carrier."""
    __tablename__ = "quotes"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    carrier_result_id = Column(Uuid, ForeignKey("carrier_search_results.id"), nullable=False)
    carrier = Column(String(50), nullable=False)
    etd = Column(String(20), nullable=True)  # ISO date string
    eta = Column(String(20), nullable=True)
    transit_time_days = Column(Integer, nullable=True)
    service_name = Column(String(255), nullable=True)
    vessel = Column(String(255), nullable=True)
    container_type = Column(String(50), nullable=True)
    container_quantity = Column(Integer, nullable=True)
    currency = Column(String(10), nullable=True, default="USD")
    basic_ocean_freight = Column(Float, nullable=True, default=0.0)
    discount = Column(Float, nullable=True, default=0.0)
    final_freight_value = Column(Float, nullable=True, default=0.0)
    raw_data_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    carrier_result = relationship("CarrierSearchResult", back_populates="quotes")
    charges = relationship("QuoteCharge", back_populates="quote", cascade="all, delete-orphan")


class QuoteCharge(Base):
    """Represents a single charge line item within a quote."""
    __tablename__ = "quote_charges"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    quote_id = Column(Uuid, ForeignKey("quotes.id"), nullable=False)
    charge_name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    currency = Column(String(10), nullable=True, default="USD")
    category = Column(String(50), nullable=False)
    included_in_final_value = Column(Boolean, nullable=False, default=False)
    reason = Column(Text, nullable=True)

    # Relationships
    quote = relationship("Quote", back_populates="charges")
