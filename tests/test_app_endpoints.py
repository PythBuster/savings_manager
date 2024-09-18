"""All app endpoints test are located here."""

import io
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from starlette import status

from alembic.config import CommandLine
from src.custom_types import EndpointRouteType
from src.utils import equal_dict


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


async def test_reset_app_keep_app_settings(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    # Stelle sicher, dass das Mock-Objekt keine rekursive Schleife verursacht
    original_main = CommandLine.main

    with patch.object(CommandLine, "main") as mock_main:

        def patched_main(cmd_line, args) -> None:  # type: ignore
            args = ["-x", "testing"] + args
            original_main(cmd_line, args)

        mock_main.side_effect = patched_main

        response = await client.get(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
        )
        old_moneyboxes = response.json()["moneyboxes"]

        response = await client.get(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP_SETTINGS}",
        )
        old_app_settings = response.json()

        post_data = {
            "keepAppSettings": True,
        }
        response = await client.post(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP}/reset",
            json=post_data,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = await client.get(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
        )
        moneyboxes = response.json()["moneyboxes"]
        assert len(moneyboxes) != len(old_moneyboxes)
        assert len(moneyboxes) == 1

        response = await client.get(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP_SETTINGS}",
        )
        app_settings = response.json()
        assert equal_dict(
            dict_1=old_app_settings,
            dict_2=app_settings,
            exclude_keys=["createdAt", "modifiedAt"],
        )


async def test_reset_app_delete_app_settings(
    load_test_data: None,  # pylint: disable=unused-argument
    client: AsyncClient,
) -> None:
    original_main = CommandLine.main

    with patch.object(CommandLine, "main") as mock_main:

        def patched_main(cmd_line, args) -> None:  # type: ignore
            args = ["-x", "testing"] + args
            original_main(cmd_line, args)

        mock_main.side_effect = patched_main

        response = await client.get(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
        )
        old_moneyboxes = response.json()["moneyboxes"]

        response = await client.get(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP_SETTINGS}",
        )
        old_app_settings = response.json()

        post_data = {
            "keepAppSettings": False,
        }
        response = await client.post(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP}/reset",
            json=post_data,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = await client.get(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.MONEYBOXES}",
        )
        moneyboxes = response.json()["moneyboxes"]
        assert len(moneyboxes) != len(old_moneyboxes)
        assert len(moneyboxes) == 1

        response = await client.get(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP_SETTINGS}",
        )
        app_settings = response.json()
        assert not equal_dict(
            dict_1=old_app_settings,
            dict_2=app_settings,
            exclude_keys=["createdAt", "modifiedAt"],
        )


@pytest.mark.order(after="tests/test_db_manager.py::test_export_sql_dump")
async def test_app_export_valid(client: AsyncClient) -> None:
    response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP}/export",
    )

    assert response.status_code == 200

    dump_file_path = (Path(__file__).parent / "temp" / "dump.sql").resolve()

    with open(dump_file_path, "rb") as file:
        sql_dump_bytes = io.BytesIO(file.read())

    assert hash(response.content) == hash(sql_dump_bytes.getvalue())
    assert 'filename="export_data_savings_manager_' in response.headers["Content-Disposition"]
    assert response.headers["content-type"] == "application/octet-stream"
