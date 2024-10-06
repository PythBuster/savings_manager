"""All app endpoints test are located here."""

import asyncio
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
    original_main = CommandLine.main

    with patch.object(CommandLine, "main") as mock_main:

        def patched_main(cmd_line, args) -> None:  # type: ignore
            args = ["-x", "ENVIRONMENT=test"] + args
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
            args = ["-x", "ENVIRONMENT=test"] + args
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

    assert response.status_code == status.HTTP_200_OK

    dump_file_path = (Path(__file__).parent / "temp" / "dump.sql").resolve()

    with open(dump_file_path, "rb") as file:
        sql_dump_bytes = io.BytesIO(file.read())

    sql_dump_value = sql_dump_bytes.getvalue()
    assert len(response.content) == len(sql_dump_value)

    # Remove HEADER, because datetime is embedded within first ~50 bytes
    # see: https://github.com/postgres/postgres/blob/d35e29387870fecfdb52ffd4c93c651f0c7c1b43/src/bin/pg_dump/pg_backup_archiver.c#L3953-L3980  # noqa: ignore  # pylint: disable=line-too-long
    hash1 = hash(response.content[50:])
    hash2 = hash(sql_dump_value[50:])
    assert hash1 == hash2

    assert 'filename="export_data_savings_manager_' in response.headers["Content-Disposition"]
    assert response.headers["content-type"] == "application/octet-stream"

    await asyncio.sleep(1)


@pytest.mark.order(after="tests/test_db_manager.py::test_import_sql_dump")
async def test_app_import_valid(client: AsyncClient) -> None:
    original_main = CommandLine.main

    with patch.object(CommandLine, "main") as mock_main:

        def patched_main(cmd_line, args) -> None:  # type: ignore
            args = ["-x", "ENVIRONMENT=test"] + args
            original_main(cmd_line, args)

        mock_main.side_effect = patched_main

        dump_file_path = (Path(__file__).parent / "temp" / "dump.sql").resolve()

        with open(dump_file_path, "rb") as file:
            sql_dump_bytes = io.BytesIO(file.read())

        # Prepare the file as part of the request (mimicking an upload)
        files = {"file": ("dump.sql", sql_dump_bytes, "application/sql")}

        response = await client.post(
            f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP}/import",
            files=files,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.order(after="tests/test_db_manager.py::test_add_user_success")
async def test_app_login_fail__invalid_password(
    client: AsyncClient,
) -> None:
    login_post_data = {
        "userName": "hannelore.von.buxtehude@eine-email-adresse-halt.de",
        "userPassword": "incorrect-password",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP}/login",
        json=login_post_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    content = response.json()
    assert content["message"] == "Username or password incorrect."

@pytest.mark.order(after="test_app_login_fail__invalid_password")
async def test_app_login_success(
    client: AsyncClient,
) -> None:
    login_post_data = {
        "userName": "hannelore.von.buxtehude@eine-email-adresse-halt.de",
        "userPassword": "sicher-ist-nichts",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP}/login",
        json=login_post_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.headers.raw) == 3
    assert response.headers.raw[-1][0] == b"set-cookie"
    assert b"savings_manager=" in response.headers.raw[-1][1]
    assert len(response.headers.raw[-1][1]) > len(b"savings_manager=.......")

    user = response.json()
    assert user is not None
    assert user["userName"] == login_post_data["userName"]


@pytest.mark.order(after="test_app_login_success")
async def test_app_logout_success(
    client: AsyncClient,
) -> None:
    response = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP}/logout",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(response.headers.raw) == 1
    assert response.headers.raw[-1][0] == b"set-cookie"
    assert b'savings_manager=""' in response.headers.raw[-1][1]


@pytest.mark.order(after="test_app_logout_success")
async def test_app_logout_fail(
    client: AsyncClient,
) -> None:
    response = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP}/logout",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.order(after="test_app_logout_fail")
async def test_app_login_fail(
    client: AsyncClient,
) -> None:
    login_post_data = {
        "userName": "not-hannelore",
        "userPassword": "sicher-ist-nichts",
    }

    response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP}/login",
        json=login_post_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

