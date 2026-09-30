from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

def format_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        phone=user.phone or "",
        location=user.location or "",
        headline=user.headline or "",
        avatar=user.avatar or "DS",
        linkedin=user.linkedin or "",
        github=user.github or "",
        portfolio=user.portfolio or "",
        college=user.college or "",
        degree=user.degree or "",
        graduationYear=user.graduation_year or ""
    )

@router.post("/register", response_model=TokenResponse)
async def register(req: UserRegister, db: AsyncSession = Depends(get_db)):
    """Registers a new user account."""
    existing = await db.execute(select(User).where(User.email == req.email.lower()))
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Derive initials avatar
    avatar = "".join([part[0].upper() for part in req.name.split() if part])[:2] or "US"

    new_user = User(
        email=req.email.lower(),
        hashed_password=hash_password(req.password),
        name=req.name,
        phone=req.phone or "",
        location=req.location or "",
        headline=req.headline or "",
        avatar=avatar,
        college=req.college or "",
        degree=req.degree or "",
        graduation_year=req.graduationYear or ""
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token({"sub": new_user.id, "email": new_user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=format_user_response(new_user)
    )

@router.post("/login", response_model=TokenResponse)
async def login(req: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticates a user with email and password."""
    result = await db.execute(select(User).where(User.email == req.email.lower()))
    user = result.scalars().first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user.id, "email": user.email})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=format_user_response(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Fetches authenticated user profile."""
    return format_user_response(current_user)
