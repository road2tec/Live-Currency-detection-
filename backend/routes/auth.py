"""
Indian Currency Detection - Authentication Routes
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from bson import ObjectId

from models.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from utils.auth import hash_password, verify_password, create_access_token
from database.connection import get_database

router = APIRouter(prefix="/api", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user"""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    # Check if email exists
    existing_user = await db.users.find_one({"email": user_data.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user_doc = {
        "name": user_data.name.strip(),
        "email": user_data.email.lower().strip(),
        "password": hash_password(user_data.password),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    # Generate JWT
    token = create_access_token(data={"sub": user_id, "email": user_doc["email"]})

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            name=user_doc["name"],
            email=user_doc["email"],
            created_at=user_doc["created_at"],
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login and get JWT token"""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    # Find user
    user = await db.users.find_one({"email": credentials.email.lower()})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    user_id = str(user["_id"])

    # Generate JWT
    token = create_access_token(data={"sub": user_id, "email": user["email"]})

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            name=user["name"],
            email=user["email"],
            created_at=user.get("created_at", datetime.utcnow()),
        ),
    )
