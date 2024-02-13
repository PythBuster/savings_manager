"""The moneybox routes."""

from fastapi import APIRouter
from starlette.requests import Request

from src.custom_types import EndpointRouteType
from src.data_classes.moneybox import MoneyboxResponse

moneybox_router = APIRouter(
    prefix=f"/{EndpointRouteType.MONEYBOX}",
    tags=["moneybox"],
)


@moneybox_router.get(
    "/{moneybox_id}",
    response_model=MoneyboxResponse,
)
async def get_moneybox(
    request: Request,
    moneybox_id: int,
) -> MoneyboxResponse:
    moneybox_data = await request.app.state.db_manager.get_moneybox(moneybox_id=moneybox_id)
    return MoneyboxResponse(**moneybox_data)
