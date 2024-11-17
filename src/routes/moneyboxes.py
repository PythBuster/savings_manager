"""The moneyboxes routes."""

from typing import Any, cast

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.custom_types import EndpointRouteType, OverflowMoneyboxAutomatedSavingsModeType
from src.data_classes.responses import MoneyboxesResponse, MoneyboxesReachingSavingsTargetsResponse
from src.db.db_manager import DBManager
from src.db.exceptions import InconsistentDatabaseError, OverflowMoneyboxNotFoundError
from src.db.models import AppSettings
from src.routes.responses.moneyboxes import GET_MONEYBOXES_RESPONSES, GET_MONEYBOXES_REACHING_SAVINGS_TARGETS_RESPONSES
from src.utils import calculate_months_for_reaching_savings_targets

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

    :raises OverflowMoneyboxNotFoundError: if moneyboxes result is empty, it means, that
        the overflow moneybox is missing. At least the overflow moneybox has into the results.
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    moneyboxes_data: list[dict[str, Any]] = await db_manager.get_moneyboxes()

    if not moneyboxes_data:  # expected at least the overflow moneybox
        raise OverflowMoneyboxNotFoundError()

    response_moneyboxes_data: dict[str, list[dict[str, Any]]] = {
        "moneyboxes": moneyboxes_data,
    }
    return response_moneyboxes_data  # type: ignore


@moneyboxes_router.get(
    "/reaching_savings_targets",
    response_model=MoneyboxesReachingSavingsTargetsResponse,
    responses=GET_MONEYBOXES_REACHING_SAVINGS_TARGETS_RESPONSES,
)
async def get_months_for_reaching_savings_targets(
        request: Request,
) -> MoneyboxesReachingSavingsTargetsResponse | Response:
    """Endpoint for getting the number of months for reaching savings targets of the moneyboxes, if
    a savings target is set.
    \f

    :param request: The current request object.
    :return: A map of moneybox_id to number of months for reaching the savings target. Only moneyboxes
        with a savings target are included in the response.
    :rtype: :class:`MoneyboxesReachingSavingsTargetsResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    moneyboxes_data: list[dict[str, Any]] = await db_manager.get_moneyboxes()
    app_settings: AppSettings = await db_manager._get_app_settings()

    overflow_moneybox_mode: OverflowMoneyboxAutomatedSavingsModeType = app_settings.overflow_moneybox_automated_savings_mode
    savings_amount: int = app_settings.savings_amount

    reaching_savings_targets: dict[int, int] = calculate_months_for_reaching_savings_targets(
        moneyboxes=moneyboxes_data,
        savings_amount=savings_amount,
        overflow_moneybox_mode=overflow_moneybox_mode,
    )

    if reaching_savings_targets:
        return { # type: ignore
            "reaching_savings_targets": [
                {"moneybox_id": key, "amount_of_months": value}
                for key, value in reaching_savings_targets.items()
            ]
        }

    return Response(status_code=status.HTTP_204_NO_CONTENT)