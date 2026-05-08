from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    status: str
    created_at: datetime
