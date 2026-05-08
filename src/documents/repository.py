from sqlalchemy.ext.asyncio import AsyncSession
from src.documents.models import Document
from sqlalchemy import select, func


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(self, document: Document):
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def get_by_id(self, document_id):
        query = select(Document).where(Document.id == document_id)
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_analytics(self):
        total_query = select(func.count(Document.id))

        verified_query = select(func.count(Document.id)).where(
            Document.status == "VERIFIED"
        )
        rejected_query = select(func.count(Document.id)).where(
            Document.status == "REJECTED"
        )
        total = await self.db.execute(total_query)

        verified = await self.db.execute(verified_query)
        rejected = await self.db.execute(rejected_query)

        return {
            "total_documents": total.scalar(),
            "verified_documents": verified.scalar(),
            "rejected_documents": rejected.scalar(),
        }

    async def average_processing_time(self):
        query = select(func.avg(Document.processing_time))
        result = await self.db.execute(query)
        return result.scalar()
