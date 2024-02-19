"""The moneyboxes routes."""

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

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
) -> MoneyboxesResponse | Response:
    """Endpoint for getting moneyboxes.

    :param request: The current request.
    :type request: :class:`Request`
    :return: The moneyboxes.
    :rtype: :class:`MoneyboxesResponse`
    """

    moneyboxes_data = await request.app.state.db_manager.get_moneyboxes()

    if moneyboxes_data:
        moneyboxes_data = {
            "total": len(moneyboxes_data),
            "moneyboxes": moneyboxes_data,
        }
        moneyboxes = MoneyboxesResponse(**moneyboxes_data)
        return moneyboxes

    return Response(status_code=status.HTTP_204_NO_CONTENT)
