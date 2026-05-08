import os
from uuid import uuid4
from fastapi import UploadFile

from src.documents.models import Document
from src.documents.repository import DocumentRepository
from src.documents.utils import chunk_content, validate_file_size, validate_file_type
import json
from src.infrastructure.redis import redis_client
from src.infrastructure.tasks.document_task import process_document_task


class DocumentService:
    def __init__(self, repository:DocumentRepository):
        self.repository = repository
    
    async def uploade_document(self, file: UploadFile, user_id):

        upload_dir = "uploads/documents"

        os.makedirs(upload_dir, exist_ok=True)

        validate_file_type(file.content_type)

        content = await file.read()

        validate_file_size(len(content))

        chunks = list(chunk_content(content))
        print(f"Number of chunks: {len(chunks)}")

        extension = file.filename.split(".")[-1]

        unique_filename = f"{uuid4()}.{extension}"

        file_path = os.path.join(upload_dir, unique_filename)

        with open(file_path, "wb") as f:
            f.write(content)

        document = Document(
            user_id=user_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_size=len(content),
            content_type=file.content_type
        )

        saved_document = await self.repository.create_document(document)

        # CELERY TASK
        print("BEFORE CELERY")

        task = process_document_task.delay(str(saved_document.id))
        # await redis_client.delete("analytics_summary")
        print("AFTER CELERY")
        print(task)

        return saved_document

    async def get_cached_analytics(self):
        cache_key = "analytics_summary"

        cached_data = await redis_client.get(cache_key)
        # await redis_client.delete("analytics_summary")
        if cached_data:
            return json.loads(cached_data)
        analytics = await self.repository.get_analytics()
        await redis_client.set(cache_key, json.dumps(analytics))
        return analytics
    
    async def mark_document_failed(self, document_id:str, reason:str):
        document = await self.repository.get_by_id(document_id)
        if document:
            document.status = "FAILED"
            document.failure_reason = reason
            await self.repository.db.commit()