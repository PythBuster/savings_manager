"""All app endpoints test are located here."""

from typing import Any

from httpx import AsyncClient, Response
from starlette import status

from src.custom_types import EndpointRouteType, UserRoleType
from src.db.db_manager import DBManager
from src.utils import equal_dict


async def test_user_add_as_admin__success(admin_role_authed_client: AsyncClient) -> None:
    user_post_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    response: Response = await admin_role_authed_client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}",
        json=user_post_data,
    )
    assert response.status_code == status.HTTP_200_OK

    user: dict[str, Any] = response.json()
    assert equal_dict(
        user,
        user_post_data | {"role": UserRoleType.USER},
        exclude_keys=["userPassword", "createdAt", "modifiedAt", "id"],
    )

    # add second user
    user_post_data_2: dict[str, str] = {
        "userName": "another user",
        "userPassword": "my-another-password",
    }
    response_2: Response = await admin_role_authed_client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}",
        json=user_post_data_2,
    )
    assert response_2.status_code == status.HTTP_200_OK

    user_2: dict[str, Any] = response_2.json()
    assert equal_dict(
        user_2,
        user_post_data_2 | {"role": UserRoleType.USER},
        exclude_keys=["userPassword", "createdAt", "modifiedAt", "id"],
    )


async def test_user_add_as_user__fail__403(user_role_authed_client: AsyncClient) -> None:
    user_post_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    response: Response = await user_role_authed_client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}",
        json=user_post_data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # add second user
    user_post_data_2: dict[str, str] = {
        "userName": "another user",
        "userPassword": "my-another-password",
    }
    response_2: Response = await user_role_authed_client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}",
        json=user_post_data_2,
    )
    assert response_2.status_code == status.HTTP_403_FORBIDDEN


async def test_user_add_non_authed__fail__401(client: AsyncClient) -> None:
    user_post_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    response: Response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}",
        json=user_post_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # add second user
    user_post_data_2: dict[str, str] = {
        "userName": "another user",
        "userPassword": "my-another-password",
    }
    response_2: Response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}",
        json=user_post_data_2,
    )
    assert response_2.status_code == status.HTTP_401_UNAUTHORIZED


async def test_user_add_as_admin__fail__user_already_exist(
    admin_role_authed_client: AsyncClient,
) -> None:
    user_post_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    response: Response = await admin_role_authed_client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}",
        json=user_post_data,
    )
    assert response.status_code == status.HTTP_409_CONFLICT

    content: dict[str, Any] = response.json()
    assert content["message"] == "User already exists."


async def test_user_add_as_user__fail__user_already_exist__but_403(
    user_role_authed_client: AsyncClient,
) -> None:
    user_post_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    response: Response = await user_role_authed_client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}",
        json=user_post_data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_add_non_authed__fail__user_already_exist__but_401(client: AsyncClient) -> None:
    user_post_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    response: Response = await client.post(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}",
        json=user_post_data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_user_get_as_admin__success(
    admin_role_authed_client: AsyncClient,
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]

    response: Response = await admin_role_authed_client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}",
    )
    assert response.status_code == status.HTTP_200_OK

    user: dict[str, Any] = response.json()
    assert equal_dict(
        user,
        user_data | {"id": user_id, "role": UserRoleType.USER},
        exclude_keys=["userPassword", "createdAt", "modifiedAt"],
    )


async def test_user_get_as_user__fail__403(
    user_role_authed_client: AsyncClient,
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]

    response: Response = await user_role_authed_client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_get_as_non_authed__fail__401(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]

    response: Response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_user_get_as_admin__fail__non_existing_user_id(
    admin_role_authed_client: AsyncClient,
) -> None:
    non_existing_user_id: int = 12345

    response: Response = await admin_role_authed_client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    content: dict[str, Any] = response.json()
    assert content["message"] == "User does not exist."


async def test_user_get_as_user__fail__non_existing_user_id__but_403(
    user_role_authed_client: AsyncClient,
) -> None:
    non_existing_user_id: int = 12345

    response: Response = await user_role_authed_client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_get_non_authed__fail__non_existing_user_id__but_401(
    client: AsyncClient,
) -> None:
    non_existing_user_id: int = 12345

    response: Response = await client.get(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_user_update_password_as_admin__success(
    admin_role_authed_client: AsyncClient,
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "my-password-123",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["userName"],
        user_password=user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    new_user_password: str = "<PASSWORD>"

    response: Response = await admin_role_authed_client.patch(
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


async def test_user_update_password_as_user__fail__403(
    user_role_authed_client: AsyncClient,
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "<PASSWORD>",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["userName"],
        user_password=user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    new_user_password: str = "<PASSWORD>"

    response: Response = await user_role_authed_client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}/password",
        json={"newUserPassword": new_user_password},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_update_password_non_authed__fail__401(
    client: AsyncClient,
    db_manager: DBManager,
) -> None:
    user_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "<PASSWORD>",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["userName"],
        user_password=user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    new_user_password: str = "<PASSWORD>"

    response: Response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}/password",
        json={"newUserPassword": new_user_password},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_user_update_password_as_admin__fail__user_id_not_exist(
    admin_role_authed_client: AsyncClient,
) -> None:
    non_existing_user_id: int = 12345

    response: Response = await admin_role_authed_client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}/password",
        json={"newUserPassword": "test"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    content: dict[str, Any] = response.json()
    assert content["message"] == "Record not found."


async def test_user_update_password_as_user__fail__user_id_not_exist__but_403(
    user_role_authed_client: AsyncClient,
) -> None:
    non_existing_user_id: int = 12345

    response: Response = await user_role_authed_client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}/password",
        json={"newUserPassword": "test"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_update_password_non_authed__fail__user_id_not_exist__but_401(
    client: AsyncClient,
) -> None:
    non_existing_user_id: int = 12345

    response: Response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}/password",
        json={"newUserPassword": "test"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_user_update_name_as_admin__success(
    admin_role_authed_client: AsyncClient, db_manager: DBManager
) -> None:
    user_data: dict[str, str] = {
        "userName": "New User",
        "userPassword": "<PASSWORD>",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    new_user_name = "Another Login"

    response: Response = await admin_role_authed_client.patch(
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


async def test_user_update_name_as_user__fail__403(
    user_role_authed_client: AsyncClient, db_manager: DBManager
) -> None:
    user_data: dict[str, str] = {
        "userName": "Another Login",
        "userPassword": "<PASSWORD>",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    new_user_name = "Another Login 2"

    response: Response = await user_role_authed_client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}/name",
        json={"newUserName": new_user_name},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_update_name_non_authed__fail__401(
    client: AsyncClient, db_manager: DBManager
) -> None:
    user_data: dict[str, str] = {
        "userName": "Another Login",
        "userPassword": "<PASSWORD>",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_data["userName"],
        user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    new_user_name = "Another Login 2"

    response: Response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}/name",
        json={"newUserName": new_user_name},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_user_update_name_as_admin__fail__username_already_exist(
    admin_role_authed_client: AsyncClient, db_manager: DBManager
) -> None:
    user_data: dict[str, str] = {
        "userName": "another user",
        "userPassword": "my-another-password",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["userName"],
        user_password=user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    new_user_name = "Another Login"

    response: Response = await admin_role_authed_client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}/name",
        json={"newUserName": new_user_name},
    )
    assert response.status_code == status.HTTP_409_CONFLICT

    content: dict[str, Any] = response.json()
    assert content["message"] == "User already exists."


async def test_user_update_name_as_user__fail__username_already_exist__but_403(
    user_role_authed_client: AsyncClient, db_manager: DBManager
) -> None:
    user_data: dict[str, str] = {
        "userName": "another user",
        "userPassword": "my-another-password",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["userName"],
        user_password=user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    new_user_name = "Another Login"

    response: Response = await user_role_authed_client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}/name",
        json={"newUserName": new_user_name},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_update_name_non_authed__fail__username_already_exist__but_401(
    client: AsyncClient, db_manager: DBManager
) -> None:
    user_data: dict[str, str] = {
        "userName": "another user",
        "userPassword": "my-another-password",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["userName"],
        user_password=user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]
    new_user_name = "Another Login"

    response: Response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}/name",
        json={"newUserName": new_user_name},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_user_update_name_as_admin__fail__user_id_not_exist(
    admin_role_authed_client: AsyncClient,
) -> None:
    non_existing_user_id: int = 12345

    response: Response = await admin_role_authed_client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}/name",
        json={"newUserName": "test"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    content: dict[str, Any] = response.json()
    assert content["message"] == "Record not found."


async def test_user_update_name_as_user__fail__user_id_not_exist__but_403(
    user_role_authed_client: AsyncClient,
) -> None:
    non_existing_user_id: int = 12345

    response: Response = await user_role_authed_client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}/name",
        json={"newUserName": "test"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_update_name_non_authed__fail__user_id_not_exist__but_401(
    client: AsyncClient,
) -> None:
    non_existing_user_id: int = 12345

    response: Response = await client.patch(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}/name",
        json={"newUserName": "test"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_user_delete_as_admin__fail__user_id_not_exist(
    admin_role_authed_client: AsyncClient,
) -> None:
    non_existing_user_id: int = 12345

    response: Response = await admin_role_authed_client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    content: dict[str, Any] = response.json()
    assert content["message"] == "User does not exist."


async def test_user_delete_as_user__fail__user_id_not_exist__but_403(
    user_role_authed_client: AsyncClient,
) -> None:
    non_existing_user_id: int = 12345

    response: Response = await user_role_authed_client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_delete_non_authed__fail__user_id_not_exist__but_401(
    client: AsyncClient,
) -> None:
    non_existing_user_id: int = 12345

    response: Response = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{non_existing_user_id}"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_user_delete_as_user__fail__403(
    user_role_authed_client: AsyncClient, db_manager: DBManager
) -> None:
    user_data: dict[str, str] = {
        "userName": "Another Login",
        "userPassword": "<PASSWORD>",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["userName"],
        user_password=user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]

    response: Response = await user_role_authed_client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_user_delete_non_authed__fail__401(
    client: AsyncClient, db_manager: DBManager
) -> None:
    user_data: dict[str, str] = {
        "userName": "Another Login",
        "userPassword": "<PASSWORD>",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["userName"],
        user_password=user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]

    response: Response = await client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_user_delete_as_admin__success(
    admin_role_authed_client: AsyncClient, db_manager: DBManager
) -> None:
    user_data: dict[str, str] = {
        "userName": "Another Login",
        "userPassword": "<PASSWORD>",
    }
    db_user: dict[str, Any] | None = await db_manager.get_user_by_credentials(
        user_name=user_data["userName"],
        user_password=user_data["userPassword"],
    )
    assert db_user is not None

    user_id: int = db_user["id"]

    response: Response = await admin_role_authed_client.delete(
        f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.USER}/{user_id}"
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
