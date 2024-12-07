"""The moneyboxes routes."""

from typing import Any, cast

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.custom_types import (
    EndpointRouteType,
    MoneyboxSavingsMonthData,
    OverflowMoneyboxAutomatedSavingsModeType,
)
from src.data_classes.responses import (
    MoneyboxesReachingSavingsTargetsResponse,
    MoneyboxesResponse,
)
from src.db.db_manager import DBManager
from src.db.models import AppSettings
from src.routes.responses.moneyboxes import (
    GET_MONEYBOXES_REACHING_SAVINGS_TARGETS_RESPONSES,
    GET_MONEYBOXES_RESPONSES,
)
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
async def get_moneyboxes_endpoint(
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

    _ = MoneyboxesResponse(moneyboxes=moneyboxes_data)

    response_moneyboxes_data: dict[str, list[dict[str, Any]]] = {
        "moneyboxes": moneyboxes_data,
    }
    return response_moneyboxes_data  # type: ignore


@moneyboxes_router.get(
    "/reaching_savings_targets",
    response_model=MoneyboxesReachingSavingsTargetsResponse,
    responses=GET_MONEYBOXES_REACHING_SAVINGS_TARGETS_RESPONSES,
)
async def get_reaching_savings_targets(
    request: Request,
) -> MoneyboxesReachingSavingsTargetsResponse | Response:
    """Endpoint for getting the number of months for reaching savings targets of the moneyboxes, if
    a savings target is set.
    \f

    :param request: The current request object.
    :return: A map of moneybox_id to number of months for reaching
        the savings target. Only moneyboxes with a savings target are included
        in the response.
    :rtype: :class:`MoneyboxesReachingSavingsTargetsResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    moneyboxes_data: list[dict[str, Any]] = await db_manager.get_moneyboxes()

    # validate before continuing
    _ = MoneyboxesResponse(moneyboxes=moneyboxes_data)

    app_settings: AppSettings = (
        await db_manager._get_app_settings()  # pylint: disable=protected-access
    )

    overflow_moneybox_mode: OverflowMoneyboxAutomatedSavingsModeType = (
        app_settings.overflow_moneybox_automated_savings_mode
    )

    reaching_savings_targets: dict[int, list[MoneyboxSavingsMonthData]] = (
        calculate_months_for_reaching_savings_targets(
            moneyboxes=moneyboxes_data,
            app_settings=app_settings.asdict(),
            overflow_moneybox_mode=overflow_moneybox_mode,
        )
    )

    if reaching_savings_targets:
        return {  # type: ignore
            "reaching_savings_targets": [
                {"moneybox_id": moneybox_id, "amount_of_months": list_of_distributions[-1].month}
                for moneybox_id, list_of_distributions in reaching_savings_targets.items()
            ]
        }

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@moneyboxes_router.get(
    "/next_automated_savings_moneyboxes",
    response_model=MoneyboxesReachingSavingsTargetsResponse,
    responses=GET_MONEYBOXES_REACHING_SAVINGS_TARGETS_RESPONSES,
)
async def get_next_automated_savings_moneyboxes(
    request: Request,
) -> Response:
    """Collect and return a list of moneybox IDs that would receive
    savings next month (automated saving).
    \f

    :param request: The current request object.
    :return: A list of moneybox IDs.
    :rtype: :class:`Response`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    moneyboxes_data: list[dict[str, Any]] = await db_manager.get_moneyboxes()

    # validate before continuing
    _ = MoneyboxesResponse(moneyboxes=moneyboxes_data)

    app_settings: AppSettings = (
        await db_manager._get_app_settings()  # pylint: disable=protected-access
    )

    overflow_moneybox_mode: OverflowMoneyboxAutomatedSavingsModeType = (
        app_settings.overflow_moneybox_automated_savings_mode
    )

    next_month_moneyboxes: dict[int, list[MoneyboxSavingsMonthData]] = (
        calculate_months_for_reaching_savings_targets(
            moneyboxes=moneyboxes_data,
            app_settings=app_settings.asdict(),
            overflow_moneybox_mode=overflow_moneybox_mode,
        )
    )

    if next_month_moneyboxes:
        return JSONResponse(
            content={
                "moneyboxIds": [
                    moneybox_id
                    for moneybox_id, list_of_distributions in next_month_moneyboxes.items()
                    if list_of_distributions[0].month == 1
                ]
            }
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
