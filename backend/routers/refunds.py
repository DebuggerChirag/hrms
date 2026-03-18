from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
import shutil

from .. import models, schemas
from ..database import get_db
from ..services.ai_service import evaluate_refund_request

router = APIRouter()
UPLOAD_DIR = "backend/uploads"

@router.post("/submit", response_model=schemas.RefundRequest)
async def submit_refund_request(
    patient_id: int = Form(...),
    reason: str = Form(...),
    amount_requested: float = Form(...),
    document: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Verify patient exists
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Save document
    file_path = None
    if document:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, document.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(document.file, buffer)

    # Note: AI evaluation could be heavy, in a real app this should be a background task (e.g. Celery)
    # For now, synchronous is fine for demo
    status, ai_decision_reason = ("Pending", None)
    
    if file_path:
        status, ai_decision_reason = evaluate_refund_request(file_path, reason, amount_requested)
        # Convert string to Enum
        try:
            enum_status = models.RefundStatus(status)
        except ValueError:
            enum_status = models.RefundStatus.PENDING

    else:
        enum_status = models.RefundStatus.PENDING
        ai_decision_reason = "No document provided."

    # Create refund request record
    refund_request = models.RefundRequest(
        patient_id=patient.id,
        reason=reason,
        amount_requested=amount_requested,
        document_path=file_path,
        status=enum_status,
        ai_decision_reason=ai_decision_reason
    )
    db.add(refund_request)
    db.commit()
    db.refresh(refund_request)

    return refund_request

@router.get("/{refund_id}", response_model=schemas.RefundRequest)
def get_refund_request(refund_id: int, db: Session = Depends(get_db)):
    refund = db.query(models.RefundRequest).filter(models.RefundRequest.id == refund_id).first()
    if not refund:
        raise HTTPException(status_code=404, detail="Refund request not found")
    return refund
