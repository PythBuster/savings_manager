"""All moneybox endpoint tests are located here."""

from datetime import datetime

import pytest
from httpx import AsyncClient
from starlette import status

from src.custom_types import EndpointRouteType
from src.utils import equal_dict


@pytest.mark.dependency(depends=["tests/test_db_manager.py::test_transfer_amount"], scope="session")
async def test_endpoint_get_moneyboxes__status_200__total_5(
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

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.dependency
async def test_endpoint_get_moneybox__moneybox_id_1__status_200_existing(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1",
    )
    moneybox = response.json()

    expected_moneybox_data = {"name": "Test Box 1", "id": 1, "balance": 0}

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
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/0",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_get_moneybox__status_405__path_incomplete(client: AsyncClient) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}",
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.dependency
async def test_endpoint_get_moneybox__moneybox_id_2__status_200_existing__with_balance_100(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2",
    )
    moneybox = response.json()

    expected_moneybox_data = {"name": "Test Box 2", "id": 2, "balance": 100}

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
    moneybox_data = {"name": "Test Box Endpoint Add 1"}
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}", json=moneybox_data
    )
    moneybox = response.json()

    expected_moneybox_data = {"name": "Test Box Endpoint Add 1", "id": 1, "balance": 0}

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
    moneybox_data_1 = {"name": "Test Box Endpoint Add 1"}
    response_1 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}", json=moneybox_data_1
    )
    moneybox_1 = response_1.json()

    expected_moneybox_data_1 = {"name": "Test Box Endpoint Add 1", "id": 1, "balance": 0}

    assert response_1.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_1,
        dict_2=expected_moneybox_data_1,
        exclude_keys=["created_at", "modified_at"],
    )

    moneybox_data_2 = {"name": "Test Box Endpoint Add 2"}
    response_2 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}",
        json=moneybox_data_2,
    )
    moneybox_2 = response_2.json()

    expected_moneybox_data_2 = {"name": "Test Box Endpoint Add 2", "id": 2, "balance": 0}

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
async def test_endpoint_update_moneybox__moneybox_id_1__namechange(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    moneybox_data_1 = {"name": "Updated Name Test Box 1"}

    response_1 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1", json=moneybox_data_1
    )
    moneybox_1 = response_1.json()
    expected_moneybox_data_1 = moneybox_data_1 | {"id": 1, "balance": 0}

    assert response_1.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_1,
        dict_2=expected_moneybox_data_1,
        exclude_keys=["created_at", "modified_at"],
    )

    # no change should be happened for moneyboxes 2 and 3
    response_2 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/2",
    )
    moneybox_2 = response_2.json()
    expected_moneybox_data_2 = {"name": "Test Box 2", "id": 2, "balance": 0}

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
    expected_moneybox_data_3 = {"name": "Test Box 3", "id": 3, "balance": 0}

    assert response_2.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_3,
        dict_2=expected_moneybox_data_3,
        exclude_keys=["created_at", "modified_at"],
    )


@pytest.mark.dependency
async def test_endpoint_update_moneybox__moneybox_id_1__status_422__fail_extra_field(
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
async def test_endpoint_delete_moneybox_1__status_204(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response_1 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    moneyboxes = response_1.json()

    assert moneyboxes["total"] == 2

    response_2 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1"
    )
    assert response_2.status_code == status.HTTP_204_NO_CONTENT

    response_3 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    moneyboxes = response_3.json()

    assert moneyboxes["total"] == 1


@pytest.mark.dependency
async def test_endpoint_delete_moneybox_1__non_existing__status_404(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.delete(f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_delete_moneybox_1__non_existing_after_success_deletion__status_204_and_404(
    load_test_data: None, client: AsyncClient  # pylint: disable=unused-argument
) -> None:
    response_1 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1"
    )
    assert response_1.status_code == status.HTTP_204_NO_CONTENT

    response_2 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1"
    )
    assert response_2.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_delete_moneybox__status_405__missing_moneybox_id_in_valid_path(
        client: AsyncClient
) -> None:
    response = await client.delete(f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.dependency
async def test_endpoint_deposit_moneybox_1__status_200(
        load_test_data: None,
        client: AsyncClient
) -> None:
    deposit_data = {
        "amount": 100,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/add",
        json=deposit_data,
    )
    moneybox = response.json()

    expected_data = {
        "name": "Test Box 1",
        "id": 1,
        "balance": 100,
    }

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=expected_data,
        dict_2=moneybox,
        exclude_keys=["created_at", "modified_at"],
    )


@pytest.mark.dependency
async def test_endpoint_deposit_moneybox_1__status_422__fail_extra_field(
        client: AsyncClient
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
async def test_endpoint_deposit_moneybox_1__status_404__missing_moneybox_id_invalid_path(
        client: AsyncClient
) -> None:
    deposit_data = {
        "amount": 100,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/balance/add",
        json=deposit_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_deposit_moneybox_1__status_422__negative_amount(
        load_test_data: None,
        client: AsyncClient
) -> None:
    deposit_data = {
        "amount": -100,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1/balance/add",
        json=deposit_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


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
