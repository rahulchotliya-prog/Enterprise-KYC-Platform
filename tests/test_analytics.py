import pytest
from uuid import uuid4
from src.documents.models import Document
from src.auth.models import User
from src.auth.utils import hash_password
from src.database.session import AsyncSessionLocal


@pytest.mark.asyncio
async def test_analytics_summary_endpoint_returns_counts(client):
    async with AsyncSessionLocal() as session:
        user = User(
            email=f"user-{uuid4().hex[:8]}@example.com",
            hashed_password=hash_password("StrongPass123!"),
            full_name="Analytics User",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        document = Document(
            user_id=user.id,
            filename="report.pdf",
            original_filename="report.pdf",
            file_size=1024,
            content_type="application/pdf",
            status="VERIFIED",
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)

    response = await client.get("/documents/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 1
    assert data["verified_documents"] == 1
    assert data["rejected_documents"] == 0


@pytest.mark.asyncio
async def test_performance_metrics_endpoint_returns_average_processing_time(client):
    async with AsyncSessionLocal() as session:
        user = User(
            email=f"user-{uuid4().hex[:8]}@example.com",
            hashed_password=hash_password("StrongPass123!"),
            full_name="Metrics User",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        document_one = Document(
            user_id=user.id,
            filename="one.pdf",
            original_filename="one.pdf",
            file_size=512,
            content_type="application/pdf",
            status="VERIFIED",
            processing_time=5,
        )
        document_two = Document(
            user_id=user.id,
            filename="two.pdf",
            original_filename="two.pdf",
            file_size=1024,
            content_type="application/pdf",
            status="VERIFIED",
            processing_time=7,
        )
        session.add_all([document_one, document_two])
        await session.commit()

    response = await client.get("/documents/analytics/performance")
    assert response.status_code == 200
    data = response.json()
    assert data["average_processing_time"] in (6.0, 6)


