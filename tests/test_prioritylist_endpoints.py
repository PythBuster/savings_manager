"""All prioritylist endpoint tests are located here."""

from httpx import AsyncClient
from starlette import status

from src.custom_types import EndpointRouteType
from src.data_classes.requests import PrioritylistRequest
from src.db.db_manager import DBManager
from src.utils import equal_dict


async def test_get_priority_list(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    expected_priority_list = [
        {"name": "Test Box 1", "priority": 1},
        {"name": "Test Box 2", "priority": 2},
    ]

    response = await client.get(f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.PRIORITYLIST}")

    if (
        response.status_code == status.HTTP_204_NO_CONTENT
    ):  # Handle the case where no priority list is available
        assert response.json() == {}  # Expecting an empty JSON response
        return  # Exit the test early if status code is 204

    assert response.status_code == status.HTTP_200_OK
    response_priority_list = response.json()["priority_list"]

    for i, expected_priority in enumerate(expected_priority_list):
        assert equal_dict(
            dict_1=response_priority_list[i], dict_2=expected_priority, exclude_keys=["moneybox_id"]
        )


async def test_get_empty_priority_list(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.PRIORITYLIST}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_update_priority_list(  # pylint:disable=too-many-locals
    load_test_data: None,  # pylint:disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
        name="Test Box 1",
    )
    second_moneybox_id = await db_manager._get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
        name="Test Box 2",
    )

    update_priority_list = [
        {"moneybox_id": first_moneybox_id, "priority": 2},
        {"moneybox_id": second_moneybox_id, "priority": 1},
    ]

    # Attempting to update with valid priorities
    update_data = PrioritylistRequest(priority_list=update_priority_list)
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.PRIORITYLIST}",
        json=update_data.model_dump(),
    )
    assert response.status_code == status.HTTP_200_OK
    response_priority_list = response.json()["priority_list"]

    expected_priority = [
        {"moneybox_id": first_moneybox_id, "priority": 2, "name": "Test Box 1"},
        {"moneybox_id": second_moneybox_id, "priority": 1, "name": "Test Box 2"},
    ]
    expected_priority.sort(key=lambda x: x["priority"])  # type: ignore

    for i, priority in enumerate(expected_priority):
        assert equal_dict(
            dict_1=response_priority_list[i],
            dict_2=priority,
        )

    # Attempting to update with priority=0, which should be rejected
    invalid_update_priority_list = [
        {"moneybox_id": first_moneybox_id, "priority": 0},
        {"moneybox_id": second_moneybox_id, "priority": 1},
    ]
    response_invalid = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.PRIORITYLIST}",
        json=invalid_update_priority_list,
    )
    assert response_invalid.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Attempting to update the overflow moneybox with moneybox_id=1
    overflow_update_priority_list = [
        {"moneybox_id": 1, "priority": 1},  # Assuming 1 is the overflow moneybox
        {"moneybox_id": second_moneybox_id, "priority": 2},
    ]
    update_data_overflow = PrioritylistRequest(priority_list=overflow_update_priority_list)
    response_overflow = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.PRIORITYLIST}",
        json=update_data_overflow.model_dump(),
    )
    assert response_overflow.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
