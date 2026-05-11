import pytest
from uuid import uuid4
from unittest.mock import patch


@pytest.mark.asyncio
@pytest.mark.real_auth
@patch("src.documents.service.process_document_task.delay")
async def test_upload_document_success(mock_process_document, client):
    mock_process_document.return_value = "mocked_document_id"
    email = f"user-{uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"

    await client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    login_response = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    token = login_response.json()["access_token"]

    files = {"file": ("test-document.pdf", b"PDF content bytes", "application/pdf")}
    response = await client.post(
        "/documents/upload",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UPLOADED"
    assert "id" in data
    mock_process_document.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.real_auth
async def test_upload_document_invalid_file_type(client):
    email = f"user-{uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"

    await client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    login_response = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    token = login_response.json()["access_token"]

    files = {"file": ("bad.exe", b"bad content", "application/octet-stream")}
    response = await client.post(
        "/documents/upload",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "Unsupported file type"


@pytest.mark.asyncio
@pytest.mark.real_auth
async def test_upload_document_exceeds_max_size(client):
    email = f"user-{uuid4().hex[:8]}@example.com"
    password = "StrongPass123!"

    await client.post(
        "/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    login_response = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    token = login_response.json()["access_token"]

    large_content = b"x" * (5 * 1024 * 1024 + 1)
    files = {"file": ("large.pdf", large_content, "application/pdf")}
    response = await client.post(
        "/documents/upload",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert "File size exceeds" in response.json()["error"]


@pytest.mark.asyncio
async def test_get_document_status_not_found(client):
    response = await client.get(f"/documents/{uuid4().hex}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"
