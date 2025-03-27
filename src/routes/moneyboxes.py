"""The moneyboxes routes."""

from typing import Any, cast

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.custom_types import (
    EndpointRouteType,
    MoneyboxSavingsMonthData,
    OverflowMoneyboxAutomatedSavingsModeType,
)
from src.data_classes.responses import (
    MoneyboxesResponse,
    MoneyboxForecastListResponse,
    MoneyboxForecastResponse,
)
from src.db.db_manager import DBManager
from src.db.models import AppSettings
from src.routes.responses.moneyboxes import (
    GET_MONEYBOXES_RESPONSES,
    GET_SAVINGS_FORECAST_RESPONSES,
)
from src.utils import calculate_savings_forecast

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
    "/savings_forecast",
    response_model=MoneyboxForecastListResponse,
    responses=GET_SAVINGS_FORECAST_RESPONSES,
)
async def get_savings_forecast_endpoint(
    request: Request,
) -> MoneyboxForecastListResponse | Response:
    """Returns a forecast of monthly savings distributions for each moneybox.

    This endpoint provides a projection of which moneyboxes will receive distributions
    in the upcoming months, including the expected amount for each. The forecast
    is based on current budget rules, savings priorities, and available funds.

    The Overflow Moneybox is not a part of the results.
    \f

    :param request: The current request object.
    :return: A list of moneyboxes and their respective savings distributions.
    :rtype: :class:`MoneyboxForecastListResponse`
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
        calculate_savings_forecast(
            moneyboxes=moneyboxes_data,
            app_settings=app_settings.asdict(),
            overflow_moneybox_mode=overflow_moneybox_mode,
        )
    )

    if reaching_savings_targets:
        return MoneyboxForecastListResponse(
            moneybox_forecasts=[
                MoneyboxForecastResponse(
                    moneybox_id=moneybox_id,
                    monthly_distributions=[
                        {"month": data.month, "amount": data.amount}
                        for data in moneybox_savings_month_data
                        if data.month > 0
                    ],
                    reached_in_months=(
                        moneybox_savings_month_data[-1].month  # can be 0 or >0
                        if moneybox_savings_month_data[-1].month != -1
                        else None  # if -1, reached: never
                    ),
                )
                for moneybox_id, moneybox_savings_month_data in reaching_savings_targets.items()
            ]
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
