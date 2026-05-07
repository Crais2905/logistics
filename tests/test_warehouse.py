import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_warehouse_unauthorized(client: AsyncClient):
    response = await client.post(
        "/warehouse/",
        json={"name": "Test Warehouse", "location": "Lviv"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_get_warehouse(admin_client: AsyncClient):
    response = await admin_client.post(
        "/warehouse/",
        json={"name": "Test Warehouse", "location": "Lviv"},
    )
    assert response.status_code == 201
    warehouse_id = response.json()["id"]

    response = await admin_client.get(f"/warehouse/{warehouse_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Warehouse"
    assert response.json()["location"] == "Lviv"


@pytest.mark.asyncio
async def test_warehouses_isolated(authorized_client: AsyncClient):
    response = await authorized_client.get("/warehouse/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_warehouse_get_list(admin_client: AsyncClient):
    response = await admin_client.post(
        "/warehouse/",
        json={"name": "Test Warehouse1", "location": "Lviv"},
    )
    assert response.status_code == 201

    response = await admin_client.post(
        "/warehouse/",
        json={"name": "Test Warehouse2", "location": "Kyiv"},
    )
    assert response.status_code == 201

    response = await admin_client.get(f"/warehouse/")
    assert response.status_code == 200
    # assert type(response.json()) == type([])
    assert isinstance(response.json(), list)

    assert response.json()[0]["name"] == "Test Warehouse1"
    assert response.json()[0]["location"] == "Lviv"

    assert response.json()[1]["name"] == "Test Warehouse2"
    assert response.json()[1]["location"] == "Kyiv"
