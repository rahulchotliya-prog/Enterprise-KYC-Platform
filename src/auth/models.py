from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean,DateTime,String, Column, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm  import Mapped, mapped_column

from src.database.base import Base

class User(Base):
    __tablename__ = "users"

    id : Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4)
    email : Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password : Mapped[str] = mapped_column(String, nullable=False)
    full_name : Mapped[str] = mapped_column(String, nullable=False)
    is_active : Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin : Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified : Mapped[bool] = mapped_column(Boolean, default=False)
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now())