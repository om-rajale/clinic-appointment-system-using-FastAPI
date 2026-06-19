from fastapi import APIRouter, HTTPException, status

from app.database import supabase
from app.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.utils.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201)
def register(payload: RegisterRequest):
    """Register a new patient, doctor, or admin."""
    # Check email uniqueness
    existing = supabase.table("users").select("id").eq("email", payload.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = {
        "email": payload.email,
        "password": hash_password(payload.password),
        "full_name": payload.full_name,
        "phone": payload.phone,
        "role": payload.role,
    }
    result = supabase.table("users").insert(user).execute()
    created = result.data[0]

    return {"message": "Registration successful", "user_id": created["id"], "role": created["role"]}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    """Authenticate and receive a JWT token."""
    result = supabase.table("users").select("*").eq("email", payload.email).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = result.data[0]
    if not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user["id"], "role": user["role"]})
    return TokenResponse(access_token=token, user_id=user["id"], role=user["role"])
