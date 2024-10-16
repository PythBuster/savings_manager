"""All app settings endpoint tests are located here."""

import pytest
from httpx import AsyncClient
from starlette import status

from src.custom_types import EndpointRouteType, OverflowMoneyboxAutomatedSavingsModeType
from src.utils import equal_dict


@pytest.mark.dependency
async def test_get_app_settings_status_200(
    load_test_data: None,  # pylint: disable=unused-argument)
    client: AsyncClient,
) -> None:
    """Test the get_app_settings endpoint with a valid app_settings_id."""
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP_SETTINGS}",
    )

    expected_data = {
        "createdAt": "2024-08-11T13:57:17.941840+00:00",
        "modifiedAt": "2024-08-11T15:03:17.312860+00:00",
        "sendReportsViaEmail": False,
        "userEmailAddress": None,
        "isAutomatedSavingActive": True,
        "savingsAmount": 0,
        "overflowMoneyboxAutomatedSavingsMode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
    }

    app_settings = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=app_settings,
        dict_2=expected_data,
        exclude_keys=["createdAt", "modifiedAt", "id"],
    )


@pytest.mark.dependency(depends=["test_get_app_settings_status_200"])
async def test_update_app_settings_invalid_data(client: AsyncClient) -> None:
    """Test the update_app_settings endpoint with invalid data."""
    update_data = {
        "savingsAmount": -1000,  # Invalid savings_amount
    }

    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP_SETTINGS}",
        json=update_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
