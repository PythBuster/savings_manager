"""The users routes."""

from typing import Annotated, cast

from fastapi import APIRouter, Path
from starlette.requests import Request

from src.custom_types import EndpointRouteType
from src.data_classes.responses import LoginUserResponse
from src.db.db_manager import DBManager

user_router: APIRouter = APIRouter(
    prefix=f"/{EndpointRouteType.USER}",
    tags=[EndpointRouteType.USER],
)
"""The user router."""


@user_router.get(
    "/{user_id}",
    response_model=LoginUserResponse,
    responses=...,
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
    user = await db_manager.get_users()

    # TODO implement ...
