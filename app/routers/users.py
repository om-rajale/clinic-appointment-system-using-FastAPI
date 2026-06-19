from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.database import supabase
from app.schemas import UserOut
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Get the logged-in user's profile."""
    return current_user


@router.get("/", response_model=List[UserOut])
def list_users(current_user: dict = Depends(require_role("admin"))):
    """List all users — admin only."""
    result = supabase.table("users").select("*").order("created_at", desc=True).execute()
    return result.data or []


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, current_user: dict = Depends(require_role("admin"))):
    """Get a specific user by ID — admin only."""
    result = supabase.table("users").select("*").eq("id", user_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return result.data


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str, current_user: dict = Depends(require_role("admin"))):
    """Delete a user — admin only."""
    supabase.table("users").delete().eq("id", user_id).execute()
