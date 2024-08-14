from httpx import AsyncClient
from sqlalchemy.util import await_only

from src.custom_types import EndpointRouteType
from src.data_classes.requests import PrioritylistRequest
from src.db.db_manager import DBManager
from src.utils import equal_dict


async def test_get_priority_list(
        load_test_data: None,  # pylint: disable=unused-argument
        client: AsyncClient,
)->None:
    expected_priority_list = [
        {"name": "Test Box 1", "priority": 1},
        {"name": "Test Box 2", "priority": 2},
    ]

    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.PRIORITYLIST}"
    )
    assert response.status_code == 200
    response_priority_list = response.json()["priority_list"]
    del response_priority_list[0]  # remove overflow moneybox

    for i, expected_priority in enumerate(expected_priority_list):
        assert equal_dict(
            dict_1=response_priority_list[i],
            dict_2=expected_priority,
            exclude_keys=["moneybox_id"]
        )


async def test_update_priority_list(
        load_test_data: None,
        client: AsyncClient,
        db_manager: DBManager,
):
    """Test für den Endpunkt zum Aktualisieren der Prioritätenliste."""
    first_moneybox_id = await db_manager._get_moneybox_id_by_name(
        name="Test Box 1",
    )
    second_moneybox_id = await db_manager._get_moneybox_id_by_name(
        name="Test Box 2",
    )

    update_priority_list = [
        {"moneybox_id": first_moneybox_id, "priority": 2},
        {"moneybox_id": second_moneybox_id, "priority": 1},
    ]

    update_data = PrioritylistRequest(priority_list=update_priority_list)
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.PRIORITYLIST}",
        json=update_data.model_dump()
    )
    assert response.status_code == 200
    response_priority_list = response.json()["priority_list"]
    del response_priority_list[0]  # remove overflow moneybox

    expected_priority = [
        {"moneybox_id": first_moneybox_id, "priority": 2, "name": "Test Box 1"},
        {"moneybox_id": second_moneybox_id, "priority": 1, "name": "Test Box 2"},
    ]

    for i, expected_priority in enumerate(expected_priority):
        assert equal_dict(
            dict_1=response_priority_list[i],
            dict_2=expected_priority,
        )
