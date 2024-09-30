"""The users routes."""

from typing import Annotated, cast

from fastapi import APIRouter, Path
from starlette.requests import Request

from src.custom_types import EndpointRouteType
from src.data_classes.responses import LoginUserResponse, PrioritylistResponse
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
    """Endpoint for getting prioritylist. Note: Returns a list SORTED by priority (asc).
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :return: The prioritylist if not empty, else a response object including status
        code 204.
    :rtype: :class:`PrioritylistResponse` | :class:`Response`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    user = await db_manager.get_users()

    # TODO implement ...
