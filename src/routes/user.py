"""The users routes."""

from typing import Annotated, cast

from fastapi import APIRouter, Path, Body
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.custom_types import EndpointRouteType
from src.data_classes.requests import LoginUserRequest
from src.data_classes.responses import LoginUserResponse
from src.db.db_manager import DBManager
from src.routes.responses.user import GET_USER_RESPONSES, DELETE_USER_RESPONSES, ADD_USER_RESPONSES

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
    "",
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
        user_login=user_create_request.user_login,
        user_password=user_create_request.user_password.get_secret_value(),
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
