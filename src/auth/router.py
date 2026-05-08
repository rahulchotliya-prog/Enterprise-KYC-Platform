from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.repository import UserRepository
from src.auth.schemas import UserCreate, UserResponse, LoginRequest, LoginResponse
from src.auth.service import AuthService
from src.database.session import get_db
from src.auth.dependencies import get_current_user, require_admin
from src.auth.models import User


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    repository = UserRepository(db)
    service = AuthService(repository)
    try:
        return await service.register_user(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    repository = UserRepository(db)
    service = AuthService(repository)
    try:
        return await service.login(payload.email, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def me(user: User = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
    }


@router.get("/admin", status_code=status.HTTP_200_OK)
async def admin_dahhboard(user: User = Depends(require_admin)):
    return {"message": "Welcome Admin", "email": user.email}
