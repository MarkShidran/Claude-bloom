import pytest


@pytest.mark.asyncio
async def test_list_companies_empty(client):
    response = await client.get("/api/v1/companies/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_create_company(client):
    payload = {
        "name": "Test Company",
        "ticker": "TEST",
        "sector": "Technology",
        "country": "RUS",
    }
    response = await client.post("/api/v1/companies/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Company"
    assert data["ticker"] == "TEST"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_get_company(client):
    # Create first
    payload = {"name": "Sberbank", "ticker": "SBER", "country": "RUS"}
    create_resp = await client.post("/api/v1/companies/", json=payload)
    company_id = create_resp.json()["id"]

    # Get
    response = await client.get(f"/api/v1/companies/{company_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Sberbank"


@pytest.mark.asyncio
async def test_search_companies(client):
    await client.post("/api/v1/companies/", json={"name": "Газпром", "ticker": "GAZP", "country": "RUS"})
    await client.post("/api/v1/companies/", json={"name": "Лукойл", "ticker": "LKOH", "country": "RUS"})

    response = await client.get("/api/v1/companies/search", params={"q": "Газ"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
