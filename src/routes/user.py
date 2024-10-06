"""The users routes."""

from typing import Annotated, cast

from fastapi import APIRouter, Path, Body
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.custom_types import EndpointRouteType
from src.data_classes.requests import LoginUserRequest, LoginUserUpdateNameRequest, LoginUserUpdatePasswordRequest
from src.data_classes.responses import LoginUserResponse
from src.db.db_manager import DBManager
from src.routes.responses.user import GET_USER_RESPONSES, DELETE_USER_RESPONSES, ADD_USER_RESPONSES, \
    UPDATE_USER_PASSWORD_RESPONSES, UPDATE_USER_NAME_RESPONSES

user_router: APIRouter = APIRouter(
    prefix=f"/{EndpointRouteType.USER}",
    tags=[EndpointRouteType.USER],
)
"""The user router."""


@user_router.get(
    "/{user_id}",
    response_model=LoginUserResponse,
    responses=GET_USER_RESPONSES,
)
async def get_user(
    request: Request,
    user_id: Annotated[
        int,
        Path(
            title="User ID",
            description="User ID to be retrieved.",
        ),
    ],
) -> LoginUserResponse:
    """Endpoint for getting user by user_id.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param user_id: The user ID to be retrieved.
    :type user_id: :class:`int`
    :return: The requested user data.
    :rtype: :class:`LoginUserResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    user = await db_manager.get_user(user_id=user_id)

    return user



@user_router.post(
    "/register",
    response_model=LoginUserResponse,
    responses=ADD_USER_RESPONSES,
)
async def add_user(
    request: Request,
    user_create_request: Annotated[
        LoginUserRequest,
        Body(title="Post Data", description="The new moneybox data."),
    ],
) -> LoginUserResponse:
    """Endpoint for creating new user.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param user_create_request: The data of the new user.
    :type user_create_request: :class:`LoginUserRequest`
    :return: The requested user data.
    :rtype: :class:`LoginUserResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    user = await db_manager.add_user(
        user_name=user_create_request.user_name,
        user_password=user_create_request.user_password.get_secret_value(),
    )
    return user  # type: ignore

# TODO: Require the current password before setting a new one!
#   The user is authenticated, but for added security,
#   it's better to prompt for the current password again.
#   -> adapt code!
@user_router.patch(
    "/{user_id}/password",
    response_model=LoginUserResponse,
    responses=UPDATE_USER_PASSWORD_RESPONSES,
)
async def update_user_password(
    request: Request,
    user_id: Annotated[
        int, Path(title="User ID", description="User ID to be updated.")
    ],
    user_data: Annotated[
        LoginUserUpdatePasswordRequest,
        Body(title="Update Password", description="The updating user password."),
    ],
) -> LoginUserResponse:
    """Endpoint for updating users password.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param user_id: The user ID to be updated.
    :type user_id: :class:`int`
    :param user_data: The new user password.
    :type user_data: :class:`LoginUserUpdatePasswordRequest`
    :return: The updated user.
    :rtype: :class:`LoginUserResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    user = await db_manager.update_user_password(
        user_id=user_id,
        new_user_password=user_data.new_user_password.get_secret_value(),
    )

    return user  # type: ignore


@user_router.patch(
    "/{user_id}/name",
    response_model=LoginUserResponse,
    responses=UPDATE_USER_NAME_RESPONSES,
)
async def update_user_name(
    request: Request,
    user_id: Annotated[
        int, Path(title="User ID", description="User ID to be updated.")
    ],
    user_data: Annotated[
        LoginUserUpdateNameRequest,
        Body(title="Update Login (name)", description="The updating user login."),
    ],
) -> LoginUserResponse:
    """Endpoint for updating username.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param user_id: The user ID to be updated.
    :type user_id: :class:`int`
    :param user_data: The new username.
    :type user_data: :class:`LoginUserUpdateNameRequest`
    :return: The updated user.
    :rtype: :class:`LoginUserResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    user = await db_manager.update_user_name(
        user_id=user_id,
        new_user_name=user_data.new_user_name,
    )

    return user  # type: ignore


@user_router.delete(
    "/{user_id}",
    responses=DELETE_USER_RESPONSES,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    request: Request,
    user_id: Annotated[
        int,
        Path(
            title="User ID",
            description="User ID to be deleted.",
        ),
    ],
) -> Response:
    """Endpoint for deleting user by user_id.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param user_id: The user ID to be deleted.
    :type user_id: :class:`int`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    await db_manager.delete_user(user_id=user_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
