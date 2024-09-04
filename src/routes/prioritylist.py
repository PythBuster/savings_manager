"""The prioritylist routes."""

from typing import Annotated

from fastapi import APIRouter, Body
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.custom_types import EndpointRouteType
from src.data_classes.requests import PrioritylistRequest
from src.data_classes.responses import PrioritylistResponse
from src.db.db_manager import DBManager
from src.routes.responses.prioritylist import (
    GET_PRIORITYLIST_RESPONSES,
    UPDATE_PRIORITYLIST_RESPONSES,
)

prioritylist_router = APIRouter(
    prefix=f"/{EndpointRouteType.PRIORITYLIST}",
    tags=[EndpointRouteType.PRIORITYLIST],
)
"""The prioritylist router."""


@prioritylist_router.get(
    "",
    response_model=PrioritylistResponse,
    responses=GET_PRIORITYLIST_RESPONSES,
)
async def get_prioritylist(
    request: Request,
) -> PrioritylistResponse | Response:
    """Endpoint for getting prioritylist. Note: Returns a list SORTED by priority (asc)."""

    db_manager: DBManager = request.app.state.db_manager
    priority_list = await db_manager.get_prioritylist()

    if priority_list:
        return {"prioritylist": priority_list}  # type: ignore

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@prioritylist_router.patch(
    "",
    response_model=PrioritylistResponse,
    responses=UPDATE_PRIORITYLIST_RESPONSES,
)
async def update_prioritylist(
    request: Request,
    prioritylist: Annotated[
        PrioritylistRequest,
        Body(title="Update Data", description="The updating priority list data."),
    ],
) -> PrioritylistResponse:
    """Endpoint for updating priority list. Note: Returns the updated list
    SORTED by priority (asc)."""

    db_manager: DBManager = request.app.state.db_manager
    updated_priority_list = await db_manager.update_prioritylist(
        priorities=prioritylist.model_dump()["prioritylist"],
    )

    return {"prioritylist": updated_priority_list}  # type: ignore
