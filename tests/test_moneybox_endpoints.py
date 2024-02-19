"""All moneybox endpoint tests are located here."""

import pytest
from httpx import AsyncClient

from src.custom_types import EndpointRouteType


@pytest.mark.dependency(depends=["tests/test_db_manager.py::test_delete_moneybox"], scope="session")
async def test_endpoint_get_moneybox(client: AsyncClient) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOX}/1",
    )
    expected_moneybox_data = {"name": "Test Box 1", "id": 1, "balance": 0}

    assert response.status_code == 200
    assert response.json() == expected_moneybox_data
