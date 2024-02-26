"""All moneybox endpoint tests are located here."""

import pytest
from httpx import AsyncClient

from src.custom_types import EndpointRouteType
from src.db.db_manager import DBManager


@pytest.mark.dependency(
    depends=["tests/test_db_manager.py::test_transfer_balance"], scope="session"
)
async def test_endpoint_get_moneyboxes(db_manager: DBManager, client: AsyncClient) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    expected_moneyboxes = {
        "total": 3,
        "moneyboxes": [
            {"name": "Test Box 1 - Updated", "id": 1, "balance": 33},
            {"name": "Test Box 3", "id": 3, "balance": 300},
            {"name": "Test Box 4", "id": 4, "balance": 0},
        ],
    }
    moneyboxes = response.json()
    assert response.status_code == 200
    assert moneyboxes == expected_moneyboxes

    # delete money all boxes
    await db_manager.delete_moneybox(moneybox_id=1)
    await db_manager.delete_moneybox(moneybox_id=3)
    await db_manager.delete_moneybox(moneybox_id=4)

    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    assert response.status_code == 204

    # re-add deleted moneyboxes
    await db_manager.add_moneybox(moneybox_data=moneyboxes["moneyboxes"][0])
    await db_manager.add_moneybox(moneybox_data=moneyboxes["moneyboxes"][1])
    await db_manager.add_moneybox(moneybox_data=moneyboxes["moneyboxes"][2])

    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    # test to ensure if moneyboxes were added
    assert response.status_code == 200
    assert response.json() == expected_moneyboxes


@pytest.mark.dependency(depends=["test_endpoint_get_moneyboxes"])
async def test_endpoint_get_moneybox(client: AsyncClient) -> None:
    response_1 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1",
    )
    expected_moneybox_data = {"name": "Test Box 1 - Updated", "id": 1, "balance": 33}
    assert response_1.status_code == 200
    assert response_1.json() == expected_moneybox_data

    response_2 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/0",
    )
    assert response_2.status_code == 422
    content = response_2.json()
    assert content["detail"][0]["type"] == "greater_than_equal"
    assert content["detail"][0]["loc"][0] == "path"
    assert content["detail"][0]["loc"][1] == "moneybox_id"

    response_3 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}",
    )
    assert response_3.status_code == 405


@pytest.mark.dependency(depends=["test_endpoint_get_moneybox"])
async def test_endpoint_add_moneybox(client: AsyncClient) -> None:
    moneybox_data_1 = {"name": "Test Box Endpoint Add 1"}
    response_1 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}", json=moneybox_data_1
    )
    assert response_1.status_code == 200
    assert response_1.json() == moneybox_data_1 | {"id": 5, "balance": 0}

    moneybox_data_2 = {"name": "Test Box Endpoint Add 2", "balance": 1234}
    response_2 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}",
        json=moneybox_data_2,
    )
    assert response_2.status_code == 422

    duplicate = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}",
        json=moneybox_data_1,
    )
    content = duplicate.json()
    assert duplicate.status_code == 405
    assert content["message"] == "Moneybox name 'Test Box Endpoint Add 1' already exists."
    assert len(content["details"]) == 1
    assert content["details"]["name"] == "Test Box Endpoint Add 1"


@pytest.mark.dependency(depends=["test_endpoint_add_moneybox"])
async def test_endpoint_update_moneybox(client: AsyncClient) -> None:
    moneybox_data_1 = {"name": "Test Box Endpoint Add 1 - Updated"}

    missing_id_response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}", json=moneybox_data_1
    )
    assert missing_id_response.status_code == 405

    response_1 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/5", json=moneybox_data_1
    )
    assert response_1.status_code == 200
    assert response_1.json() == moneybox_data_1 | {"id": 5, "balance": 0}


@pytest.mark.dependency(depends=["test_endpoint_update_moneybox"])
async def test_endpoint_delete_moneybox(client: AsyncClient) -> None:
    missing_id_response = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}"
    )
    assert missing_id_response.status_code == 405

    response_1 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/5"
    )
    assert response_1.status_code == 204

    response_2 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/42"
    )
    content_2 = response_2.json()
    assert response_2.status_code == 404
    assert content_2["message"] == "Moneybox with id 42 does not exist."
    assert len(content_2["details"]) == 1
    assert content_2["details"]["id"] == 42

    response_3 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/-1"
    )
    content_3 = response_3.json()
    assert response_3.status_code == 422
    assert content_3["detail"][0]["type"] == "greater_than_equal"
    assert content_3["detail"][0]["loc"][0] == "path"
    assert content_3["detail"][0]["loc"][1] == "moneybox_id"


@pytest.mark.dependency(depends=["test_endpoint_delete_moneybox"])
async def test_endpoint_deposit_moneybox(client: AsyncClient) -> None:
    moneybox_data = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1",
    )

    deposit_data_1 = {"balance": 10}

    response_1 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/add",
        json=deposit_data_1,
    )
    expected_data_1 = moneybox_data.json()
    expected_data_1["balance"] += 10
    assert expected_data_1 == response_1.json()

    deposit_data_2 = {"balance": -1}
    response_2 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/add",
        json=deposit_data_2,
    )
    assert response_2.status_code == 422


@pytest.mark.dependency(depends=["test_endpoint_deposit_moneybox"])
async def test_endpoint_withdraw_moneybox(client: AsyncClient) -> None:
    moneybox_data = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1",
    )

    withdraw_data_1 = {"balance": 10}

    response_1 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/sub",
        json=withdraw_data_1,
    )
    expected_data_1 = moneybox_data.json()
    expected_data_1["balance"] -= 10
    assert expected_data_1 == response_1.json()

    deposit_data_2 = {"balance": -1}
    response_2 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/add",
        json=deposit_data_2,
    )
    assert response_2.status_code == 422
