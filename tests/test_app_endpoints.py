from httpx import AsyncClient

from src.custom_types import EndpointRouteType


async def test_app_metadata_valid(client: AsyncClient) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP}/metadata",
    )
    app_data = response.json()

    app_name = app_data["appName"]
    expected_app_name = "Savings Manager"
    assert app_name == expected_app_name

    description = app_data["appDescription"]
    assert description == (
    "Savings Manager is an intuitive app for managing your savings using "
    "virtual moneyboxes. Allocate budgets, automate savings, and set priorities "
    "to reach goals faster. The app adjusts automatically when you withdraw, "
    "ensuring your plan stays on track. Easily transfer funds between moneyboxes "
    "or make manual deposits, giving you full control over your savings journey."
    )

    ver_parts = str(app_data["appVersion"]).split(".")

    for part in ver_parts:
        assert part.isdigit()
