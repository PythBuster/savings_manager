"""All moneybox endpoint tests are located here."""

from datetime import datetime

import pytest
from httpx import AsyncClient

from src.custom_types import EndpointRouteType
from src.db.db_manager import DBManager
from src.utils import equal_dict, equal_list_of_dict


@pytest.mark.dependency(depends=["tests/test_db_manager.py::test_transfer_amount"], scope="session")
async def test_endpoint_get_moneyboxes_exist_5(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    expected_moneyboxes = {
        "total": 5,
        "moneyboxes": [
            {"name": "Test Box 1", "id": 1, "balance": 0},
            {"name": "Test Box 2", "id": 2, "balance": 0},
            {"name": "Test Box 3", "id": 3, "balance": 0},
            {"name": "Test Box 4", "id": 4, "balance": 0},
            {"name": "Test Box 5", "id": 5, "balance": 0},
        ],
    }

    moneyboxes = response.json()

    assert response.status_code == 200
    assert moneyboxes["total"] == expected_moneyboxes["total"]

    for dict_1, dict_2 in zip(  # type: ignore
        moneyboxes["moneyboxes"], expected_moneyboxes["moneyboxes"]
    ):
        assert equal_dict(
            dict_1=dict_1,
            dict_2=dict_2,
            exclude_keys=["created_at", "modified_at"],
        )


@pytest.mark.dependency(depends=["tests/test_db_manager.py::test_transfer_amount"], scope="session")
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
    assert moneyboxes["total"] == expected_moneyboxes["total"]

    assert equal_list_of_dict(
        list_dict_1=moneyboxes["moneyboxes"],
        list_dict_2=expected_moneyboxes["moneyboxes"],  # type: ignore
        exclude_keys=["created_at", "modified_at", "id"],
    )

    # delete money all boxes
    await db_manager.update_moneybox(moneybox_id=1, moneybox_data={"balance": 0})
    await db_manager.update_moneybox(moneybox_id=3, moneybox_data={"balance": 0})

    await db_manager.delete_moneybox(moneybox_id=1)
    await db_manager.delete_moneybox(moneybox_id=3)
    await db_manager.delete_moneybox(moneybox_id=4)

    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    assert response.status_code == 204

    # restore deleted moneyboxes
    await db_manager._restore_moneybox(moneybox_id=1)  # pylint: disable=protected-access
    await db_manager._restore_moneybox(moneybox_id=3)  # pylint: disable=protected-access
    await db_manager._restore_moneybox(moneybox_id=4)  # pylint: disable=protected-access

    await db_manager.update_moneybox(moneybox_id=1, moneybox_data={"balance": 33})
    await db_manager.update_moneybox(moneybox_id=3, moneybox_data={"balance": 300})

    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    moneyboxes = response.json()

    # test to ensure if moneyboxes were added
    assert response.status_code == 200

    assert moneyboxes["total"] == expected_moneyboxes["total"]
    assert equal_list_of_dict(
        list_dict_1=moneyboxes["moneyboxes"],
        list_dict_2=expected_moneyboxes["moneyboxes"],  # type: ignore
        exclude_keys=["created_at", "modified_at", "id"],
    )


@pytest.mark.dependency(depends=["test_endpoint_get_moneyboxes"])
async def test_endpoint_get_moneybox(client: AsyncClient) -> None:
    response_1 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1",
    )
    moneybox = response_1.json()

    expected_moneybox_data = {"name": "Test Box 1 - Updated", "id": 1, "balance": 33}

    assert response_1.status_code == 200
    assert equal_dict(
        dict_1=moneybox,
        dict_2=expected_moneybox_data,  # type: ignore
        exclude_keys=["created_at", "modified_at"],
    )

    response_2 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/0",
    )
    assert response_2.status_code == 404

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
    moneybox = response_1.json()

    assert response_1.status_code == 200
    assert equal_dict(
        dict_1=moneybox,
        dict_2=moneybox_data_1 | {"id": 7, "balance": 0},
        exclude_keys=["created_at", "modified_at"],
    )

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
    assert content["message"] == (
        "Creation Error: Please choose another name, 'Test Box Endpoint Add 1' "
        "is already in use (case insensitive)."
    )
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
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/7", json=moneybox_data_1
    )
    monneybox = response_1.json()

    assert response_1.status_code == 200
    assert equal_dict(
        dict_1=monneybox,
        dict_2=moneybox_data_1 | {"id": 7, "balance": 0},
        exclude_keys=["created_at", "modified_at"],
    )


@pytest.mark.dependency(depends=["test_endpoint_update_moneybox"])
async def test_endpoint_delete_moneybox(client: AsyncClient) -> None:
    missing_id_response = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}"
    )
    assert missing_id_response.status_code == 405

    response_1 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/7"
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
    assert response_3.status_code == 404

    # can't delete moneybox 1, because balance > 0, expected 405 not allowed
    response_4 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1"
    )
    assert response_4.status_code == 405


@pytest.mark.dependency(depends=["test_endpoint_delete_moneybox"])
async def test_endpoint_deposit_moneybox(client: AsyncClient) -> None:
    moneybox_data = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1",
    )

    deposit_data_1 = {
        "amount": 10,
        "description": "Bonus.",
    }

    response_1 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/add",
        json=deposit_data_1,
    )
    moneybox = response_1.json()

    expected_data_1 = moneybox_data.json()
    expected_data_1["balance"] += 10
    assert equal_dict(
        dict_1=expected_data_1,
        dict_2=moneybox,
        exclude_keys=["created_at", "modified_at"],
    )

    deposit_data_2 = {
        "amount": 0,
        "description": "Bonus.",
    }
    response_2 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/add",
        json=deposit_data_2,
    )
    assert response_2.status_code == 422

    deposit_data_3 = {
        "deposit_data": {"amount": -1},
        "transaction_data": {
            "description": "Bonus.",
            "transaction_trigger": "manually",
            "transaction_type": "direct",
        },
    }
    response_3 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/add",
        json=deposit_data_3,
    )
    assert response_3.status_code == 422


@pytest.mark.dependency(depends=["test_endpoint_deposit_moneybox"])
async def test_endpoint_withdraw_moneybox(client: AsyncClient) -> None:
    moneybox_data = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1",
    )

    withdraw_data_1 = {
        "amount": 10,
        "description": "Unexpected expenses.",
    }

    response_1 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/sub",
        json=withdraw_data_1,
    )
    moneybox = response_1.json()
    expected_data_1 = moneybox_data.json()

    expected_data_1["balance"] -= 10
    assert equal_dict(
        dict_1=expected_data_1,
        dict_2=moneybox,
        exclude_keys=["created_at", "modified_at"],
    )

    deposit_data_2 = {
        "amount": 0,
        "description": "Unexpected expenses.",
    }
    response_2 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/sub",
        json=deposit_data_2,
    )
    assert response_2.status_code == 422

    deposit_data_3 = {
        "amount": -1,
        "description": "Unexpected expenses.",
    }
    response_3 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/sub",
        json=deposit_data_3,
    )
    assert response_3.status_code == 422


@pytest.mark.dependency(depends=["test_endpoint_deposit_moneybox"])
async def test_endpoint_transfer_amount_moneybox(client: AsyncClient) -> None:
    response_moneybox_id_1_data = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1",
    )
    moneybox_id_1_data = response_moneybox_id_1_data.json()

    respose_moneybox_id_3_data = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/3",
    )
    moneybox_id_3_data = respose_moneybox_id_3_data.json()

    transfer_data_1 = {
        "amount": 50,
        "to_moneybox_id": 1,
        "description": "Transfer money.",
    }

    response_1 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/3/balance/transfer",
        json=transfer_data_1,
    )
    assert response_1.status_code == 204

    response_new_moneybox_id_1_data = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1",
    )
    new_moneybox_id_1_data = response_new_moneybox_id_1_data.json()

    assert moneybox_id_1_data["modified_at"] < new_moneybox_id_1_data["modified_at"]
    moneybox_id_1_data["balance"] += 50
    assert equal_dict(
        dict_1=moneybox_id_1_data,
        dict_2=new_moneybox_id_1_data,
        exclude_keys=["created_at", "modified_at"],
    )

    response_new_moneybox_id_3_data = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/3",
    )
    new_moneybox_id_3_data = response_new_moneybox_id_3_data.json()

    try:
        datetime.fromisoformat(new_moneybox_id_3_data["modified_at"])
    except:  # noqa: E722  # pylint: disable=bare-except
        assert False, "Invalid datetime"

    moneybox_id_3_data["balance"] -= 50
    assert equal_dict(
        dict_1=moneybox_id_3_data,
        dict_2=new_moneybox_id_3_data,
        exclude_keys=["created_at", "modified_at"],
    )

    response_2 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/transfer",
        json=transfer_data_1,
    )
    assert response_2.status_code == 405
