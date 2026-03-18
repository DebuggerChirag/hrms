from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import refunds, patients

app = FastAPI(title="Hospital Refund Management System API")

# Update CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all. In prod, lock this down.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router, prefix="/api/patients", tags=["patients"])
app.include_router(refunds.router, prefix="/api/refunds", tags=["refunds"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Hospital Refund Management System API"}
