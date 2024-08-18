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
    app_settings_id = 1  # Assumed to be a valid ID for testing
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP_SETTINGS}/{app_settings_id}",
    )

    expected_data = {
        "id": app_settings_id,
        "created_at": "2024-08-11T13:57:17.941840+00:00",
        "modified_at": "2024-08-11T15:03:17.312860+00:00",
        "is_automated_saving_active": True,
        "savings_amount": 0,
        "overflow_moneybox_automated_savings_mode": OverflowMoneyboxAutomatedSavingsModeType.COLLECT,  # noqa: ignore  # pylint: disable=line-too-long
    }

    app_settings = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert equal_dict(
        dict_1=app_settings, dict_2=expected_data, exclude_keys=["created_at", "modified_at"]
    )


@pytest.mark.dependency(depends=["test_get_app_settings_status_200"])
async def test_get_app_settings_invalid_id(
    client: AsyncClient,
) -> None:
    """Test the get_app_settings endpoint with an invalid app_settings_id."""
    app_settings_id = 9999  # Assumed to be an invalid ID for testing
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP_SETTINGS}/{app_settings_id}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.dependency(depends=["test_get_app_settings_invalid_id"])
async def test_update_app_settings_status_200(
    client: AsyncClient,
) -> None:
    """Test the update_app_settings endpoint with valid data."""
    app_settings_id = 1  # Assumed to be a valid ID for testing
    update_data = {
        "is_automated_saving_active": False,
        "savings_amount": 50000,
    }

    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP_SETTINGS}/{app_settings_id}",
        json=update_data,
    )
    updated_app_settings = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert updated_app_settings["id"] == app_settings_id
    assert (
        updated_app_settings["is_automated_saving_active"]
        == update_data["is_automated_saving_active"]
    )
    assert updated_app_settings["savings_amount"] == update_data["savings_amount"]


@pytest.mark.dependency(depends=["test_update_app_settings_status_200"])
async def test_update_app_settings_invalid_data(client: AsyncClient) -> None:
    """Test the update_app_settings endpoint with invalid data."""
    app_settings_id = 1  # Assumed to be a valid ID for testing
    update_data = {
        "savings_amount": -1000,  # Invalid savings_amount
    }

    response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP_SETTINGS}/{app_settings_id}",
        json=update_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
