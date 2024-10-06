"""All app endpoints test are located here."""

import asyncio
import io
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from httpx import AsyncClient, Response
from starlette import status

from alembic.config import CommandLine
from src.custom_types import EndpointRouteType
from src.db.db_manager import DBManager
from src.utils import equal_dict


async def test_user_add_success(client: AsyncClient) -> None:
    user_post_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    response: Response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/register",
        json=user_post_data,
    )
    assert response.status_code == status.HTTP_200_OK

    user: dict[str, Any] = response.json()
    assert equal_dict(
        user,
        user_post_data,
        exclude_keys=["userPassword","createdAt","modifiedAt","id"],
    )

    # add second user
    user_post_data_2: dict[str, str] = {
        "userName": "another user",
        "userPassword": "my-another-password",
    }
    response_2: Response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/register",
        json=user_post_data_2,
    )
    assert response_2.status_code == status.HTTP_200_OK

    user_2: dict[str, Any] = response_2.json()
    assert equal_dict(
        user_2,
        user_post_data_2,
        exclude_keys=["userPassword", "createdAt", "modifiedAt", "id"],
    )

async def test_user_add_failed(client: AsyncClient) -> None:
    user_post_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    response: Response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/register",
        json=user_post_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    content: dict[str, Any] = response.json()
    assert content["message"] == "User already exists."


async def test_user_get_success(client: AsyncClient, db_manager: DBManager) -> None:
    user_data: dict[str, str|int] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    db_user = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    user_data["id"] = user_id

    response: Response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}",
    )
    assert response.status_code == status.HTTP_200_OK

    user: dict[str, Any] = response.json()
    assert equal_dict(
        user,
        user_data,
        exclude_keys=["userPassword","createdAt","modifiedAt"],
    )

async def test_user_get_fail__non_existing_user_id(client: AsyncClient) -> None:
    non_existing_user_id: int = 12345

    response: Response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    content: dict[str, Any] = response.json()
    assert content["message"] == "User does not exist."

async def test_user_update_password_success(client: AsyncClient, db_manager: DBManager) -> None:
    user_data: dict[str, str | int] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    db_user: dict[str, Any] = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    new_user_password: str = "<PASSWORD>"

    response: Response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}/password",
        json={"newUserPassword": new_user_password},
    )
    assert response.status_code == status.HTTP_200_OK

    # check if user passwort is changed by trying to get the user with old password
    db_user = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is None


async def test_user_update_password_fail__user_id_not_exist(client: AsyncClient) -> None:
    non_existing_user_id: int = 12345

    response: Response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}/password",
        json={"newUserPassword": "test"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content: dict[str, Any] = response.json()
    assert content["message"] == "Updating user password failed."

async def test_user_update_name_success(client: AsyncClient, db_manager: DBManager) -> None:
    user_data: dict[str, str | int] = {
        "userName": "New User",
        "userPassword": "<PASSWORD>",
    }
    db_user: dict[str, Any] = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    new_user_name = "Another Login"

    response: Response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}/name",
        json={"newUserName": new_user_name},
    )
    assert response.status_code == status.HTTP_200_OK

    # check if user passwort is changed by trying to get the user with old password
    db_user = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is None

async def test_user_update_name_fail__username_already_exist(client: AsyncClient, db_manager: DBManager) -> None:
    user_data: dict[str, str | int] = {
        "userName": "another user",
        "userPassword": "my-another-password",
    }
    db_user: dict[str, Any] = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    new_user_name = "Another Login"

    response: Response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}/name",
        json={"newUserName": new_user_name},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    content: dict[str, Any] = response.json()
    assert content["message"] == "User already exists."


async def test_user_update_name_fail__user_id_not_exist(client: AsyncClient, db_manager: DBManager) -> None:
    non_existing_user_id: int = 12345

    response: Response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}/name",
        json={"newUserName": "test"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content: dict[str, Any] = response.json()
    assert content["message"] == "Updating username failed."

async def test_user_delete_fail__user_id_not_exist(client: AsyncClient) -> None:
    non_existing_user_id: int = 12345

    response: Response = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content: dict[str, Any] = response.json()
    assert content["message"] == "User does not exist."

async def test_user_delete_success(client: AsyncClient, db_manager: DBManager) -> None:
    user_data: dict[str, str | int] = {
        "userName": "Another Login",
        "userPassword": "<PASSWORD>",
    }
    db_user: dict[str, Any] = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]

    response: Response = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
