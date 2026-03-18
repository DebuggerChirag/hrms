from sqlalchemy import Column, Integer, String, Float, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .database import Base

class RefundStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    dob = Column(String) # For simplicity, storing as string YYYY-MM-DD
    policy_number = Column(String, unique=True, index=True)

    refunds = relationship("RefundRequest", back_populates="patient")

class RefundRequest(Base):
    __tablename__ = "refund_requests"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    reason = Column(Text)
    # Using string for simplicity, can also just be a stored file path or document reference
    document_path = Column(String, nullable=True) 
    amount_requested = Column(Float)
    status = Column(Enum(RefundStatus), default=RefundStatus.PENDING)
    ai_decision_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="refunds")
