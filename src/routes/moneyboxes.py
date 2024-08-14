"""The moneyboxes routes."""

from fastapi import APIRouter
from starlette.requests import Request

from src.custom_types import EndpointRouteType
from src.data_classes.responses import MoneyboxesResponse
from src.routes.responses.moneyboxes import GET_MONEYBOXES_RESPONSES

moneyboxes_router = APIRouter(
    prefix=f"/{EndpointRouteType.MONEYBOXES}",
    tags=[EndpointRouteType.MONEYBOXES.lower()],
)
"""The moneyboxes router."""


@moneyboxes_router.get(
    "",
    response_model=MoneyboxesResponse,
    responses=GET_MONEYBOXES_RESPONSES,
)
async def get_moneyboxes(
    request: Request,
) -> MoneyboxesResponse:
    """Endpoint for getting moneyboxes."""

    moneyboxes_data = await request.app.state.db_manager.get_moneyboxes()

    response_moneyboxes_data = {
        "moneyboxes": moneyboxes_data,
    }
    moneyboxes = MoneyboxesResponse(**response_moneyboxes_data)
    return moneyboxes
