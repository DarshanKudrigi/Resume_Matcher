from typing import List, Optional
from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = ""
    location: Optional[str] = ""
    headline: Optional[str] = ""
    college: Optional[str] = ""
    degree: Optional[str] = ""
    graduationYear: Optional[str] = ""

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    headline: Optional[str] = None
    avatar: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    graduationYear: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str] = ""
    location: Optional[str] = ""
    headline: Optional[str] = ""
    avatar: Optional[str] = "DS"
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""
    college: Optional[str] = ""
    degree: Optional[str] = ""
    graduationYear: Optional[str] = ""

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
