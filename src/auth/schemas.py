from uuid import UUID
from pydantic import BaseModel,EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool

    # class Config:
    #     orm_mode = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"