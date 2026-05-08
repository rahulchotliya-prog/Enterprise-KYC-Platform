from unittest.mock import AsyncMock, patch
import pytest
from src.documents.service import DocumentService


# @pytest.mark.asyncio
# async def test_cached_analytics():

#     mock_repo = AsyncMock()

#     mock_repo.get_analytics.return_value = {"total_documents": 10}
#     print("Mocked get_analytics return value:", mock_repo.get_analytics.return_value)
#     service = DocumentService(mock_repo)

#     analytics = await service.get_cached_analytics()
#     assert analytics == {"total_documents": 10}
#     # mock_repo.get_analytics.assert_called_once()
    

@pytest.mark.asyncio
async def test_cached_analytics():

    mock_repo = AsyncMock()

    mock_repo.get_analytics.return_value = {
        "total_documents": 10
    }

    service = DocumentService(mock_repo)

    with patch(
        "src.infrastructure.redis.redis_client.get",
        new_callable=AsyncMock
    ) as mock_redis_get:

        with patch(
            "src.infrastructure.redis.redis_client.set",
            new_callable=AsyncMock
        ) as mock_redis_set:

            mock_redis_get.return_value = None

            analytics = await service.get_cached_analytics()

            assert analytics == {"total_documents": 10}

            mock_repo.get_analytics.assert_called_once()

            mock_redis_set.assert_called_once()