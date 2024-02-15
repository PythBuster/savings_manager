"""The moneybox routes."""

from fastapi import APIRouter
from starlette.requests import Request

from src.custom_types import EndpointRouteType
from src.data_classes.requests import MoneyboxPostRequest
from src.data_classes.responses import MoneyboxResponse
from src.routes.responses.moneybox import (
    GET_MONEYBOX_RESPONSES,
    POST_MONEYBOX_RESPONSES,
)

moneybox_router = APIRouter(
    prefix=f"/{EndpointRouteType.MONEYBOX}",
    tags=["moneybox"],
)


@moneybox_router.get(
    "/{moneybox_id}",
    response_model=MoneyboxResponse,
    responses=GET_MONEYBOX_RESPONSES,
)
async def get_moneybox(
    request: Request,
    moneybox_id: int,
) -> MoneyboxResponse:
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
    moneybox_data = await request.app.state.db_manager.add_moneybox(
        moneybox_data=moneybox_post_request.model_dump()
    )
    return MoneyboxResponse(**moneybox_data)
