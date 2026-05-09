from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base
from src.auth.models import User

from sqlalchemy import JSON


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="UPLOADED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    extracted_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    processing_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String, nullable=True)

    user = relationship(User)
