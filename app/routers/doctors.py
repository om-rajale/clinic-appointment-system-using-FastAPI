from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timedelta

from app.database import supabase
from app.schemas import DoctorProfileCreate, DoctorProfileUpdate, DoctorOut
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/doctors", tags=["Doctors"])


def _enrich_doctor(doc: dict) -> dict:
    """Join doctor row with user info for the response."""
    user = supabase.table("users").select("full_name, email").eq("id", doc["user_id"]).single().execute()
    return {**doc, **(user.data or {})}


@router.post("/profile", status_code=201, response_model=DoctorOut)
def create_doctor_profile(
    payload: DoctorProfileCreate,
    current_user: dict = Depends(require_role("doctor")),
):
    """A doctor creates their own schedule/profile."""
    existing = supabase.table("doctors").select("id").eq("user_id", current_user["id"]).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Doctor profile already exists")

    data = payload.model_dump()
    data["user_id"] = current_user["id"]
    result = supabase.table("doctors").insert(data).execute()
    return _enrich_doctor(result.data[0])


@router.get("/", response_model=List[DoctorOut])
def list_doctors(_: dict = Depends(get_current_user)):
    """List all doctors (any authenticated user)."""
    result = supabase.table("doctors").select("*").execute()
    return [_enrich_doctor(d) for d in (result.data or [])]


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(doctor_id: str, _: dict = Depends(get_current_user)):
    """Get a single doctor's profile."""
    result = supabase.table("doctors").select("*").eq("id", doctor_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return _enrich_doctor(result.data)


@router.patch("/profile", response_model=DoctorOut)
def update_doctor_profile(
    payload: DoctorProfileUpdate,
    current_user: dict = Depends(require_role("doctor")),
):
    """Doctor updates their own profile."""
    result = supabase.table("doctors").select("*").eq("user_id", current_user["id"]).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Doctor profile not found — create it first")

    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    updated = supabase.table("doctors").update(updates).eq("user_id", current_user["id"]).execute()
    return _enrich_doctor(updated.data[0])


@router.get("/{doctor_id}/slots")
def get_available_slots(doctor_id: str, date: str, _: dict = Depends(get_current_user)):
    """
    Return free time slots for a doctor on a given date.
    Query param: date=YYYY-MM-DD
    """
    doc_result = supabase.table("doctors").select("*").eq("id", doctor_id).single().execute()
    if not doc_result.data:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doc = doc_result.data
    try:
        day = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD")

    day_name = day.strftime("%A")
    if day_name not in doc["available_days"]:
        return {"date": date, "available_slots": []}

    # Build all slots for the day
    start_h, start_m = map(int, doc["start_time"].split(":"))
    end_h,   end_m   = map(int, doc["end_time"].split(":"))
    slot_mins = doc["slot_duration"]

    current = day.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
    end_dt  = day.replace(hour=end_h,   minute=end_m,   second=0, microsecond=0)

    all_slots = []
    while current < end_dt:
        all_slots.append(current.isoformat())
        current += timedelta(minutes=slot_mins)

    # Remove already-booked slots
    booked = (
        supabase.table("appointments")
        .select("scheduled_at")
        .eq("doctor_id", doctor_id)
        .gte("scheduled_at", day.isoformat())
        .lt("scheduled_at", (day + timedelta(days=1)).isoformat())
        .in_("status", ["pending", "confirmed"])
        .execute()
    )
    booked_times = {r["scheduled_at"][:16] for r in (booked.data or [])}

    free_slots = [s for s in all_slots if s[:16] not in booked_times]
    return {"date": date, "doctor_id": doctor_id, "available_slots": free_slots}
