from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.database import supabase
from app.schemas import AppointmentCreate, AppointmentUpdate, AppointmentOut
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def _check_doctor_available(doctor_id: str, scheduled_at: str, exclude_id: str = None):
    """Raise 409 if the time slot is already taken."""
    query = (
        supabase.table("appointments")
        .select("id")
        .eq("doctor_id", doctor_id)
        .eq("scheduled_at", scheduled_at)
        .in_("status", ["pending", "confirmed"])
    )
    result = query.execute()
    for row in (result.data or []):
        if row["id"] != exclude_id:
            raise HTTPException(status_code=409, detail="This time slot is already booked")


# ── Patient: Book appointment ─────────────────────────────────────────────────

@router.post("/", status_code=201, response_model=AppointmentOut)
def book_appointment(
    payload: AppointmentCreate,
    current_user: dict = Depends(require_role("patient")),
):
    """Patient books a new appointment."""
    # Verify doctor exists
    doc = supabase.table("doctors").select("id, slot_duration").eq("id", payload.doctor_id).single().execute()
    if not doc.data:
        raise HTTPException(status_code=404, detail="Doctor not found")

    scheduled_str = payload.scheduled_at.isoformat()
    _check_doctor_available(payload.doctor_id, scheduled_str)

    data = {
        "patient_id": current_user["id"],
        "doctor_id": payload.doctor_id,
        "scheduled_at": scheduled_str,
        "duration_mins": doc.data["slot_duration"],
        "reason": payload.reason,
        "status": "pending",
    }
    result = supabase.table("appointments").insert(data).execute()
    return result.data[0]


# ── Patient: My appointments ──────────────────────────────────────────────────

@router.get("/my", response_model=List[AppointmentOut])
def my_appointments(current_user: dict = Depends(require_role("patient"))):
    """Patient sees all their appointments."""
    result = (
        supabase.table("appointments")
        .select("*")
        .eq("patient_id", current_user["id"])
        .order("scheduled_at", desc=True)
        .execute()
    )
    return result.data or []


# ── Doctor: Their schedule ────────────────────────────────────────────────────

@router.get("/schedule", response_model=List[AppointmentOut])
def doctor_schedule(
    status: str = None,
    current_user: dict = Depends(require_role("doctor")),
):
    """Doctor sees their appointment schedule, optionally filtered by status."""
    doc = supabase.table("doctors").select("id").eq("user_id", current_user["id"]).single().execute()
    if not doc.data:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    query = (
        supabase.table("appointments")
        .select("*")
        .eq("doctor_id", doc.data["id"])
        .order("scheduled_at")
    )
    if status:
        query = query.eq("status", status)

    return query.execute().data or []


# ── List appointments (role-aware) ────────────────────────────────────────────

@router.get("/", response_model=List[AppointmentOut])
def list_appointments(current_user: dict = Depends(get_current_user)):
    """Return appointments for the current user's role."""
    role = current_user["role"]

    if role == "admin":
        result = (
            supabase.table("appointments")
            .select("*")
            .order("scheduled_at", desc=True)
            .execute()
        )
        return result.data or []

    if role == "doctor":
        doc = supabase.table("doctors").select("id").eq("user_id", current_user["id"]).single().execute()
        if not doc.data:
            return []
        result = (
            supabase.table("appointments")
            .select("*")
            .eq("doctor_id", doc.data["id"])
            .order("scheduled_at", desc=True)
            .execute()
        )
        return result.data or []

    result = (
        supabase.table("appointments")
        .select("*")
        .eq("patient_id", current_user["id"])
        .order("scheduled_at", desc=True)
        .execute()
    )
    return result.data or []


# ── Get single appointment ────────────────────────────────────────────────────

@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: str, current_user: dict = Depends(get_current_user)):
    """Fetch one appointment. Patients can only see their own."""
    result = supabase.table("appointments").select("*").eq("id", appointment_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt = result.data
    if current_user["role"] == "patient" and appt["patient_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return appt


# ── Update appointment (doctor confirms / patient cancels) ────────────────────

@router.patch("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(
    appointment_id: str,
    payload: AppointmentUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    - Doctor can confirm, complete, or add notes.
    - Patient can cancel their own appointment.
    - Admin can do anything.
    """
    appt_result = supabase.table("appointments").select("*").eq("id", appointment_id).single().execute()
    if not appt_result.data:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt = appt_result.data
    role = current_user["role"]

    # Enforce permissions
    if role == "patient":
        if appt["patient_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not your appointment")
        if payload.status and payload.status not in ("cancelled",):
            raise HTTPException(status_code=403, detail="Patients can only cancel appointments")

    if role == "doctor":
        # Verify it's actually their appointment
        doc = supabase.table("doctors").select("id").eq("user_id", current_user["id"]).single().execute()
        if not doc.data or appt["doctor_id"] != doc.data["id"]:
            raise HTTPException(status_code=403, detail="Not your appointment")

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Nothing to update")

    updated = supabase.table("appointments").update(updates).eq("id", appointment_id).execute()
    return updated.data[0]


# ── Patient: Cancel ───────────────────────────────────────────────────────────

@router.delete("/{appointment_id}", status_code=200)
def cancel_appointment(
    appointment_id: str,
    current_user: dict = Depends(require_role("patient")),
):
    """Patient cancels their appointment (shortcut endpoint)."""
    appt = supabase.table("appointments").select("*").eq("id", appointment_id).single().execute()
    if not appt.data:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appt.data["patient_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not your appointment")
    if appt.data["status"] in ("completed", "cancelled"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel a {appt.data['status']} appointment")

    supabase.table("appointments").update({"status": "cancelled"}).eq("id", appointment_id).execute()
    return {"message": "Appointment cancelled"}
