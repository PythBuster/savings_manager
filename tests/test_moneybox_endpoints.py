"""All moneybox endpoint tests are located here."""

import asyncio
from datetime import datetime

import pytest
from httpx import AsyncClient
from starlette import status

from src.custom_types import EndpointRouteType
from src.utils import equal_dict


@pytest.mark.dependency(depends=["tests/test_db_manager.py::test_transfer_amount"], scope="session")
async def test_endpoint_get_moneyboxes__status_200__total_6(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    expected_moneyboxes = {
        "total": 6,
        "moneyboxes": [
            {
                "name": "1bd2a9ee-26a1-4630-a068-19865cf2ca62",
                "id": 1,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": None,
                "priority": 0,
            },
            {
                "name": "Test Box 1",
                "id": 2,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": None,
                "priority": 1,
            },
            {
                "name": "Test Box 2",
                "id": 3,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": None,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "id": 4,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "id": 5,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": None,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "id": 6,
                "balance": 0,
                "savings_amount": 0,
                "savings_target": None,
                "priority": 5,
            },
        ],
    }

    moneyboxes = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert moneyboxes["total"] == expected_moneyboxes["total"]

    for dict_1, dict_2 in zip(  # type: ignore
        moneyboxes["moneyboxes"], expected_moneyboxes["moneyboxes"]
    ):
        assert equal_dict(
            dict_1=dict_1,
            dict_2=dict_2,
            exclude_keys=["created_at", "modified_at"],
        )


@pytest.mark.dependency
async def test_endpoint_get_moneyboxes__status_204__no_content(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )

    # there should be always at least one moneybox: the overflow moneybox
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.dependency
async def test_endpoint_get_moneybox__moneybox_id_2__status_200_existing(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2",
    )
    moneybox = response.json()

    expected_moneybox_data = {
        "name": "Test Box 1",
        "id": 2,
        "balance": 0,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox,
        dict_2=expected_moneybox_data,  # type: ignore
        exclude_keys=["created_at", "modified_at"],
    )


@pytest.mark.dependency
async def test_endpoint_get_moneybox_status_404_non_existing(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/10",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_get_moneybox__moneybox_id_2__status_200_existing__with_balance_100(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2",
    )
    moneybox = response.json()

    expected_moneybox_data = {
        "name": "Test Box 1",
        "id": 2,
        "balance": 100,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox,
        dict_2=expected_moneybox_data,  # type: ignore
        exclude_keys=["created_at", "modified_at"],
    )


@pytest.mark.dependency
async def test_endpoint_add_moneybox__one__status_200(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    moneybox_data = {
        "name": "Test Box Endpoint Add 1",
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}", json=moneybox_data
    )
    moneybox = response.json()

    expected_moneybox_data = {
        "name": "Test Box Endpoint Add 1",
        "id": 2,
        "balance": 0,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox,
        dict_2=expected_moneybox_data,
        exclude_keys=["created_at", "modified_at"],
    )


@pytest.mark.dependency
async def test_endpoint_add_moneybox__two__status_200(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    moneybox_data_1 = {
        "name": "Test Box Endpoint Add 1",
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }
    response_1 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}", json=moneybox_data_1
    )
    moneybox_1 = response_1.json()

    expected_moneybox_data_1 = {
        "name": "Test Box Endpoint Add 1",
        "id": 2,
        "balance": 0,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    assert response_1.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_1,
        dict_2=expected_moneybox_data_1,
        exclude_keys=["created_at", "modified_at"],
    )

    moneybox_data_2 = {
        "name": "Test Box Endpoint Add 2",
        "savings_amount": 0,
        "savings_target": None,
        "priority": 2,
    }
    response_2 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}",
        json=moneybox_data_2,
    )
    moneybox_2 = response_2.json()

    expected_moneybox_data_2 = {
        "name": "Test Box Endpoint Add 2",
        "id": 3,
        "balance": 0,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 2,
    }

    assert response_2.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_2,
        dict_2=expected_moneybox_data_2,
        exclude_keys=["created_at", "modified_at"],
    )


@pytest.mark.dependency
async def test_endpoint_add_moneybox__one__status_422__balance_postdata(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    # balance not allowed in post data
    moneybox_data = {"name": "Test Box Endpoint Add 1", "balance": 200}

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}", json=moneybox_data
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.dependency
async def test_endpoint_update_overflow_moneybox(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    moneybox_data_1 = {
        "name": "Updated Name Test Box 1",
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    response_1 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1", json=moneybox_data_1
    )
    content = response_1.json()
    assert response_1.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert content["message"] == "Updating overflow moneybox is not allowed/possible!"


@pytest.mark.dependency
async def test_endpoint_delete_overflow_moneybox__status_405(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.delete(f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {
        "details": {
            "id": 1,
        },
        "message": "Deleting overflow moneybox is not allowed/possible!",
    }


@pytest.mark.dependency
async def test_endpoint_update_moneybox__moneybox_id_4__namechange(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    moneybox_data_4 = {
        "name": "Updated Name Test Box 4",
        "savings_amount": 0,
        "savings_target": None,
        "priority": 3,
    }
    expected_moneybox_data_4 = {
        "name": "Updated Name Test Box 4",
        "id": 4,
        "balance": 0,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 3,
    }

    response_4 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/4", json=moneybox_data_4
    )
    moneybox_4 = response_4.json()
    assert response_4.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_4,
        dict_2=expected_moneybox_data_4,
        exclude_keys=["created_at", "modified_at"],
    )

    # no change should be happened for moneyboxes id=2 and id=3
    response_2 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2",
    )
    moneybox_2 = response_2.json()
    expected_moneybox_data_2 = {
        "name": "Test Box 1",
        "id": 2,
        "balance": 0,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    assert response_2.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_2,
        dict_2=expected_moneybox_data_2,
        exclude_keys=["created_at", "modified_at"],
    )

    response_3 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/3",
    )
    moneybox_3 = response_3.json()
    expected_moneybox_data_3 = {
        "name": "Test Box 2",
        "id": 3,
        "balance": 0,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 2,
    }

    assert response_3.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_3,
        dict_2=expected_moneybox_data_3,
        exclude_keys=["created_at", "modified_at"],
    )


@pytest.mark.dependency
async def test_endpoint_moneybox_id_2__modified_at_checks(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response_1 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2",
    )
    content_1 = response_1.json()
    assert content_1["modified_at"] is None

    moneybox_data_2 = {
        "name": "Updated Name Test Box 1",
    }
    response_2 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2", json=moneybox_data_2
    )
    content_2 = response_2.json()

    assert content_2["modified_at"] is not None

    # sleep to get higher modified_at datetime (simulate time passing before modifying data)
    await asyncio.sleep(1)

    moneybox_data_3 = {"name": "RE-Updated Name Test Box 1"}
    response_3 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2", json=moneybox_data_3
    )
    content_3 = response_3.json()
    assert datetime.fromisoformat(content_3["modified_at"]) > datetime.fromisoformat(
        content_2["modified_at"]
    )


@pytest.mark.dependency
async def test_endpoint_update_moneybox__moneybox_id_1__status_422__fail_extra_fields(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    # balance not allowed in update data
    moneybox_data_1 = {"name": "Updated Test Box 1", "balance": 200}

    response_1 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1", json=moneybox_data_1
    )

    assert response_1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # unknown extra field not allowed in update data
    moneybox_data_2 = {"name": "Updated Test Box 1", "unknwon_field": "xyz"}

    response_2 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2", json=moneybox_data_2
    )

    assert response_2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.dependency
async def test_endpoint_delete_moneybox_2__status_204(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response_1 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    moneyboxes = response_1.json()

    assert moneyboxes["total"] == 3

    response_2 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2"
    )
    assert response_2.status_code == status.HTTP_204_NO_CONTENT

    response_3 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    moneyboxes = response_3.json()

    assert moneyboxes["total"] == 2


@pytest.mark.dependency
async def test_endpoint_delete_moneybox_2__non_existing__status_404(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.delete(f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_delete_moneybox_2__non_existing_after_success_deletion__status_204_and_404(
    load_test_data: None, client: AsyncClient  # pylint: disable=unused-argument
) -> None:
    response_1 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2"
    )
    assert response_1.status_code == status.HTTP_204_NO_CONTENT

    response_2 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2"
    )
    assert response_2.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_deposit_moneybox_2__status_200(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    deposit_data = {
        "amount": 100,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/add",
        json=deposit_data,
    )
    moneybox = response.json()

    expected_data = {
        "name": "Test Box 1",
        "id": 2,
        "balance": 100,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=expected_data,
        dict_2=moneybox,
        exclude_keys=["created_at", "modified_at"],
    )


@pytest.mark.dependency
async def test_endpoint_deposit_moneybox_2__status_422__fail_extra_field(
    client: AsyncClient,
) -> None:
    deposit_data = {
        "amount": 100,
        "description": "Bonus.",
        "extra_field": "wow",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/add",
        json=deposit_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.dependency
async def test_endpoint_deposit_moneybox_2__status_422__missing_required_amount_field(
    client: AsyncClient,
) -> None:
    deposit_data = {
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/add",
        json=deposit_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "missing" == content["detail"][0]["type"]
    assert "amount" in content["detail"][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_deposit_moneybox_2__status_422__negative_amount(
    client: AsyncClient,
) -> None:
    deposit_data = {
        "amount": -100,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/add",
        json=deposit_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "greater_than_equal" == content["detail"][0]["type"]
    assert "amount" in content["detail"][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_deposit_moneybox_2__status_422__zero_amount(
    client: AsyncClient,
) -> None:
    deposit_data = {
        "amount": 0,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/add",
        json=deposit_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "greater_than_equal" == content["detail"][0]["type"]
    assert "amount" in content["detail"][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_withdraw_moneybox_2__status_200(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    withdraw_data = {
        "amount": 99,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/sub",
        json=withdraw_data,
    )
    moneybox = response.json()

    expected_data = {
        "name": "Test Box 1",
        "id": 2,
        "balance": 1,
        "savings_amount": 0,
        "savings_target": None,
        "priority": 1,
    }

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=expected_data,
        dict_2=moneybox,
        exclude_keys=["created_at", "modified_at"],
    )


@pytest.mark.dependency
async def test_endpoint_withdraw_moneybox_2__status_422__fail_extra_field(
    client: AsyncClient,
) -> None:
    withdraw_data = {
        "amount": 100,
        "description": "",
        "extra_field": "wow",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/sub",
        json=withdraw_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.dependency
async def test_endpoint_withdraw_moneybox_2__status_422__missing_required_amount_field(
    client: AsyncClient,
) -> None:
    withdraw_data = {
        "description": "",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/sub",
        json=withdraw_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "missing" == content["detail"][0]["type"]
    assert "amount" in content["detail"][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_withdraw_moneybox_2__status_422__negative_amount(
    client: AsyncClient,
) -> None:
    withdraw_data = {
        "amount": -100,
        "description": "",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/sub",
        json=withdraw_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "greater_than_equal" == content["detail"][0]["type"]
    assert "amount" in content["detail"][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_withdraw_moneybox_2__status_422__zero_amount(
    client: AsyncClient,
) -> None:
    withdraw_data = {
        "amount": 0,
        "description": "",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/sub",
        json=withdraw_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "greater_than_equal" == content["detail"][0]["type"]
    assert "amount" in content["detail"][0]["loc"]


async def test_endpoint_withdraw_moneybox_2__status_405__balance_negative(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    withdraw_data = {
        "amount": 101,
        "description": "",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/sub",
        json=withdraw_data,
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_2_to_moneybox_3__status_204(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    transfer_data = {
        "amount": 500,
        "to_moneybox_id": 3,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/transfer",
        json=transfer_data,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_2_to_moneybox_3__status_204__missing_description_field(  # noqa: E501
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    transfer_data = {
        "amount": 500,
        "to_moneybox_id": 3,
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/transfer",
        json=transfer_data,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_2_to_moneybox_3__status_422__missing_amount_field(
    client: AsyncClient,
) -> None:
    transfer_data = {
        "to_moneybox_id": 3,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/transfer",
        json=transfer_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "missing" == content["detail"][0]["type"]
    assert "amount" in content["detail"][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_2_to_moneybox_3__status_422__missing_to_moneybox_id_field(  # noqa: E501
    client: AsyncClient,
) -> None:
    transfer_data = {
        "amount": 500,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/transfer",
        json=transfer_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "missing" == content["detail"][0]["type"]
    assert "to_moneybox_id" in content["detail"][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_2_to_moneybox_3__status_422__status_422__fail_extra_field(  # noqa: E501
    client: AsyncClient,
) -> None:
    transfer_data = {
        "amount": 500,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/transfer",
        json=transfer_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "missing" == content["detail"][0]["type"]
    assert "to_moneybox_id" in content["detail"][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_2_to_moneybox_3__status_422__negative_amount(
    client: AsyncClient,
) -> None:
    transfer_data = {
        "amount": -500,
        "to_moneybox_id": 3,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/transfer",
        json=transfer_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "greater_than_equal" == content["detail"][0]["type"]
    assert "amount" in content["detail"][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_2_to_moneybox_3__status_422__zero_amount(
    client: AsyncClient,
) -> None:
    transfer_data = {
        "amount": 0,
        "to_moneybox_id": 3,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/transfer",
        json=transfer_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "greater_than_equal" == content["detail"][0]["type"]
    assert "amount" in content["detail"][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_2_to_moneybox_3__status_404__to_moneybox_id_3_not_found(  # noqa: E501
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    transfer_data = {
        "amount": 500,
        "to_moneybox_id": 3,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/balance/transfer",
        json=transfer_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_get_transactions_log_moneybox_2__status_200(  # noqa: E501
    default_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2/transactions",
    )
    content = response.json()

    expected_logs = [
        {
            "id": 2,
            "counterparty_moneybox_name": None,
            "description": "",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": 1000,
            "balance": 1000,
            "counterparty_moneybox_id": None,
            "moneybox_id": 2,
        },
        {
            "id": 3,
            "counterparty_moneybox_name": None,
            "description": "",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": 333,
            "balance": 1333,
            "counterparty_moneybox_id": None,
            "moneybox_id": 2,
        },
        {
            "id": 4,
            "counterparty_moneybox_name": None,
            "description": "",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": 2000,
            "balance": 3333,
            "counterparty_moneybox_id": None,
            "moneybox_id": 2,
        },
        {
            "id": 5,
            "counterparty_moneybox_name": "Moneybox 2",
            "description": "",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": -3000,
            "balance": 333,
            "counterparty_moneybox_id": 3,
            "moneybox_id": 2,
        },
        {
            "id": 18,
            "counterparty_moneybox_name": "Moneybox 4",
            "description": "",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": 15000,
            "balance": 15333,
            "counterparty_moneybox_id": 5,
            "moneybox_id": 2,
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert content["total"] == 5

    for i, expected_log in enumerate(expected_logs):
        assert equal_dict(
            dict_1=expected_log,  # type: ignore
            dict_2=content["transaction_logs"][i],
            exclude_keys=["modified_at", "created_at", "id"],
        )


@pytest.mark.dependency
async def test_endpoint_get_transactions_log_moneybox_3__status_200(  # noqa: E501
    default_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/3/transactions",
    )
    content = response.json()

    expected_logs = [
        {
            "counterparty_moneybox_name": "Moneybox 1",
            "description": "",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": 3000,
            "balance": 3000,
            "counterparty_moneybox_id": 2,
            "moneybox_id": 3,
        },
        {
            "counterparty_moneybox_name": None,
            "description": "",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": 6000,
            "balance": 9000,
            "counterparty_moneybox_id": None,
            "moneybox_id": 3,
        },
        {
            "counterparty_moneybox_name": None,
            "description": "",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": -500,
            "balance": 8500,
            "counterparty_moneybox_id": None,
            "moneybox_id": 3,
        },
        {
            "counterparty_moneybox_name": None,
            "description": "",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": -600,
            "balance": 7900,
            "counterparty_moneybox_id": None,
            "moneybox_id": 3,
        },
        {
            "counterparty_moneybox_name": None,
            "description": "",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": 5000,
            "balance": 12900,
            "counterparty_moneybox_id": None,
            "moneybox_id": 3,
        },
        {
            "counterparty_moneybox_name": None,
            "description": "",
            "transaction_type": "direct",
            "transaction_trigger": "manually",
            "amount": -900,
            "balance": 12000,
            "counterparty_moneybox_id": None,
            "moneybox_id": 3,
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert content["total"] == 6

    for i, expected_log in enumerate(expected_logs):
        assert equal_dict(
            dict_1=expected_log,  # type: ignore
            dict_2=content["transaction_logs"][i],
            exclude_keys=["modified_at", "created_at", "id"],
        )


@pytest.mark.dependency
async def test_endpoint_get_transactions_log_moneybox_6__status_204(  # noqa: E501
    default_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/6/transactions",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.dependency
async def test_endpoint_get_transactions_log_moneybox_5__status_404__deleted_and_not_found(  # noqa: E501
    default_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/5/transactions",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_get_transactions_log_moneybox_7__status_404__not_existing_and_not_found(  # noqa: E501
    default_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/7/transactions",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
