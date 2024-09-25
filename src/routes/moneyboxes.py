"""The moneyboxes routes."""

from typing import Any, cast

from fastapi import APIRouter
from starlette.requests import Request

from src.custom_types import EndpointRouteType
from src.data_classes.responses import MoneyboxesResponse
from src.db.db_manager import DBManager
from src.routes.responses.moneyboxes import GET_MONEYBOXES_RESPONSES

moneyboxes_router: APIRouter = APIRouter(
    prefix=f"/{EndpointRouteType.MONEYBOXES}",
    tags=[EndpointRouteType.MONEYBOXES],
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
    """Endpoint for getting moneyboxes.
    \f

    :param request: The current request object.
    :return: The list of moneyboxes.
    :rtype: :class:`MoneyboxesResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    moneyboxes_data: list[dict[str, Any]] = await db_manager.get_moneyboxes()

    response_moneyboxes_data: dict[str, list[dict[str, Any]]] = {
        "moneyboxes": moneyboxes_data,
    }
    return response_moneyboxes_data  # type: ignore
