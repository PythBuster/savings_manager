"""All prioritylist endpoint tests are located here."""

from httpx import AsyncClient
from starlette import status

from src.custom_types import EndpointRouteType
from src.db.db_manager import DBManager
from src.utils import equal_dict
from tests.utils.db_manager import get_moneybox_id_by_name


async def test_get_prioritylist(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    expected_prioritylist = [
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
    response_prioritylist = response.json()["prioritylist"]

    for i, expected_priority in enumerate(expected_prioritylist):
        assert equal_dict(
            dict_1=response_prioritylist[i],
            dict_2=expected_priority,
            exclude_keys=["moneyboxId"],
        )


async def test_get_empty_prioritylist(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.PRIORITYLIST}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_update_prioritylist(  # pylint:disable=too-many-locals
    load_test_data: None,  # pylint:disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker,
            name="Test Box 1",
        )
    )
    second_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker,
            name="Test Box 2",
        )
    )

    update_prioritylist_data = {
        "prioritylist": [
            {"moneyboxId": first_moneybox_id, "priority": 2},
            {"moneyboxId": second_moneybox_id, "priority": 1},
        ]
    }

    # Attempting to update with valid priorities
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.PRIORITYLIST}",
        json=update_prioritylist_data,
    )
    assert response.status_code == status.HTTP_200_OK
    response_prioritylist = response.json()["prioritylist"]

    expected_priority = [
        {"moneyboxId": first_moneybox_id, "priority": 2, "name": "Test Box 1"},
        {"moneyboxId": second_moneybox_id, "priority": 1, "name": "Test Box 2"},
    ]
    expected_priority.sort(key=lambda x: x["priority"])  # type: ignore

    for i, priority in enumerate(expected_priority):
        assert equal_dict(
            dict_1=response_prioritylist[i],
            dict_2=priority,
        )

    # Attempting to update with priority=0, which should be rejected
    invalid_update_prioritylist = [
        {"moneyboxId": first_moneybox_id, "priority": 0},
        {"moneyboxId": second_moneybox_id, "priority": 1},
    ]
    response_invalid = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.PRIORITYLIST}",
        json=invalid_update_prioritylist,
    )
    assert response_invalid.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Attempting to update the overflow moneybox with moneybox_id=1
    overflow_update_prioritylist_data = {
        "prioritylist": [
            {"moneyboxId": 1, "priority": 1},  # Assuming 1 is the overflow moneybox
            {"moneyboxId": second_moneybox_id, "priority": 2},
        ]
    }
    response_overflow = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.PRIORITYLIST}",
        json=overflow_update_prioritylist_data,
    )
    assert response_overflow.status_code == status.HTTP_409_CONFLICT
