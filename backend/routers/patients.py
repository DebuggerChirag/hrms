from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random
import string

from .. import models, schemas
from ..database import get_db

router = APIRouter()

def generate_policy_number():
    return "POL-" + ''.join(random.choices(string.digits, k=6))

@router.post("/signup", response_model=schemas.Patient)
def signup_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.email == patient.email).first()
    if db_patient:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    policy_num = generate_policy_number()
    while db.query(models.Patient).filter(models.Patient.policy_number == policy_num).first():
        policy_num = generate_policy_number()
        
    new_patient = models.Patient(
        name=patient.name,
        email=patient.email,
        phone=patient.phone,
        dob=patient.dob,
        policy_number=policy_num
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

@router.post("/login", response_model=schemas.PatientWithRefunds)
def login_patient(credentials: schemas.PatientLogin, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(
        models.Patient.policy_number == credentials.policy_number,
        models.Patient.dob == credentials.dob
    ).first()
    
    if not patient:
        raise HTTPException(status_code=401, detail="Invalid policy number or date of birth")
        
    return patient
