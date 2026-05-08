from src.auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_mail(self, email:str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id:UUID):
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, user:User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user