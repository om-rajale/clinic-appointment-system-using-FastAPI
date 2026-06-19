from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.database import supabase
from app.schemas import MedicalRecordCreate, MedicalRecordOut
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/records", tags=["Medical Records"])


@router.post("/", status_code=201, response_model=MedicalRecordOut)
def create_record(
    payload: MedicalRecordCreate,
    current_user: dict = Depends(require_role("doctor")),
):
    """Doctor creates a medical record for a patient."""
    # Verify doctor profile exists
    doc = supabase.table("doctors").select("id").eq("user_id", current_user["id"]).single().execute()
    if not doc.data:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    # Verify patient exists
    patient = supabase.table("users").select("id").eq("id", payload.patient_id).eq("role", "patient").execute()
    if not patient.data:
        raise HTTPException(status_code=404, detail="Patient not found")

    data = payload.model_dump()
    data["doctor_id"] = doc.data["id"]
    result = supabase.table("medical_records").insert(data).execute()
    return result.data[0]


@router.get("/", response_model=List[MedicalRecordOut])
def list_records(current_user: dict = Depends(get_current_user)):
    """Return medical records for the current user's role."""
    role = current_user["role"]

    if role == "admin":
        result = (
            supabase.table("medical_records")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    if role == "doctor":
        doc = supabase.table("doctors").select("id").eq("user_id", current_user["id"]).single().execute()
        if not doc.data:
            return []
        result = (
            supabase.table("medical_records")
            .select("*")
            .eq("doctor_id", doc.data["id"])
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    result = (
        supabase.table("medical_records")
        .select("*")
        .eq("patient_id", current_user["id"])
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


@router.get("/my", response_model=List[MedicalRecordOut])
def my_records(current_user: dict = Depends(require_role("patient"))):
    """Patient retrieves all their own medical records."""
    result = (
        supabase.table("medical_records")
        .select("*")
        .eq("patient_id", current_user["id"])
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


@router.get("/patient/{patient_id}", response_model=List[MedicalRecordOut])
def patient_records(
    patient_id: str,
    current_user: dict = Depends(require_role("doctor", "admin")),
):
    """Doctor or admin retrieves records for a specific patient."""
    result = (
        supabase.table("medical_records")
        .select("*")
        .eq("patient_id", patient_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


@router.get("/{record_id}", response_model=MedicalRecordOut)
def get_record(record_id: str, current_user: dict = Depends(get_current_user)):
    """Get a single record. Patients can only view their own."""
    result = supabase.table("medical_records").select("*").eq("id", record_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Record not found")

    record = result.data
    if current_user["role"] == "patient" and record["patient_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return record


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: str, current_user: dict = Depends(require_role("admin"))):
    """Admin deletes a medical record."""
    supabase.table("medical_records").delete().eq("id", record_id).execute()
