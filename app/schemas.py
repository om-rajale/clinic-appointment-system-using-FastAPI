from __future__ import annotations
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, time
import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


# ── AUTH ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None
    role: str = "patient"          # patient | doctor | admin

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not EMAIL_REGEX.match(v):
            raise ValueError("value is not a valid email address")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("patient", "doctor", "admin"):
            raise ValueError("role must be patient, doctor, or admin")
        return v

    @field_validator("password")
    @classmethod
    def min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not EMAIL_REGEX.match(v):
            raise ValueError("value is not a valid email address")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


# ── USER ──────────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    created_at: datetime


# ── DOCTOR ────────────────────────────────────────────────────────────────────

class DoctorProfileCreate(BaseModel):
    specialization: str
    bio: Optional[str] = None
    available_days: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    start_time: str = "09:00"      # "HH:MM"
    end_time: str = "17:00"
    slot_duration: int = 30        # minutes


class DoctorProfileUpdate(BaseModel):
    specialization: Optional[str] = None
    bio: Optional[str] = None
    available_days: Optional[List[str]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    slot_duration: Optional[int] = None


class DoctorOut(BaseModel):
    id: str
    user_id: str
    full_name: str
    email: str
    specialization: str
    bio: Optional[str]
    available_days: List[str]
    start_time: str
    end_time: str
    slot_duration: int


# ── APPOINTMENT ───────────────────────────────────────────────────────────────

class AppointmentCreate(BaseModel):
    doctor_id: str
    scheduled_at: datetime         # ISO 8601, e.g. "2025-07-01T10:00:00"
    reason: Optional[str] = None


class AppointmentUpdate(BaseModel):
    status: Optional[str] = None   # confirmed | cancelled | completed
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v and v not in ("pending", "confirmed", "cancelled", "completed"):
            raise ValueError("invalid status")
        return v


class AppointmentOut(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    scheduled_at: datetime
    duration_mins: int
    status: str
    reason: Optional[str]
    notes: Optional[str]
    reminder_sent: bool
    created_at: datetime


# ── MEDICAL RECORD ────────────────────────────────────────────────────────────

class MedicalRecordCreate(BaseModel):
    patient_id: str
    appointment_id: Optional[str] = None
    diagnosis: str
    prescription: Optional[str] = None
    notes: Optional[str] = None


class MedicalRecordOut(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    appointment_id: Optional[str]
    diagnosis: str
    prescription: Optional[str]
    notes: Optional[str]
    created_at: datetime
