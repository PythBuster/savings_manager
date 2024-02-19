"""The moneybox routes."""

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.custom_types import EndpointRouteType
from src.data_classes.requests import MoneyboxPatchRequest, MoneyboxPostRequest
from src.data_classes.responses import MoneyboxResponse
from src.routes.responses.moneybox import (
    DELETE_MONEYBOX_RESPONSES,
    GET_MONEYBOX_RESPONSES,
    PATCH_MONEYBOX_RESPONSES,
    POST_MONEYBOX_RESPONSES,
)

moneybox_router = APIRouter(
    prefix=f"/{EndpointRouteType.MONEYBOX}",
    tags=[EndpointRouteType.MONEYBOX.lower()],
)
"""The moneybox router."""


@moneybox_router.get(
    "/{moneybox_id}",
    response_model=MoneyboxResponse,
    responses=GET_MONEYBOX_RESPONSES,
)
async def get_moneybox(
    request: Request,
    moneybox_id: int,
) -> MoneyboxResponse:
    """Endpoint for getting moneybox by moneybox_id."""

    moneybox_data = await request.app.state.db_manager.get_moneybox(moneybox_id=moneybox_id)
    return MoneyboxResponse(**moneybox_data)


@moneybox_router.post(
    "",
    response_model=MoneyboxResponse,
    responses=POST_MONEYBOX_RESPONSES,
)
async def add_moneybox(
    request: Request,
    moneybox_post_request: MoneyboxPostRequest,
) -> MoneyboxResponse:
    """Endpoint for adding moneybox."""

    moneybox_data = await request.app.state.db_manager.add_moneybox(
        moneybox_data=moneybox_post_request.model_dump()
    )
    return MoneyboxResponse(**moneybox_data)


@moneybox_router.patch(
    "/{moneybox_id}",
    response_model=MoneyboxResponse,
    responses=PATCH_MONEYBOX_RESPONSES,
)
async def update_moneybox(
    request: Request,
    moneybox_id: int,
    moneybox_patch_request: MoneyboxPatchRequest,
) -> MoneyboxResponse:
    """Endpoint for updating moneybox by moneybox_id."""

    moneybox_data = await request.app.state.db_manager.update_moneybox(
        moneybox_id=moneybox_id, moneybox_data=moneybox_patch_request.model_dump(exclude_none=True)
    )
    return MoneyboxResponse(**moneybox_data)


@moneybox_router.delete(
    "/{moneybox_id}",
    responses=DELETE_MONEYBOX_RESPONSES,
)
async def delete_moneybox(
    request: Request,
    moneybox_id: int,
) -> Response:
    """Endpoint for deleting moneybox by moneybox_id."""

    await request.app.state.db_manager.delete_moneybox(
        moneybox_id=moneybox_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
