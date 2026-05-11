import pytest
import pytest_asyncio
from httpx import AsyncClient

@pytest_asyncio.fixture
async def product_factory(admin_client: AsyncClient):
    async def _create(name: str = "Test Product", sku: str = "tp-1", unit: str = "kg"):
        response = await admin_client.post(
            "/product/",
            json={"name": name, "sku": sku, "unit": unit},
        )
        assert response.status_code == 201
        return response.json()["id"]

    return _create


@pytest.mark.asyncio
async def test_create_product_unauthorized(client: AsyncClient):
    """Unauthorized user cannot create a product."""
    response = await client.post(
        "/product/",
        json={"name": "Test Product", "sku": "tp-1", "unit": "kg"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_product_forbidden_for_regular_user(authorized_client: AsyncClient):
    """A regular user (non-admin/manager) cannot create a product."""
    response = await authorized_client.post(
        "/product/",
        json={"name": "Test Product", "sku": "tp-1", "unit": "kg"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_product(admin_client: AsyncClient):
    """Admin successfully creates a product."""
    response = await admin_client.post(
        "/product/",
        json={"name": "Test Product", "sku": "tp-1", "unit": "kg"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["sku"] == "tp-1"
    assert data["unit"] == "kg"
    assert data["is_active"] == True


@pytest.mark.asyncio
async def test_get_products_unauthorized(client: AsyncClient):
    """Product list is available without authorization."""
    response = await client.get("/product/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_products_isolated(authorized_client: AsyncClient):
    """A newly created database contains no products."""
    response = await authorized_client.get("/product/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_products_list(admin_client: AsyncClient, product_factory):
    """The list returns all created products in the correct order."""
    await product_factory("Product A")
    await product_factory("Product B")

    response = await admin_client.get("/product/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "Product A"
    assert data[1]["name"] == "Product B"



@pytest.mark.asyncio
async def test_get_products_pagination(admin_client: AsyncClient, product_factory):
    """Offset and limit parameters correctly restrict the selection."""
    for i in range(5):
        await product_factory(name=f"Product {i}", sku=f"tg-{i}")

    response = await admin_client.get("/product/?offset=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Product 1"
    assert data[1]["name"] == "Product 2"


@pytest.mark.asyncio
async def test_get_product_by_id(admin_client: AsyncClient, product_factory):
    """Retrieving an existing product by ID."""
    product_id = await product_factory()

    response = await admin_client.get(f"/product/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["name"] == "Test Product"


@pytest.mark.asyncio
async def test_get_product_not_found(admin_client: AsyncClient):
    """Requesting a non-existent ID returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await admin_client.get(f"/product/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_product_unauthorized(client: AsyncClient):
    """Unauthorized user cannot update a product."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.patch(
        f"/product/{fake_id}",
        json={"unit": "l"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_product_forbidden_for_regular_user(
        authorized_client: AsyncClient, product_factory
):
    """A regular user cannot update a product."""
    product_id = await product_factory()

    response = await authorized_client.patch(
        f"/product/{product_id}",
        json={"unit": "l"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_product(admin_client: AsyncClient, product_factory):
    """Admin successfully updates a product field."""
    product_id = await product_factory()

    response = await admin_client.patch(
        f"/product/{product_id}",
        json={"unit": "l"},
    )
    assert response.status_code == 200

    response = await admin_client.get(f"/product/{product_id}")
    assert response.status_code == 200
    assert response.json()["unit"] == "l"
    assert response.json()["name"] == "Test Product"


@pytest.mark.asyncio
async def test_update_product_not_found(admin_client: AsyncClient):
    """Updating a non-existent product returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await admin_client.patch(
        f"/product/{fake_id}",
        json={"unit": "l"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deactivate_product_unauthorized(client: AsyncClient):
    """Unauthorized user cannot deactivate a product."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.patch(f"/product/{fake_id}/deactivate")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_deactivate_product_forbidden_for_regular_user(
        authorized_client: AsyncClient, product_factory
):
    """A regular user cannot deactivate a product."""
    product_id = await product_factory()

    response = await authorized_client.patch(f"/product/{product_id}/deactivate")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_deactivate_product(admin_client: AsyncClient, product_factory):
    """Admin successfully deactivates a product; is_active becomes False."""
    product_id = await product_factory()

    response = await admin_client.get(f"/product/{product_id}")
    assert response.json()["is_active"] is True

    response = await admin_client.patch(f"/product/{product_id}/deactivate")
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_deactivate_product_not_found(admin_client: AsyncClient):
    """Deactivating a non-existent product returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await admin_client.patch(f"/product/{fake_id}/deactivate")
    assert response.status_code == 404