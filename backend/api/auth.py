from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status

from backend.core.models import UserRegister, UserLogin, UserProfile, TokenResponse
from backend.core.database import create_user, get_user_by_email
from backend.core.security import hash_password, verify_password, create_access_token
from backend.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register(req: UserRegister):
    """Registers a new user account and returns a JWT access token."""
    email = req.email.strip().lower()
    username = req.username.strip()

    if not email or "@" not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address."
        )

    if not username or len(username) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 2 characters long."
        )

    if not req.password or len(req.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )

    existing_user = get_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    hashed_pw = hash_password(req.password)
    user = create_user(email=email, username=username, hashed_password=hashed_pw)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account. Please try again."
        )

    token = create_access_token(user_id=user["id"], email=user["email"], username=user["username"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/login", response_model=TokenResponse)
def login(req: UserLogin):
    """Authenticates user credentials and returns a JWT access token."""
    email = req.email.strip().lower()
    user = get_user_by_email(email)

    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token(user_id=user["id"], email=user["email"], username=user["username"])
    user_profile = {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "created_at": str(user["created_at"])
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_profile
    }


@router.get("/me", response_model=UserProfile)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return current_user
