"""All moneybox endpoint tests are located here."""

import asyncio
from datetime import datetime

import pytest
from httpx import AsyncClient
from starlette import status

from src.custom_types import EndpointRouteType
from src.db.db_manager import DBManager
from src.utils import equal_dict


@pytest.mark.dependency(
    depends=["tests/test_db_manager.py::test_update_app_settings_valid"], scope="session"
)
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
                "name": "Overflow Moneybox",
                "id": 1,
                "balance": 0,
                "savingsAmount": 0,
                "savingsTarget": None,
                "priority": 0,
            },
            {
                "name": "Test Box 1",
                "id": 2,
                "balance": 0,
                "savingsAmount": 0,
                "savingsTarget": None,
                "priority": 1,  # pylint: disable=duplicate-code
            },
            {
                "name": "Test Box 2",
                "id": 3,
                "balance": 0,
                "savingsAmount": 0,
                "savingsTarget": None,
                "priority": 2,
            },
            {
                "name": "Test Box 3",
                "id": 4,
                "balance": 0,
                "savingsAmount": 0,
                "savingsTarget": None,
                "priority": 3,
            },
            {
                "name": "Test Box 4",
                "id": 5,
                "balance": 0,
                "savingsAmount": 0,
                "savingsTarget": None,
                "priority": 4,
            },
            {
                "name": "Test Box 5",
                "id": 6,
                "balance": 0,
                "savingsAmount": 0,
                "savingsTarget": None,
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
            exclude_keys=["createdAt", "modifiedAt", "id"],
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
async def test_endpoint_get_moneybox__second_moneybox__status_200_existing(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    moneyboxes = await db_manager.get_moneyboxes()
    moneybox_id = moneyboxes[-1]["id"]
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{moneybox_id}",
    )
    moneybox = response.json()

    expected_moneybox_data = {
        "name": "Test Box 1",
        "id": moneybox_id,
        "balance": 0,
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 1,
    }

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox,
        dict_2=expected_moneybox_data,  # type: ignore
        exclude_keys=["createdAt", "modifiedAt"],
    )


@pytest.mark.dependency
async def test_endpoint_get_moneybox_status_404_non_existing(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/10",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.dependency
async def test_endpoint_get_moneybox__second_moneybox__status_200_existing__with_balance_100(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: ignore  # pylint:disable=protected-access, line-too-long
        name="Test Box 2",
    )
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{moneybox_id}",
    )
    moneybox = response.json()

    expected_moneybox_data = {
        "name": "Test Box 2",
        "id": moneybox_id,
        "balance": 100,
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 2,
    }

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox,
        dict_2=expected_moneybox_data,  # type: ignore
        exclude_keys=["createdAt", "modifiedAt"],
    )


@pytest.mark.dependency
async def test_endpoint_add_moneybox__one__status_200(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    moneybox_data = {
        "name": "Test Box Endpoint Add 1",
        "savingsAmount": 0,
        "savingsTarget": None,
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}", json=moneybox_data
    )
    moneybox = response.json()

    expected_moneybox_data = {
        "name": "Test Box Endpoint Add 1",
        "id": moneybox["id"],
        "balance": 0,
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 1,
    }

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox,
        dict_2=expected_moneybox_data,
        exclude_keys=["createdAt", "modifiedAt", "id"],
    )


@pytest.mark.dependency
async def test_endpoint_add_moneybox__two__status_200(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    moneybox_data_1 = {
        "name": "Test Box Endpoint Add 1",
        "savingsAmount": 0,
        "savingsTarget": None,
    }
    response_1 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}", json=moneybox_data_1
    )
    moneybox_1 = response_1.json()

    expected_moneybox_data_1 = {
        "name": "Test Box Endpoint Add 1",
        "id": moneybox_1["id"],
        "balance": 0,
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 1,
    }

    assert response_1.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_1,
        dict_2=expected_moneybox_data_1,
        exclude_keys=["createdAt", "modifiedAt"],
    )

    moneybox_data_2 = {
        "name": "Test Box Endpoint Add 2",
        "savingsAmount": 0,
        "savingsTarget": None,
    }
    response_2 = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}",
        json=moneybox_data_2,
    )
    moneybox_2 = response_2.json()

    expected_moneybox_data_2 = {
        "name": "Test Box Endpoint Add 2",
        "id": moneybox_2["id"],
        "balance": 0,
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 2,
    }

    assert response_2.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_2,
        dict_2=expected_moneybox_data_2,
        exclude_keys=["createdAt", "modifiedAt"],
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

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.dependency
async def test_endpoint_update_overflow_moneybox(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    moneyboxes = await db_manager.get_moneyboxes()
    moneybox_id = moneyboxes[0]["id"]

    moneybox_data_1 = {
        "name": "Updated Name Test Box 1",
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 1,
    }

    response_1 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{moneybox_id}",
        json=moneybox_data_1,
    )
    content = response_1.json()
    assert response_1.status_code == status.HTTP_400_BAD_REQUEST
    assert content["message"] == "Updating overflow moneybox is not allowed/possible!"


@pytest.mark.dependency
async def test_endpoint_delete_overflow_moneybox__status_405(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    moneyboxes = await db_manager.get_moneyboxes()
    moneybox_id = moneyboxes[0]["id"]

    response = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{moneybox_id}"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "details": {
            "id": moneybox_id,
        },
        "message": "Deleting overflow moneybox is not allowed/possible!",
    }


@pytest.mark.dependency
async def test_endpoint_update_moneybox__invalid_priority_0(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
        name="Test Box 1"
    )

    moneybox_data = {
        "name": "Updated Name Test Box 4",
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 0,
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    content = response.json()
    assert content["details"]["args"][0][0]["msg"] == "Input should be greater than or equal to 1"
    assert content["details"]["args"][0][0]["loc"][1] == "priority"
    assert content["details"]["args"][0][0]["input"] == 0


@pytest.mark.dependency
async def test_endpoint_update_moneybox__last_moneybox__namechange(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    moneyboxes = await db_manager.get_moneyboxes()
    second_moneybox_id = moneyboxes[-3]["id"]
    third_moneybox_id = moneyboxes[-2]["id"]
    last_moneybox_id = moneyboxes[-1]["id"]

    moneybox_data_4 = {
        "name": "Updated Name Test Box 4",
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 3,
    }
    expected_moneybox_data_4 = {
        "name": "Updated Name Test Box 4",
        "id": last_moneybox_id,
        "balance": 0,
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 3,
    }

    response_4 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{last_moneybox_id}",
        json=moneybox_data_4,
    )
    moneybox_4 = response_4.json()
    assert response_4.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_4,
        dict_2=expected_moneybox_data_4,
        exclude_keys=["createdAt", "modifiedAt"],
    )

    # no change should be happened for moneyboxes id=2 and id=3
    response_2 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}",
    )
    moneybox_2 = response_2.json()
    expected_moneybox_data_2 = {
        "name": "Test Box 1",
        "id": second_moneybox_id,
        "balance": 0,
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 1,
    }

    assert response_2.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_2,
        dict_2=expected_moneybox_data_2,
        exclude_keys=["createdAt", "modifiedAt"],
    )

    response_3 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{third_moneybox_id}",
    )
    moneybox_3 = response_3.json()
    expected_moneybox_data_3 = {
        "name": "Test Box 2",
        "id": third_moneybox_id,
        "balance": 0,
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 2,
    }

    assert response_3.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_3,
        dict_2=expected_moneybox_data_3,
        exclude_keys=["createdAt", "modifiedAt"],
    )


@pytest.mark.dependency
async def test_endpoint_first_moneybox__modified_at_checks(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
        name="Test Box 1"
    )

    response_1 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
    )
    content_1 = response_1.json()
    assert content_1["modifiedAt"] is None

    moneybox_data_2 = {
        "name": "Updated Name Test Box 1",
    }
    response_2 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data_2,
    )
    content_2 = response_2.json()

    assert content_2["modifiedAt"] is not None

    # sleep to get higher modified_at datetime (simulate time passing before modifying data)
    await asyncio.sleep(1)

    moneybox_data_3 = {"name": "RE-Updated Name Test Box 1"}
    response_3 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data_3,
    )
    content_3 = response_3.json()
    assert datetime.fromisoformat(content_3["modifiedAt"]) > datetime.fromisoformat(
        content_2["modifiedAt"]
    )


@pytest.mark.dependency
async def test_endpoint_update_moneybox__first_moneybox__status_422__fail_extra_fields(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
        name="Test Box 1"
    )

    # balance not allowed in update data
    moneybox_data_1 = {"name": "Updated Test Box 1", "balance": 200}

    response_1 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data_1,
    )

    assert response_1.status_code == status.HTTP_400_BAD_REQUEST

    # unknown extra field not allowed in update data
    moneybox_data_2 = {"name": "Updated Test Box 1", "unknwon_field": "xyz"}

    response_2 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data_2,
    )

    assert response_2.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.dependency
async def test_endpoint_delete_second_moneybox__status_204(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
        name="Test Box 1"
    )

    response_1 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    moneyboxes = response_1.json()

    assert moneyboxes["total"] == 3  # type: ignore

    response_2 = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}"
    )
    assert response_2.status_code == status.HTTP_204_NO_CONTENT

    response_3 = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )
    moneyboxes = response_3.json()

    assert moneyboxes["total"] == 2  # type: ignore

    response = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.dependency
async def test_endpoint_deposit_first_moneybox__status_200(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 1"
        )
    )

    deposit_data = {
        "amount": 100,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/balance/add",  # noqa: typing  # pylint: disable=line-too-long
        json=deposit_data,
    )
    moneybox = response.json()

    expected_data = {
        "name": "Test Box 1",
        "id": first_moneybox_id,
        "balance": 100,
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 1,
    }

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=expected_data,
        dict_2=moneybox,
        exclude_keys=["createdAt", "modifiedAt"],
    )


@pytest.mark.dependency
async def test_endpoint_deposit_first_moneybox__status_422__fail_extra_field(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 1"
        )
    )
    deposit_data = {
        "amount": 100,
        "description": "Bonus.",
        "extra_field": "wow",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/balance/add",  # noqa: typing  # pylint: disable=line-too-long
        json=deposit_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.dependency
async def test_endpoint_deposit_first_moneybox__status_422__missing_required_amount_field(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 1"
        )
    )

    deposit_data = {
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/balance/add",  # noqa: typing  # pylint: disable=line-too-long
        json=deposit_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "missing" == content["details"]["args"][0][0]["type"]
    assert "amount" in content["details"]["args"][0][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_deposit_first_moneybox__status_422__negative_amount(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 1"
        )
    )

    deposit_data = {
        "amount": -100,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/balance/add",  # noqa: typing  # pylint: disable=line-too-long
        json=deposit_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "greater_than_equal" == content["details"]["args"][0][0]["type"]
    assert "amount" in content["details"]["args"][0][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_deposit_first_moneybox__status_422__zero_amount(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 1"
        )
    )

    deposit_data = {
        "amount": 0,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/balance/add",  # noqa: typing  # pylint: disable=line-too-long
        json=deposit_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "greater_than_equal" == content["details"]["args"][0][0]["type"]
    assert "amount" in content["details"]["args"][0][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_withdraw_first_moneybox__status_200(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 1"
        )
    )

    withdraw_data = {
        "amount": 99,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/balance/sub",  # noqa: typing  # pylint: disable=line-too-long
        json=withdraw_data,
    )
    moneybox = response.json()

    expected_data = {
        "name": "Test Box 1",
        "id": first_moneybox_id,
        "balance": 1,
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 1,
    }

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=expected_data,
        dict_2=moneybox,
        exclude_keys=["createdAt", "modifiedAt"],
    )


@pytest.mark.dependency
async def test_endpoint_withdraw_first_moneybox__status_422__fail_extra_field(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 1"
        )
    )

    withdraw_data = {
        "amount": 100,
        "description": "",
        "extra_field": "wow",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/balance/sub",  # noqa: typing  # pylint: disable=line-too-long
        json=withdraw_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.dependency
async def test_endpoint_withdraw_first_moneybox__status_422__missing_required_amount_field(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 1"
        )
    )

    withdraw_data = {
        "description": "",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/balance/sub",  # noqa: typing  # pylint: disable=line-too-long
        json=withdraw_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "missing" == content["details"]["args"][0][0]["type"]
    assert "amount" in content["details"]["args"][0][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_withdraw_first_moneybox__status_422__negative_amount(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 1"
        )
    )

    withdraw_data = {
        "amount": -100,
        "description": "",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/balance/sub",  # noqa: typing  # pylint: disable=line-too-long
        json=withdraw_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "greater_than_equal" == content["details"]["args"][0][0]["type"]
    assert "amount" in content["details"]["args"][0][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_withdraw_first_moneybox__status_422__zero_amount(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 1"
        )
    )

    withdraw_data = {
        "amount": 0,
        "description": "",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/balance/sub",  # noqa: typing  # pylint: disable=line-too-long
        json=withdraw_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "greater_than_equal" == content["details"]["args"][0][0]["type"]
    assert "amount" in content["details"]["args"][0][0]["loc"]


async def test_endpoint_withdraw_first_moneybox__status_405__balance_negative(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 1"
        )
    )

    withdraw_data = {
        "amount": 101,
        "description": "",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/balance/sub",  # noqa: typing  # pylint: disable=line-too-long
        json=withdraw_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_second_to_third__status_204(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
        name="Test Box 2",
    )
    third_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
        name="Test Box 3",
    )

    transfer_data = {
        "amount": 500,
        "toMoneyboxId": third_moneybox_id,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/balance/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_second_to_third__status_204__missing_description_field(  # noqa: E501  # pylint: disable=line-too-long
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
        name="Test Box 2",
    )
    third_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
        name="Test Box 3",
    )

    transfer_data = {
        "amount": 500,
        "toMoneyboxId": third_moneybox_id,
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/balance/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_seconds_to_third__status_422__missing_amount_field(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
        name="Test Box 2",
    )
    third_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
        name="Test Box 3",
    )

    transfer_data = {
        "toMoneyboxId": third_moneybox_id,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/balance/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "missing" == content["details"]["args"][0][0]["type"]
    assert "amount" in content["details"]["args"][0][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_second_to_third__status_422__missing_to_moneybox_id_field(  # noqa: E501  # pylint: disable=line-too-long
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
        name="Test Box 2",
    )

    transfer_data = {
        "amount": 500,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/balance/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "missing" == content["details"]["args"][0][0]["type"]
    assert "toMoneyboxId" in content["details"]["args"][0][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_second_to_third__status_422__status_422__fail_extra_field(  # noqa: E501  # pylint: disable=line-too-long
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
        name="Test Box 2",
    )

    transfer_data = {
        "amount": 500,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/balance/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "missing" == content["details"]["args"][0][0]["type"]
    assert "toMoneyboxId" in content["details"]["args"][0][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_seconds_to_third_status_422__negative_amount(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 2"
        )
    )
    third_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 3"
        )
    )

    transfer_data = {
        "amount": -500,
        "toMoneyboxId": third_moneybox_id,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/balance/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "greater_than_equal" == content["details"]["args"][0][0]["type"]
    assert "amount" in content["details"]["args"][0][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_second_to_third__status_422__zero_amount(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 2"
        )
    )
    third_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 3"
        )
    )

    transfer_data = {
        "amount": 0,
        "toMoneyboxId": third_moneybox_id,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/balance/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )
    content = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "greater_than_equal" == content["details"]["args"][0][0]["type"]
    assert "amount" in content["details"]["args"][0][0]["loc"]


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_second_to_third__status_404__to_moneybox_third_not_found(  # noqa: E501  # pylint: disable=line-too-long
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Test Box 2"
        )
    )

    # calculate, because db-call would raise NotFound Exception here, but...
    third_moneybox_id = second_moneybox_id + 1

    transfer_data = {
        "amount": 500,
        "toMoneyboxId": third_moneybox_id,
        "description": "Transfer money.",
    }

    # ...but third_moneybox not found is expected here
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/balance/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.dependency
async def test_endpoint_get_transactions_log_moneybox_second__status_200(  # noqa: E501
    default_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Moneybox 2"
        )
    )

    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/transactions",  # noqa: typing  # pylint: disable=line-too-long
    )
    content = response.json()

    expected_logs = [
        {
            "id": 2,
            "counterpartyMoneyboxName": None,
            "description": "",
            "transactionType": "direct",
            "transactionTrigger": "manually",
            "amount": 6000,
            "balance": 6000,
            "counterpartyMoneyboxId": None,
            "moneyboxId": second_moneybox_id,
        },
        {
            "id": 3,
            "counterpartyMoneyboxName": None,
            "description": "",
            "transactionType": "direct",
            "transactionTrigger": "manually",
            "amount": -500,
            "balance": 5500,
            "counterpartyMoneyboxId": None,
            "moneyboxId": second_moneybox_id,
        },
        {
            "id": 4,
            "counterpartyMoneyboxName": None,
            "description": "",
            "transactionType": "direct",
            "transactionTrigger": "manually",
            "amount": -600,
            "balance": 4900,
            "counterpartyMoneyboxId": None,
            "moneyboxId": second_moneybox_id,
        },
        {
            "id": 5,
            "counterpartyMoneyboxName": None,
            "description": "",
            "transactionType": "direct",
            "transactionTrigger": "manually",
            "amount": 5000,
            "balance": 9900,
            "counterpartyMoneyboxId": None,
            "moneyboxId": second_moneybox_id,
        },
        {
            "id": 18,
            "counterpartyMoneyboxName": None,
            "description": "",
            "transactionType": "direct",
            "transactionTrigger": "manually",
            "amount": -900,
            "balance": 9000,
            "counterpartyMoneyboxId": None,
            "moneyboxId": second_moneybox_id,
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert content["total"] == 5

    for i, expected_log in enumerate(expected_logs):
        assert equal_dict(
            dict_1=expected_log,  # type: ignore
            dict_2=content["transactionLogs"][i],
            exclude_keys=["modifiedAt", "createdAt", "id"],
        )


@pytest.mark.dependency
async def test_endpoint_get_transactions_log_moneybox_third__status_200(  # noqa: E501
    default_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Moneybox 1"
        )
    )
    third_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Moneybox 3"
        )
    )
    fourth_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Moneybox 4",
            only_active_instances=False,
        )
    )
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{third_moneybox_id}/transactions",  # noqa: typing  # pylint: disable=line-too-long
    )
    content = response.json()

    expected_logs = [
        {
            "counterpartyMoneyboxName": "Moneybox 1",
            "description": "",
            "transactionType": "direct",
            "transactionTrigger": "manually",
            "amount": 3000,
            "balance": 3000,
            "counterpartyMoneyboxId": first_moneybox_id,
            "moneyboxId": third_moneybox_id,
        },
        {
            "counterpartyMoneyboxName": None,
            "description": "",
            "transactionType": "direct",
            "transactionTrigger": "manually",
            "amount": 10000,
            "balance": 13000,
            "counterpartyMoneyboxId": None,
            "moneyboxId": third_moneybox_id,
        },
        {
            "counterpartyMoneyboxName": None,
            "description": "",
            "transactionType": "direct",
            "transactionTrigger": "manually",
            "amount": -900,
            "balance": 12100,
            "counterpartyMoneyboxId": None,
            "moneyboxId": third_moneybox_id,
        },
        {
            "counterpartyMoneyboxName": "Moneybox 4",
            "description": "",
            "transactionType": "direct",
            "transactionTrigger": "manually",
            "amount": -5000,
            "balance": 7100,
            "counterpartyMoneyboxId": fourth_moneybox_id,
            "moneyboxId": third_moneybox_id,
        },
        {
            "counterpartyMoneyboxName": None,
            "description": "",
            "transactionType": "direct",
            "transactionTrigger": "manually",
            "amount": -900,
            "balance": 6200,
            "counterpartyMoneyboxId": None,
            "moneyboxId": third_moneybox_id,
        },
        {
            "counterpartyMoneyboxName": "Moneybox 4",
            "description": "",
            "transactionType": "direct",
            "transactionTrigger": "manually",
            "amount": 8000,
            "balance": 14200,
            "counterpartyMoneyboxId": fourth_moneybox_id,
            "moneyboxId": third_moneybox_id,
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert content["total"] == 6

    for i, expected_log in enumerate(expected_logs):
        assert equal_dict(
            dict_1=expected_log,  # type: ignore
            dict_2=content["transactionLogs"][i],
            exclude_keys=["modifiedAt", "createdAt", "id"],
        )


@pytest.mark.dependency
async def test_endpoint_get_transactions_log_moneybox_fifth__status_204(  # noqa: E501
    default_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    fifth_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Moneybox 5"
        )
    )

    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{fifth_moneybox_id}/transactions",  # noqa: typing  # pylint: disable=line-too-long
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.dependency
async def test_endpoint_get_transactions_log_moneybox_fourth__status_404__deleted_and_not_found(  # noqa: E501  # pylint: disable=line-too-long
    default_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    third_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Moneybox 3"
        )
    )

    # Calculate id of moneybox 4. Fourth moneybox is deleted, db call would raise a NotFound
    fourth_moneybox_id = third_moneybox_id + 1

    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{fourth_moneybox_id}/transactions",  # noqa: typing  # pylint: disable=line-too-long
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.dependency
async def test_endpoint_get_transactions_log_moneybox_sixth__status_404__not_existing_and_not_found(  # noqa: E501  # pylint: disable=line-too-long
    default_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    fifth_moneybox_id = (
        await db_manager._get_moneybox_id_by_name(  # pylint: disable=protected-access
            name="Moneybox 5"
        )
    )

    # Calculate id of moneybox 6. moneybox six does not exist,
    #   db call would raise a NotFound
    sith_moneybox_id = fifth_moneybox_id + 1

    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{sith_moneybox_id}/transactions",  # noqa: typing  # pylint: disable=line-too-long
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
