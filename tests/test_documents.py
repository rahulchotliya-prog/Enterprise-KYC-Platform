import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_upload_document(client):
    files = {'file': ('C:\\Users\\TGSUser116\\Desktop\\enterprise-kyc-platform\\PYTHON PROGRAMMING NOTES.pdf', b'This is a test document.',"application/pdf")}
    response = await client.post("/documents/upload", files=files)
    print("Response:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data
    assert data["status"] == "UPLOADED"

@pytest.mark.asyncio
@patch("src.documents.service.process_document_task.delay")
async def test_upload_trigger_task(mock_process_document,client):
    mock_process_document.return_value = "mocked_document_id"
    files = {'file': ('C:\\Users\\TGSUser116\\Desktop\\enterprise-kyc-platform\\PYTHON PROGRAMMING NOTES.pdf', b'This is a test document.',"application/pdf")}
    response = await client.post("/documents/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data
    assert data["status"] == "UPLOADED"