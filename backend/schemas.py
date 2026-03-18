from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import RefundStatus

class PatientBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    dob: str

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    policy_number: str
    class Config:
        orm_mode = True

class PatientLogin(BaseModel):
    policy_number: str
    dob: str

class RefundRequestBase(BaseModel):
    reason: str
    amount_requested: float

class RefundRequestCreate(RefundRequestBase):
    patient_id: int

class RefundRequest(RefundRequestBase):
    id: int
    patient_id: int
    document_path: Optional[str] = None
    status: RefundStatus
    ai_decision_reason: Optional[str] = None
    created_at: datetime
    class Config:
        orm_mode = True

class PatientWithRefunds(Patient):
    refunds: List[RefundRequest] = []
