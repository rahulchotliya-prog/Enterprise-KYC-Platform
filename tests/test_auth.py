import pytest

@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/documents/metrics/system")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'Healthy'

# @pytest.mark.skip(reason="Temporarily skipping auth test")
@pytest.mark.asyncio
async def test_login(client):
    response = await client.post("/auth/login", json={"email": "rahul@gmail.com", "password": "R@hul123"})
    assert response.status_code == 400
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'