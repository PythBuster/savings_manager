"""All moneybox endpoint tests are located here."""

import asyncio
from datetime import datetime
from typing import Any

import httpx
import pytest
from httpx import AsyncClient
from starlette import status

from src.custom_types import EndpointRouteType
from src.db.db_manager import DBManager
from src.utils import equal_dict
from tests.utils.db_manager import get_moneybox_id_by_name


@pytest.mark.dependency(
    depends=["tests/test_db_manager.py::test_update_app_settings_valid"],
    scope="session",
)
@pytest.mark.asyncio
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
                "description": "",
            },
            {
                "name": "Test Box 1",
                "id": 2,
                "balance": 0,
                "savingsAmount": 0,
                "savingsTarget": None,
                "priority": 1,  # pylint: disable=duplicate-code
                "description": "",
            },
            {
                "name": "Test Box 2",
                "id": 3,
                "balance": 0,
                "savingsAmount": 0,
                "savingsTarget": None,
                "priority": 2,
                "description": "",
            },
            {
                "name": "Test Box 3",
                "id": 4,
                "balance": 0,
                "savingsAmount": 0,
                "savingsTarget": None,
                "priority": 3,
                "description": "",
            },
            {
                "name": "Test Box 4",
                "id": 5,
                "balance": 0,
                "savingsAmount": 0,
                "savingsTarget": None,
                "priority": 4,
                "description": "",
            },
            {
                "name": "Test Box 5",
                "id": 6,
                "balance": 0,
                "savingsAmount": 0,
                "savingsTarget": None,
                "priority": 5,
                "description": "",
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
async def test_endpoint_get_moneyboxes__status_200__only_overflow_moneybox(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )

    # there should be always at least one moneybox: the overflow moneybox
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.dependency
async def test_endpoint_get_moneyboxes__fail__missing_overflow_moneybox(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response: httpx.Response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content: dict[str, Any] = response.json()
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"]) == 1
    assert (
        content["details"]["errors"][0]["message"]
        == "List should have at least 1 item after validation, not 0"
    )
    assert content["details"]["errors"][0]["type"] == "too_short"


@pytest.mark.dependency
async def test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_collect(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )

    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["total"] == 5

    expected_result: list[dict[str, int | None]] = [
        {"moneyboxId": 16, "reachedInMonths": 0},
        {"moneyboxId": 13, "reachedInMonths": 5},
        {"moneyboxId": 14, "reachedInMonths": None},
        {"moneyboxId": 15, "reachedInMonths": 15},
        {"moneyboxId": 17, "reachedInMonths": None},
    ]

    for dict_1, dict_2 in zip(content["moneyboxForecasts"], expected_result):
        assert equal_dict(dict_1, dict_2, exclude_keys=["monthlyDistributions"])

    assert len(content["moneyboxForecasts"][0]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][1]["monthlyDistributions"]) == 5
    assert len(content["moneyboxForecasts"][2]["monthlyDistributions"]) == 11
    assert len(content["moneyboxForecasts"][3]["monthlyDistributions"]) == 10
    assert len(content["moneyboxForecasts"][4]["monthlyDistributions"]) == 2


@pytest.mark.dependency
async def test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_add(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )

    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["total"] == 5

    expected_result: list[dict[str, int | None]] = [
        {"moneyboxId": 22, "reachedInMonths": 0},
        {"moneyboxId": 19, "reachedInMonths": 5},
        {"moneyboxId": 20, "reachedInMonths": None},
        {"moneyboxId": 21, "reachedInMonths": 15},
        {"moneyboxId": 23, "reachedInMonths": None},
    ]

    for dict_1, dict_2 in zip(content["moneyboxForecasts"], expected_result):
        assert equal_dict(dict_1, dict_2, exclude_keys=["monthlyDistributions"])

    assert len(content["moneyboxForecasts"][0]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][1]["monthlyDistributions"]) == 5
    assert len(content["moneyboxForecasts"][2]["monthlyDistributions"]) == 11
    assert len(content["moneyboxForecasts"][3]["monthlyDistributions"]) == 10
    assert len(content["moneyboxForecasts"][4]["monthlyDistributions"]) == 2


@pytest.mark.dependency
async def test_savings_forecast__status_200__with_savings_amount__overflow_balance_0__mode_fill(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )

    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["total"] == 5

    expected_result: list[dict[str, int | None]] = [
        {"moneyboxId": 28, "reachedInMonths": 0},
        {"moneyboxId": 25, "reachedInMonths": 5},
        {"moneyboxId": 26, "reachedInMonths": None},
        {"moneyboxId": 27, "reachedInMonths": 15},
        {"moneyboxId": 29, "reachedInMonths": None},
    ]

    for dict_1, dict_2 in zip(content["moneyboxForecasts"], expected_result):
        assert equal_dict(dict_1, dict_2, exclude_keys=["monthlyDistributions"])

    assert len(content["moneyboxForecasts"][0]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][1]["monthlyDistributions"]) == 5
    assert len(content["moneyboxForecasts"][2]["monthlyDistributions"]) == 11
    assert len(content["moneyboxForecasts"][3]["monthlyDistributions"]) == 10
    assert len(content["moneyboxForecasts"][4]["monthlyDistributions"]) == 2


@pytest.mark.dependency
async def test_savings_forecast__status_204__no_data(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.dependency
async def test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_collect(  # noqa: E501  # pylint: disable=line-too-long
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )
    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["total"] == 4

    expected_result: list[dict[str, int | None]] = [
        {"moneyboxId": 35, "reachedInMonths": 0},
        {"moneyboxId": 32, "reachedInMonths": None},
        {"moneyboxId": 33, "reachedInMonths": None},
        {"moneyboxId": 34, "reachedInMonths": None},
    ]

    for dict_1, dict_2 in zip(content["moneyboxForecasts"], expected_result):
        assert equal_dict(dict_1, dict_2, exclude_keys=["monthlyDistributions"])

    assert len(content["moneyboxForecasts"][0]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][1]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][2]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][3]["monthlyDistributions"]) == 0


@pytest.mark.dependency
async def test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_add(  # noqa: E501  # pylint: disable=line-too-long
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )
    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["total"] == 4

    expected_result: list[dict[str, int | None]] = [
        {"moneyboxId": 40, "reachedInMonths": 0},
        {"moneyboxId": 37, "reachedInMonths": None},
        {"moneyboxId": 38, "reachedInMonths": None},
        {"moneyboxId": 39, "reachedInMonths": None},
    ]

    for dict_1, dict_2 in zip(content["moneyboxForecasts"], expected_result):
        assert equal_dict(dict_1, dict_2, exclude_keys=["monthlyDistributions"])

    assert len(content["moneyboxForecasts"][0]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][1]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][2]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][3]["monthlyDistributions"]) == 0


@pytest.mark.dependency
async def test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_0__mode_fill(  # noqa: E501  # pylint: disable=line-too-long
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )
    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["total"] == 4

    expected_result: list[dict[str, int | None]] = [
        {"moneyboxId": 45, "reachedInMonths": 0},
        {"moneyboxId": 42, "reachedInMonths": None},
        {"moneyboxId": 43, "reachedInMonths": None},
        {"moneyboxId": 44, "reachedInMonths": None},
    ]

    for dict_1, dict_2 in zip(content["moneyboxForecasts"], expected_result):
        assert equal_dict(dict_1, dict_2, exclude_keys=["monthlyDistributions"])

    assert len(content["moneyboxForecasts"][0]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][1]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][2]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][3]["monthlyDistributions"]) == 0


@pytest.mark.dependency
async def test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_collect(  # noqa: E501  # pylint: disable=line-too-long
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )
    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["total"] == 4

    expected_result: list[dict[str, int | None]] = [
        {"moneyboxId": 50, "reachedInMonths": 0},
        {"moneyboxId": 47, "reachedInMonths": None},
        {"moneyboxId": 48, "reachedInMonths": None},
        {"moneyboxId": 49, "reachedInMonths": None},
    ]

    for dict_1, dict_2 in zip(content["moneyboxForecasts"], expected_result):
        assert equal_dict(dict_1, dict_2, exclude_keys=["monthlyDistributions"])

    assert len(content["moneyboxForecasts"][0]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][1]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][2]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][3]["monthlyDistributions"]) == 0


@pytest.mark.dependency
async def test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_add(  # noqa: E501  # pylint: disable=line-too-long
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )
    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["total"] == 5

    expected_result: list[dict[str, int | None]] = [
        {"moneyboxId": 55, "reachedInMonths": 0},
        {"moneyboxId": 52, "reachedInMonths": 1},
        {"moneyboxId": 53, "reachedInMonths": None},
        {"moneyboxId": 54, "reachedInMonths": 1},
        {"moneyboxId": 56, "reachedInMonths": None},
    ]

    for dict_1, dict_2 in zip(content["moneyboxForecasts"], expected_result):
        assert equal_dict(dict_1, dict_2, exclude_keys=["monthlyDistributions"])

    assert len(content["moneyboxForecasts"][0]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][1]["monthlyDistributions"]) == 1
    assert len(content["moneyboxForecasts"][2]["monthlyDistributions"]) == 1
    assert len(content["moneyboxForecasts"][3]["monthlyDistributions"]) == 1
    assert len(content["moneyboxForecasts"][4]["monthlyDistributions"]) == 0


@pytest.mark.dependency
async def test_savings_forecast__status_200__savings_amount_0__overflow_moneybox_250__mode_fill(  # noqa: E501  # pylint: disable=line-too-long
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )
    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["total"] == 5

    expected_result: list[dict[str, int | None]] = [
        {"moneyboxId": 61, "reachedInMonths": 0},
        {"moneyboxId": 58, "reachedInMonths": 1},
        {"moneyboxId": 60, "reachedInMonths": 1},
        {"moneyboxId": 59, "reachedInMonths": None},
        {"moneyboxId": 62, "reachedInMonths": None},
    ]

    for dict_1, dict_2 in zip(content["moneyboxForecasts"], expected_result):
        assert equal_dict(dict_1, dict_2, exclude_keys=["monthlyDistributions"])

    assert len(content["moneyboxForecasts"][0]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][1]["monthlyDistributions"]) == 1
    assert len(content["moneyboxForecasts"][2]["monthlyDistributions"]) == 1
    assert len(content["moneyboxForecasts"][3]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][4]["monthlyDistributions"]) == 0


@pytest.mark.dependency
async def test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_collect(  # noqa: E501  # pylint: disable=line-too-long
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )
    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["total"] == 5

    expected_result: list[dict[str, int | None]] = [
        {"moneyboxId": 67, "reachedInMonths": 0},
        {"moneyboxId": 64, "reachedInMonths": 5},
        {"moneyboxId": 65, "reachedInMonths": None},
        {"moneyboxId": 66, "reachedInMonths": 15},
        {"moneyboxId": 68, "reachedInMonths": None},
    ]

    for dict_1, dict_2 in zip(content["moneyboxForecasts"], expected_result):
        assert equal_dict(dict_1, dict_2, exclude_keys=["monthlyDistributions"])

    assert len(content["moneyboxForecasts"][0]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][1]["monthlyDistributions"]) == 5
    assert len(content["moneyboxForecasts"][2]["monthlyDistributions"]) == 11
    assert len(content["moneyboxForecasts"][3]["monthlyDistributions"]) == 10
    assert len(content["moneyboxForecasts"][4]["monthlyDistributions"]) == 0


@pytest.mark.dependency
async def test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_add(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )
    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["total"] == 5

    expected_result: list[dict[str, int | None]] = [
        {"moneyboxId": 73, "reachedInMonths": 0},
        {"moneyboxId": 70, "reachedInMonths": 4},
        {"moneyboxId": 71, "reachedInMonths": None},
        {"moneyboxId": 72, "reachedInMonths": 12},
        {"moneyboxId": 74, "reachedInMonths": None},
    ]

    for dict_1, dict_2 in zip(content["moneyboxForecasts"], expected_result):
        assert equal_dict(dict_1, dict_2, exclude_keys=["monthlyDistributions"])

    assert len(content["moneyboxForecasts"][0]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][1]["monthlyDistributions"]) == 4
    assert len(content["moneyboxForecasts"][2]["monthlyDistributions"]) == 10
    assert len(content["moneyboxForecasts"][3]["monthlyDistributions"]) == 9
    assert len(content["moneyboxForecasts"][4]["monthlyDistributions"]) == 0


@pytest.mark.dependency
async def test_savings_forecast__status_200__with_savings_amount__overflow_balance_3000__mode_fill(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}/savings_forecast",
    )
    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["total"] == 5

    expected_result: list[dict[str, int | None]] = [
        {"moneyboxId": 79, "reachedInMonths": 0},
        {"moneyboxId": 76, "reachedInMonths": 4},
        {"moneyboxId": 77, "reachedInMonths": None},
        {"moneyboxId": 78, "reachedInMonths": 10},
        {"moneyboxId": 80, "reachedInMonths": 11},
    ]

    for dict_1, dict_2 in zip(content["moneyboxForecasts"], expected_result):
        assert equal_dict(dict_1, dict_2, exclude_keys=["monthlyDistributions"])

    assert len(content["moneyboxForecasts"][0]["monthlyDistributions"]) == 0
    assert len(content["moneyboxForecasts"][1]["monthlyDistributions"]) == 4
    assert len(content["moneyboxForecasts"][2]["monthlyDistributions"]) == 9
    assert len(content["moneyboxForecasts"][3]["monthlyDistributions"]) == 6
    assert len(content["moneyboxForecasts"][4]["monthlyDistributions"]) == 1


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
        "description": "",
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
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_get_moneybox__second_moneybox__status_200_existing__with_balance_100(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    moneybox_id = await get_moneybox_id_by_name(  # noqa: ignore  # pylint:disable=protected-access, line-too-long
        async_session=db_manager.async_sessionmaker,
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
        "description": "",
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
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}",
        json=moneybox_data,
    )
    moneybox = response.json()

    expected_moneybox_data = {
        "name": "Test Box Endpoint Add 1",
        "id": moneybox["id"],
        "balance": 0,
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 1,
        "description": "",
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
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}",
        json=moneybox_data_1,
    )
    moneybox_1 = response_1.json()

    expected_moneybox_data_1 = {
        "name": "Test Box Endpoint Add 1",
        "id": moneybox_1["id"],
        "balance": 0,
        "savingsAmount": 0,
        "savingsTarget": None,
        "priority": 1,
        "description": "",
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
        "description": "",
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
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.dependency
async def test_endpoint_update_overflow_moneybox__fail_409__modification_not_allowed(
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
    assert response_1.status_code == status.HTTP_409_CONFLICT
    assert content["message"] == "It is not allowed to modify the Overflow Moneybox!"


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
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {
        "details": {
            "id": moneybox_id,
        },
        "message": "It is not allowed to delete the Overflow Moneybox!",
    }


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_422__invalid_priority_0(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
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

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "greater_than_equal"
    assert (
        content["details"]["errors"][0]["message"] == "Input should be greater than or equal to 1"
    )
    assert content["details"]["errors"][0]["field"] == "priority"


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_422__name_none(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    moneybox_data = {
        "name": None,
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "string_type"
    assert content["details"]["errors"][0]["message"] == "Input should be a valid string"
    assert content["details"]["errors"][0]["field"] == "name"


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_422__name_empty(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    moneybox_data = {
        "name": "",
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "string_too_short"
    assert content["details"]["errors"][0]["message"] == "String should have at least 1 character"
    assert content["details"]["errors"][0]["field"] == "name"


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_422__name_not_string_type(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    # int as name
    moneybox_data: dict[str, Any] = {"name": 42}
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "string_type"
    assert content["details"]["errors"][0]["message"] == "Input should be a valid string"
    assert content["details"]["errors"][0]["field"] == "name"

    # float as name
    moneybox_data = {"name": 1.23}
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "string_type"
    assert content["details"]["errors"][0]["message"] == "Input should be a valid string"
    assert content["details"]["errors"][0]["field"] == "name"


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
        "description": "",
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
        "description": "",
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
        "description": "",
    }

    assert response_3.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=moneybox_3,
        dict_2=expected_moneybox_data_3,
        exclude_keys=["createdAt", "modifiedAt"],
    )


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_200__description_change(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    moneybox_data = {
        "description": "New Description",
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["description"] == "New Description"
    assert content["id"] == first_moneybox_id


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_409__description_none(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    moneybox_data = {
        "description": None,
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    content = response.json()
    assert len(content["details"]) == 2
    assert content["message"] == "Failed to update moneybox."
    assert content["details"]["description"] is None


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_422__description_not_string_type(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    # int as name
    moneybox_data: dict[str, Any] = {"description": 42}
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "string_type"
    assert content["details"]["errors"][0]["message"] == "Input should be a valid string"
    assert content["details"]["errors"][0]["field"] == "description"

    # float as name
    moneybox_data = {"description": 1.23}
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "string_type"
    assert content["details"]["errors"][0]["message"] == "Input should be a valid string"
    assert content["details"]["errors"][0]["field"] == "description"


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_200__savings_amount_change(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    moneybox_data = {
        "savingsAmount": 123,
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["savingsAmount"] == 123
    assert content["id"] == first_moneybox_id


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_422__savings_amount_none(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    moneybox_data = {
        "savingsAmount": None,
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "int_type"
    assert content["details"]["errors"][0]["message"] == "Input should be a valid integer"
    assert content["details"]["errors"][0]["field"] == "savingsAmount"


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_422__savings_amount_non_int_type(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    # float type
    moneybox_data: dict[str, Any] = {
        "savingsAmount": 12.3,
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "int_type"
    assert content["details"]["errors"][0]["message"] == "Input should be a valid integer"
    assert content["details"]["errors"][0]["field"] == "savingsAmount"

    # string type
    moneybox_data = {
        "savingsAmount": "12",
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "int_type"
    assert content["details"]["errors"][0]["message"] == "Input should be a valid integer"
    assert content["details"]["errors"][0]["field"] == "savingsAmount"


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_422__savings_amount_negative(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    # float type
    moneybox_data = {
        "savingsAmount": -1,
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "greater_than_equal"
    assert (
        content["details"]["errors"][0]["message"] == "Input should be greater than or equal to 0"
    )
    assert content["details"]["errors"][0]["field"] == "savingsAmount"


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_200__savings_target_none_change(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    moneybox_data = {
        "savingsTarget": None,
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["savingsTarget"] is None
    assert content["id"] == first_moneybox_id


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_200__savings_target_value_change(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    moneybox_data = {
        "savingsTarget": 567,
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content["savingsTarget"] == 567
    assert content["id"] == first_moneybox_id


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_422_savings_target_non_int_type(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    # float type
    moneybox_data: dict[str, Any] = {
        "savingsTarget": 123.4,
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()

    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "int_type"
    assert content["details"]["errors"][0]["message"] == "Input should be a valid integer"
    assert content["details"]["errors"][0]["field"] == "savingsTarget"

    # string type
    moneybox_data = {
        "savingsTarget": "42",
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()

    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "int_type"
    assert content["details"]["errors"][0]["message"] == "Input should be a valid integer"
    assert content["details"]["errors"][0]["field"] == "savingsTarget"


@pytest.mark.dependency
async def test_endpoint_update_moneybox__status_422_savings_target_negative(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    # float type
    moneybox_data = {
        "savingsTarget": -1,
    }
    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()

    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "greater_than_equal"
    assert (
        content["details"]["errors"][0]["message"] == "Input should be greater than or equal to 0"
    )
    assert content["details"]["errors"][0]["field"] == "savingsTarget"


@pytest.mark.dependency
async def test_endpoint_first_moneybox__modified_at_checks(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
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
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
    )

    # balance not allowed in update data
    moneybox_data_1 = {"name": "Updated Test Box 1", "balance": 200}

    response_1 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data_1,
    )

    assert response_1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # unknown extra field not allowed in update data
    moneybox_data_2 = {"name": "Updated Test Box 1", "unknwon_field": "xyz"}

    response_2 = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}",
        json=moneybox_data_2,
    )

    assert response_2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.dependency
async def test_endpoint_delete_second_moneybox__status_204(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint:disable=protected-access
            async_session=db_manager.async_sessionmaker, name="Test Box 1"
        )
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
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_deposit_first_moneybox__status_200(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 1"
    )

    deposit_data = {
        "amount": 100,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/deposit",  # noqa: typing  # pylint: disable=line-too-long
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
        "description": "",
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
    first_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 1"
    )
    deposit_data = {
        "amount": 100,
        "description": "Bonus.",
        "extra_field": "wow",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/deposit",  # noqa: typing  # pylint: disable=line-too-long
        json=deposit_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.dependency
async def test_endpoint_deposit_first_moneybox__status_422__missing_required_amount_field(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 1"
    )

    deposit_data = {
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/deposit",  # noqa: typing  # pylint: disable=line-too-long
        json=deposit_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "missing"
    assert content["details"]["errors"][0]["message"] == "Field required"
    assert content["details"]["errors"][0]["field"] == "amount"


@pytest.mark.dependency
async def test_endpoint_deposit_first_moneybox__status_422__negative_amount(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 1"
    )

    deposit_data = {
        "amount": -100,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/deposit",  # noqa: typing  # pylint: disable=line-too-long
        json=deposit_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "greater_than_equal"
    assert (
        content["details"]["errors"][0]["message"] == "Input should be greater than or equal to 1"
    )
    assert content["details"]["errors"][0]["field"] == "amount"


@pytest.mark.dependency
async def test_endpoint_deposit_first_moneybox__status_422__zero_amount(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 1"
    )

    deposit_data = {
        "amount": 0,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/deposit",  # noqa: typing  # pylint: disable=line-too-long
        json=deposit_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "greater_than_equal"
    assert (
        content["details"]["errors"][0]["message"] == "Input should be greater than or equal to 1"
    )
    assert content["details"]["errors"][0]["field"] == "amount"


@pytest.mark.dependency
async def test_endpoint_withdraw_first_moneybox__status_200(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 1"
    )

    withdraw_data = {
        "amount": 99,
        "description": "Bonus.",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/withdraw",  # noqa: typing  # pylint: disable=line-too-long
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
        "description": "",
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
    first_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 1"
    )

    withdraw_data = {
        "amount": 100,
        "description": "",
        "extra_field": "wow",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/withdraw",  # noqa: typing  # pylint: disable=line-too-long
        json=withdraw_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.dependency
async def test_endpoint_withdraw_first_moneybox__status_422__missing_required_amount_field(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 1"
    )

    withdraw_data = {
        "description": "",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/withdraw",  # noqa: typing  # pylint: disable=line-too-long
        json=withdraw_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "missing"
    assert content["details"]["errors"][0]["message"] == "Field required"
    assert content["details"]["errors"][0]["field"] == "amount"


@pytest.mark.dependency
async def test_endpoint_withdraw_first_moneybox__status_422__negative_amount(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 1"
    )

    withdraw_data = {
        "amount": -100,
        "description": "",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/withdraw",  # noqa: typing  # pylint: disable=line-too-long
        json=withdraw_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "greater_than_equal"
    assert (
        content["details"]["errors"][0]["message"] == "Input should be greater than or equal to 1"
    )
    assert content["details"]["errors"][0]["field"] == "amount"


@pytest.mark.dependency
async def test_endpoint_withdraw_first_moneybox__status_422__zero_amount(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 1"
    )

    withdraw_data = {
        "amount": 0,
        "description": "",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/withdraw",  # noqa: typing  # pylint: disable=line-too-long
        json=withdraw_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "greater_than_equal"
    assert (
        content["details"]["errors"][0]["message"] == "Input should be greater than or equal to 1"
    )
    assert content["details"]["errors"][0]["field"] == "amount"


async def test_endpoint_withdraw_first_moneybox__status_409__balance_negative(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    first_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 1"
    )

    withdraw_data = {
        "amount": 101,
        "description": "",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{first_moneybox_id}/withdraw",  # noqa: typing  # pylint: disable=line-too-long
        json=withdraw_data,
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_second_to_third__status_204(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
            async_session=db_manager.async_sessionmaker,
            name="Test Box 2",
        )
    )
    third_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
            async_session=db_manager.async_sessionmaker,
            name="Test Box 3",
        )
    )

    transfer_data = {
        "amount": 500,
        "toMoneyboxId": third_moneybox_id,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_second_to_third__status_204__missing_description_field(  # noqa: E501  # pylint: disable=line-too-long
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
            async_session=db_manager.async_sessionmaker,
            name="Test Box 2",
        )
    )
    third_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
            async_session=db_manager.async_sessionmaker,
            name="Test Box 3",
        )
    )

    transfer_data = {
        "amount": 500,
        "toMoneyboxId": third_moneybox_id,
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_seconds_to_third__status_422__missing_amount_field(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
            async_session=db_manager.async_sessionmaker,
            name="Test Box 2",
        )
    )
    third_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
            async_session=db_manager.async_sessionmaker,
            name="Test Box 3",
        )
    )

    transfer_data = {
        "toMoneyboxId": third_moneybox_id,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "missing"
    assert content["details"]["errors"][0]["message"] == "Field required"
    assert content["details"]["errors"][0]["field"] == "amount"


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_second_to_third__status_422__missing_to_moneybox_id_field(  # noqa: E501  # pylint: disable=line-too-long
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
            async_session=db_manager.async_sessionmaker,
            name="Test Box 2",
        )
    )

    transfer_data = {
        "amount": 500,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "missing"
    assert content["details"]["errors"][0]["message"] == "Field required"
    assert content["details"]["errors"][0]["field"] == "toMoneyboxId"


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_second_to_third__status_422__status_422__fail_extra_field(  # noqa: E501  # pylint: disable=line-too-long
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = (
        await get_moneybox_id_by_name(  # noqa: typing  # pylint: disable=protected-access
            async_session=db_manager.async_sessionmaker,
            name="Test Box 2",
        )
    )

    transfer_data = {
        "amount": 500,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "missing"
    assert content["details"]["errors"][0]["message"] == "Field required"
    assert content["details"]["errors"][0]["field"] == "toMoneyboxId"


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_seconds_to_third_status_422__negative_amount(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 2"
    )
    third_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 3"
    )

    transfer_data = {
        "amount": -500,
        "toMoneyboxId": third_moneybox_id,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "greater_than_equal"
    assert (
        content["details"]["errors"][0]["message"] == "Input should be greater than or equal to 1"
    )
    assert content["details"]["errors"][0]["field"] == "amount"


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_second_to_third__status_422__zero_amount(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 2"
    )
    third_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 3"
    )

    transfer_data = {
        "amount": 0,
        "toMoneyboxId": third_moneybox_id,
        "description": "Transfer money.",
    }
    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    content = response.json()
    assert len(content["details"]["errors"]) == 1
    assert content["message"] == "Validation Error"
    assert len(content["details"]["errors"][0]) == 3
    assert content["details"]["errors"][0]["type"] == "greater_than_equal"
    assert (
        content["details"]["errors"][0]["message"] == "Input should be greater than or equal to 1"
    )
    assert content["details"]["errors"][0]["field"] == "amount"


@pytest.mark.dependency
async def test_endpoint_transfer_amount_moneybox_second_to_third__status_404__to_moneybox_third_not_found(  # noqa: E501  # pylint: disable=line-too-long
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Test Box 2"
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
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/transfer",  # noqa: typing  # pylint: disable=line-too-long
        json=transfer_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_get_transactions_log_moneybox_second__status_200(  # noqa: E501
    default_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    second_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Moneybox 2"
    )

    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{second_moneybox_id}/transactions",  # noqa: typing  # pylint: disable=line-too-long
    )
    content = response.json()

    expected_logs = [
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
    first_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Moneybox 1"
    )
    third_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Moneybox 3"
    )
    fourth_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker,
        name="Moneybox 4",
        only_active_instances=False,
    )
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{third_moneybox_id}/transactions",  # noqa: typing  # pylint: disable=line-too-long
    )
    content = response.json()

    expected_logs = [
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
            "balance": 12100,
            "counterpartyMoneyboxId": None,
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
            "counterpartyMoneyboxName": "Moneybox 1",
            "description": "",
            "transactionType": "direct",
            "transactionTrigger": "manually",
            "amount": 3000,
            "balance": 3000,
            "counterpartyMoneyboxId": first_moneybox_id,
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
    fifth_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Moneybox 5"
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
    third_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Moneybox 3"
    )

    # Calculate id of moneybox 4. The fourth moneybox is deleted, db call would raise a NotFound
    fourth_moneybox_id = third_moneybox_id + 1

    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{fourth_moneybox_id}/transactions",  # noqa: typing  # pylint: disable=line-too-long
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency
async def test_endpoint_get_transactions_log_moneybox_sixth__status_404__not_existing_and_not_found(  # noqa: E501  # pylint: disable=line-too-long
    default_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    fifth_moneybox_id = await get_moneybox_id_by_name(  # pylint: disable=protected-access
        async_session=db_manager.async_sessionmaker, name="Moneybox 5"
    )

    # Calculate id of moneybox 6. Moneybox six does not exist,
    #   db call would raise a NotFound
    sith_moneybox_id = fifth_moneybox_id + 1

    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/{sith_moneybox_id}/transactions",  # noqa: typing  # pylint: disable=line-too-long
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
