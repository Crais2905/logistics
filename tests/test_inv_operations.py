from uuid import UUID

import pytest
import pytest_asyncio
from httpx import AsyncClient

from tests.test_warehouse import warehouse_factory
from tests.test_product import product_factory


async def increase_product_quantity(
        client: AsyncClient,
        product_id: UUID,
        warehouse_id: UUID,
        quantity: float = 100
):
    response = await client.post(
        "/operations/",
        json={
            "type": "inbound",
            "product_id": product_id,
            "quantity": quantity,
            "to_warehouse_id": warehouse_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_inbound_operation(admin_client: AsyncClient, warehouse_factory, product_factory):
    """Admin successfully creates an inbound operation."""
    warehouse_id = await warehouse_factory()
    product_id = await product_factory()

    response = await admin_client.post(
        "/operations/",
        json={
          "type": "inbound",
          "product_id": product_id,
          "quantity": 5,
          "to_warehouse_id": warehouse_id,
          "comment": "Test Comment"
        },
    )
    assert response.status_code == 200

    response = await admin_client.get("/stock/?offset=0&limit=10&zero_quantity=false&active_warehouse=true")
    assert response.status_code == 200
    assert response.json()[0]["quantity"] == 5


@pytest.mark.asyncio
async def test_create_outbound_operation(admin_client: AsyncClient, warehouse_factory, product_factory):
    """Admin successfully creates an outbound operation."""
    warehouse_id = await warehouse_factory()
    product_id = await product_factory()

    await increase_product_quantity(admin_client, product_id, warehouse_id)

    response = await admin_client.post(
        "/operations/",
        json={
            "type": "outbound",
            "product_id": product_id,
            "quantity": 45,
            "from_warehouse_id": warehouse_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 200

    response = await admin_client.get("/stock/?offset=0&limit=10&zero_quantity=false&active_warehouse=true")
    assert response.status_code == 200
    assert response.json()[0]["quantity"] == 55


@pytest.mark.asyncio
async def test_create_transfer_operation(admin_client: AsyncClient, warehouse_factory, product_factory):
    """Admin successfully creates a transfer operation."""

    warehouse1_id = await warehouse_factory(name="Wh1")
    warehouse2_id = await warehouse_factory(name="Wh2")
    product_id = await product_factory()

    await increase_product_quantity(admin_client, product_id, warehouse1_id)

    response = await admin_client.post(
        "/operations/",
        json={
            "type": "transfer",
            "product_id": product_id,
            "quantity": 75,
            "from_warehouse_id": warehouse1_id,
            "to_warehouse_id": warehouse2_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_adjust_operation(admin_client: AsyncClient, warehouse_factory, product_factory):
    """Admin successfully creates an adjust operation."""
    warehouse_id = await warehouse_factory()
    product_id = await product_factory()

    await increase_product_quantity(admin_client, product_id, warehouse_id)

    response = await admin_client.post(
        "/operations/",
        json={
            "type": "adjust",
            "product_id": product_id,
            "quantity": 45,
            "from_warehouse_id": warehouse_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 200

    response = await admin_client.get("/stock/?offset=0&limit=10&zero_quantity=false&active_warehouse=true")
    assert response.status_code == 200
    assert response.json()[0]["quantity"] == 45


@pytest.mark.asyncio
async def test_create_operation_unauthorized(client: AsyncClient):
    """Unauthorized user cannot create an operation."""
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await client.post(
        "/operations/",
        json={
            "type": "inbound",
            "product_id": fake_id,
            "quantity": 5,
            "to_warehouse_id": fake_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_operation_forbidden_for_regular_user(authorized_client: AsyncClient):
    """Regular user cannot create an operation."""
    fake_id = "00000000-0000-0000-0000-000000000000"

    response = await authorized_client.post(
        "/operations/",
        json={
            "type": "inbound",
            "product_id": fake_id,
            "quantity": 5,
            "to_warehouse_id": fake_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_inbound_operation_wrong_warehouse_field(admin_client: AsyncClient, warehouse_factory, product_factory):
    """Inbound operation fails when from_warehouse_id is passed instead of to_warehouse_id."""
    warehouse_id = await warehouse_factory()
    product_id = await product_factory()

    response = await admin_client.post(
        "/operations/",
        json={
            "type": "inbound",
            "product_id": product_id,
            "quantity": 5,
            "from_warehouse_id": warehouse_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_outbound_operation_wrong_warehouse_field(admin_client: AsyncClient, warehouse_factory, product_factory):
    """Outbound operation fails when to_warehouse_id is passed instead of from_warehouse_id."""
    warehouse_id = await warehouse_factory()
    product_id = await product_factory()

    response = await admin_client.post(
        "/operations/",
        json={
            "type": "outbound",
            "product_id": product_id,
            "quantity": 45,
            "to_warehouse_id": warehouse_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_outbound_operation_insufficient_stock(admin_client: AsyncClient, warehouse_factory, product_factory):
    """Outbound operation fails when quantity exceeds available stock."""
    warehouse_id = await warehouse_factory()
    product_id = await product_factory()

    await increase_product_quantity(admin_client, product_id, warehouse_id, quantity=10)

    response = await admin_client.post(
        "/operations/",
        json={
            "type": "outbound",
            "product_id": product_id,
            "quantity": 999,
            "from_warehouse_id": warehouse_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_transfer_operation_insufficient_stock(admin_client: AsyncClient, warehouse_factory, product_factory):
    """Transfer operation fails when quantity exceeds available stock in source warehouse."""
    warehouse1_id = await warehouse_factory(name="Wh1")
    warehouse2_id = await warehouse_factory(name="Wh2")
    product_id = await product_factory()

    await increase_product_quantity(admin_client, product_id, warehouse1_id, quantity=10)

    response = await admin_client.post(
        "/operations/",
        json={
            "type": "transfer",
            "product_id": product_id,
            "quantity": 999,
            "from_warehouse_id": warehouse1_id,
            "to_warehouse_id": warehouse2_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_operation_negative_quantity(admin_client: AsyncClient, warehouse_factory, product_factory):
    """Operation fails when quantity is negative."""
    warehouse_id = await warehouse_factory()
    product_id = await product_factory()

    response = await admin_client.post(
        "/operations/",
        json={
            "type": "inbound",
            "product_id": product_id,
            "quantity": -10,
            "to_warehouse_id": warehouse_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_operation_nonexistent_product(admin_client: AsyncClient, warehouse_factory):
    """Operation fails when product does not exist."""
    warehouse_id = await warehouse_factory()
    fake_product_id = "00000000-0000-0000-0000-000000000000"

    response = await admin_client.post(
        "/operations/",
        json={
            "type": "inbound",
            "product_id": fake_product_id,
            "quantity": 5,
            "to_warehouse_id": warehouse_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_operation_nonexistent_warehouse(admin_client: AsyncClient, product_factory):
    """Operation fails when warehouse does not exist."""
    product_id = await product_factory()
    fake_warehouse_id = "00000000-0000-0000-0000-000000000000"

    response = await admin_client.post(
        "/operations/",
        json={
            "type": "inbound",
            "product_id": product_id,
            "quantity": 5,
            "to_warehouse_id": fake_warehouse_id,
            "comment": "Test Comment"
        },
    )
    assert response.status_code == 404

