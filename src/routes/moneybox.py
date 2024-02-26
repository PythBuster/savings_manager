"""The moneybox routes."""

from typing import Annotated

from fastapi import APIRouter, Body, Path
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.custom_types import EndpointRouteType
from src.data_classes.requests import (
    DepositModel,
    MoneyboxCreateModel,
    MoneyboxUpdateModel,
    TransferModel,
    WithdrawModel,
)
from src.data_classes.responses import MoneyboxResponse
from src.routes.responses.moneybox import (
    CREATE_MONEYBOX_RESPONSES,
    DELETE_MONEYBOX_RESPONSES,
    DEPOSIT_MONEYBOX_RESPONSES,
    GET_MONEYBOX_RESPONSES,
    TRANSFER_MONEYBOX_RESPONSES,
    UPDATE_MONEYBOX_RESPONSES,
    WITHDRAW_MONEYBOX_RESPONSES,
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
    moneybox_id: Annotated[
        int, Path(ge=1, title="Moneybox ID", description="Moneybox ID to be retrieved.")
    ],
) -> MoneyboxResponse:
    """Endpoint for getting moneybox by moneybox_id."""

    moneybox_data = await request.app.state.db_manager.get_moneybox(moneybox_id=moneybox_id)
    return MoneyboxResponse(**moneybox_data)


@moneybox_router.post(
    "",
    response_model=MoneyboxResponse,
    responses=CREATE_MONEYBOX_RESPONSES,
)
async def add_moneybox(
    request: Request,
    moneybox_create_request: Annotated[
        MoneyboxCreateModel, Body(title="Post Data", description="The new moneybox data.")
    ],
) -> MoneyboxResponse:
    """Endpoint for adding moneybox."""

    moneybox_data = await request.app.state.db_manager.add_moneybox(
        moneybox_data=moneybox_create_request.model_dump()
    )
    return MoneyboxResponse(**moneybox_data)


@moneybox_router.patch(
    "/{moneybox_id}",
    response_model=MoneyboxResponse,
    responses=UPDATE_MONEYBOX_RESPONSES,
)
async def update_moneybox(
    request: Request,
    moneybox_id: Annotated[
        int, Path(ge=1, title="Moneybox ID", description="Moneybox ID to be updated.")
    ],
    moneybox_update_request: Annotated[
        MoneyboxUpdateModel, Body(title="Update Data", description="The updating moneybox data.")
    ],
) -> MoneyboxResponse:
    """Endpoint for updating moneybox by moneybox_id."""

    moneybox_data = await request.app.state.db_manager.update_moneybox(
        moneybox_id=moneybox_id, moneybox_data=moneybox_update_request.model_dump(exclude_none=True)
    )
    return MoneyboxResponse(**moneybox_data)


@moneybox_router.delete(
    "/{moneybox_id}",
    responses=DELETE_MONEYBOX_RESPONSES,
)
async def delete_moneybox(
    request: Request,
    moneybox_id: Annotated[
        int, Path(ge=1, title="Moneybox ID", description="Moneybox ID to be deleted.")
    ],
) -> Response:
    """Endpoint for deleting moneybox by moneybox_id."""

    await request.app.state.db_manager.delete_moneybox(
        moneybox_id=moneybox_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@moneybox_router.post(
    "/{moneybox_id}/balance/add",
    response_model=MoneyboxResponse,
    responses=DEPOSIT_MONEYBOX_RESPONSES,
)
async def deposit_moneybox(
    request: Request,
    moneybox_id: Annotated[
        int, Path(ge=1, title="Moneybox ID", description="Moneybox ID to be updated.")
    ],
    deposit: Annotated[
        DepositModel,
        Body(title="Deposit balance", description="The balance to add to moneybox, has to be >=0."),
    ],
) -> MoneyboxResponse:
    """Endpoint to add balance to moneybox by moneybox_id."""

    moneybox_data = await request.app.state.db_manager.add_balance(
        moneybox_id=moneybox_id, balance=deposit.balance
    )
    return MoneyboxResponse(**moneybox_data)


@moneybox_router.post(
    "/{moneybox_id}/balance/sub",
    response_model=MoneyboxResponse,
    responses=WITHDRAW_MONEYBOX_RESPONSES,
)
async def withdraw_moneybox(
    request: Request,
    moneybox_id: Annotated[
        int, Path(ge=1, title="Moneybox ID", description="Moneybox ID to be updated.")
    ],
    withdraw: Annotated[
        WithdrawModel,
        Body(
            title="Withdraw balance", description="The balance to sub from moneybox, has to be >=0."
        ),
    ],
) -> MoneyboxResponse:
    """Endpoint to sub balance from moneybox by moneybox_id."""

    moneybox_data = await request.app.state.db_manager.sub_balance(
        moneybox_id=moneybox_id, balance=withdraw.balance
    )
    return MoneyboxResponse(**moneybox_data)


@moneybox_router.post(
    "/{moneybox_id}/balance/transfer",
    responses=TRANSFER_MONEYBOX_RESPONSES,
)
async def transfer_balance(
    request: Request,
    moneybox_id: Annotated[
        int, Path(ge=1, title="Moneybox ID", description="Moneybox ID to transfer balance from.")
    ],
    transfer: Annotated[
        TransferModel,
        Body(
            title="Transfer balance",
            description=(
                "The balance to transfer from moneybox_id to to_moneybox_id, balance has to be >=0."
            ),
        ),
    ],
) -> Response:
    """Endpoint to transfer balance from `moneybox_id` to `to_moneybox_id`."""

    await request.app.state.db_manager.transfer_balance(
        from_moneybox_id=moneybox_id,
        to_moneybox_id=transfer.to_moneybox_id,
        balance=transfer.balance,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
