from uuid import UUID
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.repository import UserRepository
from src.auth.utils import decode_access_token
from src.database.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credential_exception
        user = await UserRepository(db).get_by_id(UUID(user_id))
        if user is None:
            raise credential_exception
        
    except jwt.PyJWTError:
        raise credential_exception
    repository = UserRepository(db)
    user = await repository.get_by_id(UUID(user_id))
    if not user:
        raise credential_exception
    return user

async def require_admin(user :User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not an admin")
    return user