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
async def get_priority_list(
    request: Request,
) -> PrioritylistResponse | Response:
    """Endpoint for getting priority list."""

    db_manager: DBManager = request.app.state.db_manager
    priority_list = await db_manager.get_priority_list()

    if priority_list:
        return PrioritylistResponse(priority_list=priority_list)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@prioritylist_router.patch(
    "",
    response_model=PrioritylistResponse,
    responses=UPDATE_PRIORITYLIST_RESPONSES,
)
async def update_priority_list(
    request: Request,
    priority_list: Annotated[
        PrioritylistRequest,
        Body(title="Update Data", description="The updating priority list data."),
    ],
) -> PrioritylistResponse:
    """Endpoint for updating priority list."""

    db_manager: DBManager = request.app.state.db_manager
    updated_priority_list = await db_manager.update_priority_list(
        priorities=priority_list.model_dump()["priority_list"],
    )

    return PrioritylistResponse(priority_list=updated_priority_list)
