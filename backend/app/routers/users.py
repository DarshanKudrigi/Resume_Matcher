from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserProfileUpdate, UserResponse
from app.services.auth_service import get_current_user
from app.routers.auth import format_user_response

router = APIRouter(prefix="/users", tags=["Users & Profiles"])

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    req: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Updates user profile settings and social links."""
    if req.name is not None:
        current_user.name = req.name
    if req.email is not None and req.email.lower() != current_user.email:
        # Check uniqueness
        dup = await db.execute(select(User).where(User.email == req.email.lower()))
        if dup.scalars().first():
            raise HTTPException(status_code=400, detail="Email already taken")
        current_user.email = req.email.lower()
    if req.phone is not None:
        current_user.phone = req.phone
    if req.location is not None:
        current_user.location = req.location
    if req.headline is not None:
        current_user.headline = req.headline
    if req.avatar is not None:
        current_user.avatar = req.avatar
    if req.linkedin is not None:
        current_user.linkedin = req.linkedin
    if req.github is not None:
        current_user.github = req.github
    if req.portfolio is not None:
        current_user.portfolio = req.portfolio
    if req.college is not None:
        current_user.college = req.college
    if req.degree is not None:
        current_user.degree = req.degree
    if req.graduationYear is not None:
        current_user.graduation_year = req.graduationYear

    await db.commit()
    await db.refresh(current_user)
    return format_user_response(current_user)
