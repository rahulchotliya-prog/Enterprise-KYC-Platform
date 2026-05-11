from unittest.mock import AsyncMock, patch
import pytest
import json
from src.documents.service import DocumentService


@pytest.mark.asyncio
async def test_cached_analytics_reads_from_repository_when_cache_is_empty():
    mock_repo = AsyncMock()
    mock_repo.get_analytics.return_value = {
        "total_documents": 10,
        "verified_documents": 5,
        "rejected_documents": 2,
    }

    service = DocumentService(mock_repo)

    with patch(
        "src.infrastructure.redis.redis_client.get",
        new_callable=AsyncMock,
    ) as mock_redis_get:
        with patch(
            "src.infrastructure.redis.redis_client.set",
            new_callable=AsyncMock,
        ) as mock_redis_set:
            mock_redis_get.return_value = None

            analytics = await service.get_cached_analytics()

            assert analytics["total_documents"] == 10
            assert analytics["verified_documents"] == 5
            assert analytics["rejected_documents"] == 2
            mock_repo.get_analytics.assert_called_once()
            mock_redis_set.assert_called_once()


@pytest.mark.asyncio
async def test_cached_analytics_uses_cached_value_if_available():
    mock_repo = AsyncMock()
    service = DocumentService(mock_repo)

    cached_value = {
        "total_documents": 12,
        "verified_documents": 4,
        "rejected_documents": 1,
    }

    with patch(
        "src.infrastructure.redis.redis_client.get",
        new_callable=AsyncMock,
    ) as mock_redis_get:
        with patch(
            "src.infrastructure.redis.redis_client.set",
            new_callable=AsyncMock,
        ) as mock_redis_set:
            mock_redis_get.return_value = json.dumps(cached_value)

            analytics = await service.get_cached_analytics()

            assert analytics == cached_value
            mock_repo.get_analytics.assert_not_called()
            mock_redis_set.assert_not_called()
