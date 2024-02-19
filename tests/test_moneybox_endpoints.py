"""All moneybox endpoint tests are located here."""

import pytest
from httpx import AsyncClient

from src.custom_types import EndpointRouteType
from src.db.db_manager import DBManager
from src.db.exceptions import MoneyboxNameExistError, MoneyboxNotFoundError


@pytest.mark.dependency(depends=["tests/test_db_manager.py::test_delete_moneybox"], scope="session")
async def test_endpoint_get_moneyboxes(db_manager: DBManager, client: AsyncClient) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    expected_moneyboxes = {
        "total": 3,
        "moneyboxes": [
            {"name": "Test Box 1 - Updated", "id": 1, "balance": 0},
            {"name": "Test Box 3", "id": 3, "balance": 333},
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


@pytest.mark.dependency(depends=["tests/test_db_manager.py::test_delete_moneybox"], scope="session")
async def test_endpoint_get_moneybox(client: AsyncClient) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1",
    )
    expected_moneybox_data = {"name": "Test Box 1 - Updated", "id": 1, "balance": 0}

    assert response.status_code == 200
    assert response.json() == expected_moneybox_data


@pytest.mark.dependency(depends=["tests/test_db_manager.py::test_delete_moneybox"], scope="session")
async def test_endpoint_add_moneybox(client: AsyncClient) -> None:
    moneybox_data_1 = {"name": "Test Box Endpoint Add 1", "balance": 0}
    moneybox_data_2 = {"name": "Test Box Endpoint Add 2", "balance": 1234}

    response_1 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}", json=moneybox_data_1
    )
    assert response_1.status_code == 200
    assert response_1.json() == moneybox_data_1 | {"id": 5}

    response_2 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}",
        json=moneybox_data_2,
    )
    assert response_2.status_code == 200
    assert response_2.json() == moneybox_data_2 | {"id": 6}

    with pytest.raises(MoneyboxNameExistError) as ex_info:
        await client.post(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}",
            json=moneybox_data_2,
        )

    assert "Moneybox name 'Test Box Endpoint Add 2' already exists." in ex_info.value.args[0]
    assert "Test Box Endpoint Add 2" == ex_info.value.details["name"]


@pytest.mark.dependency(depends=["tests/test_db_manager.py::test_delete_moneybox"], scope="session")
async def test_endpoint_patch_moneybox(client: AsyncClient) -> None:
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


@pytest.mark.dependency(depends=["tests/test_db_manager.py::test_delete_moneybox"], scope="session")
async def test_endpoint_delete_moneybox(client: AsyncClient) -> None:
    missing_id_response = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}"
    )
    assert missing_id_response.status_code == 405

    response_1 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/5"
    )
    assert response_1.status_code == 204

    with pytest.raises(MoneyboxNotFoundError) as ex_info:
        await client.delete(f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/42")

    assert "Moneybox with id 42 does not exist." in ex_info.value.args[0]
    assert {"id": 42} == ex_info.value.details

    with pytest.raises(MoneyboxNotFoundError) as ex_info:
        await client.delete(f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/-1")

    assert "Moneybox with id -1 does not exist." in ex_info.value.args[0]
    assert {"id": -1} == ex_info.value.details
