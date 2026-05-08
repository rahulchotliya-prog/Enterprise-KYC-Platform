from src.auth.models import User
from src.auth.repository import UserRepository
from src.auth.schemas import UserCreate, UserResponse
from src.auth.utils import hash_password
from src.auth.utils import verify_password,create_access_token
from src.exceptions import AppException

class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register_user(self, user: UserCreate) -> UserResponse:
        existing_user = await self.repository.get_by_mail(user.email)
        if existing_user:
            # raise ValueError("User with this email already exists")
            raise AppException(status_code=400, message="User with this email already exists")
        user = User(
            email = user.email,
            hashed_password = hash_password(user.password),
            full_name = user.full_name
        )
        return await self.repository.create_user(user)
    
    async def login(self, email: str, password: str):
        user = await self.repository.get_by_mail(email)
        if not user:
            raise AppException(status_code=400, message="Invalid credentials")
        if not verify_password(password, user.hashed_password):
            raise AppException(status_code=400, message="Invalid credentials")

        return {"access_token": create_access_token(user.id), "token_type": "bearer"}