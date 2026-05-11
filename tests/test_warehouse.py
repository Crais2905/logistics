import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def warehouse_factory(admin_client: AsyncClient):
    async def _create(name: str = "Test Warehouse", location: str = "Lviv"):
        response = await admin_client.post(
            "/warehouse/",
            json={"name": name, "location": location},
        )
        assert response.status_code == 201
        return response.json()["id"]
    return _create


@pytest.mark.asyncio
async def test_create_warehouse_unauthorized(client: AsyncClient):
    response = await client.post(
        "/warehouse/",
        json={"name": "Test Warehouse", "location": "Lviv"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_get_warehouse(admin_client: AsyncClient, warehouse_factory):
    warehouse_id = await warehouse_factory()

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
async def test_warehouse_get_list(admin_client: AsyncClient, warehouse_factory):
    await warehouse_factory("Test Warehouse1", "Lviv")
    await warehouse_factory("Test Warehouse2", "Kyiv")

    response = await admin_client.get(f"/warehouse/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Test Warehouse1"
    assert response.json()[0]["location"] == "Lviv"

    assert response.json()[1]["name"] == "Test Warehouse2"
    assert response.json()[1]["location"] == "Kyiv"


@pytest.mark.asyncio
async def test_warehouse_update_good(admin_client: AsyncClient, warehouse_factory):
    warehouse_id = await warehouse_factory()

    response = await admin_client.patch(
        f"/warehouse/{warehouse_id}",
        json={"location": "Kyiv"}
    )
    assert response.status_code == 200
    warehouse_id = response.json()["id"]

    response = await admin_client.get(f"/warehouse/{warehouse_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Warehouse"
    assert response.json()["location"] == "Kyiv"

@pytest.mark.asyncio
async def test_warehouse_update_bad(admin_client: AsyncClient):
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await admin_client.patch(
        f"/warehouse/{fake_id}",
        json={"location": "Kyiv"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_warehouse_inactivate(admin_client: AsyncClient, warehouse_factory):
    warehouse_id = await warehouse_factory()

    response = await admin_client.get(f"/warehouse/{warehouse_id}")
    assert response.json()["is_active"] == True

    response = await admin_client.patch(f"/warehouse/{warehouse_id}/deactivate")
    assert response.status_code == 200
    assert response.json()["is_active"] == False

