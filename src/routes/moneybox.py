"""The moneybox routes."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from src.custom_types import EndpointRouteType, TransactionTrigger, TransactionType
from src.data_classes.requests import (
    DepositTransactionRequest,
    MoneyboxCreateRequest,
    MoneyboxUpdateRequest,
    TransferTransactionRequest,
    WithdrawTransactionRequest,
)
from src.data_classes.responses import MoneyboxResponse, TransactionLogsResponse
from src.routes.responses.moneybox import (
    CREATE_MONEYBOX_RESPONSES,
    DELETE_MONEYBOX_RESPONSES,
    DEPOSIT_MONEYBOX_RESPONSES,
    GET_MONEYBOX_RESPONSES,
    MONEYBOX_TRANSACTION_LOGS_RESPONSES,
    TRANSFER_MONEYBOX_RESPONSES,
    UPDATE_MONEYBOX_RESPONSES,
    WITHDRAW_MONEYBOX_RESPONSES,
)
from src.utils import check_existence_of_moneybox_by_id

moneybox_router = APIRouter(
    prefix=f"/{EndpointRouteType.MONEYBOX}",
    tags=[EndpointRouteType.MONEYBOX],
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
        int, Path(title="Moneybox ID", description="Moneybox ID to be retrieved.")
    ],
) -> MoneyboxResponse:
    """Endpoint for getting moneybox by moneybox_id."""

    moneybox_data = await request.app.state.db_manager.get_moneybox(moneybox_id=moneybox_id)
    return moneybox_data  # type: ignore


@moneybox_router.post(
    "",
    response_model=MoneyboxResponse,
    responses=CREATE_MONEYBOX_RESPONSES,
)
async def add_moneybox(
    request: Request,
    moneybox_create_request: Annotated[
        MoneyboxCreateRequest, Body(title="Post Data", description="The new moneybox data.")
    ],
) -> MoneyboxResponse:
    """Endpoint for adding moneybox."""

    moneybox_data = await request.app.state.db_manager.add_moneybox(
        moneybox_data=moneybox_create_request.model_dump()
    )
    return moneybox_data  # type: ignore


@moneybox_router.patch(
    "/{moneybox_id}",
    response_model=MoneyboxResponse,
    responses=UPDATE_MONEYBOX_RESPONSES,
)
async def update_moneybox(
    request: Request,
    moneybox_id: Annotated[int, Depends(check_existence_of_moneybox_by_id)],
    moneybox_update_request: Annotated[
        MoneyboxUpdateRequest, Body(title="Update Data", description="The updating moneybox data.")
    ],
) -> MoneyboxResponse:
    """Endpoint for updating moneybox by moneybox_id."""

    moneybox_data = await request.app.state.db_manager.update_moneybox(
        moneybox_id=moneybox_id,
        moneybox_data=moneybox_update_request.model_dump(exclude_unset=True),
    )
    return moneybox_data  # type: ignore


@moneybox_router.delete(
    "/{moneybox_id}",
    responses=DELETE_MONEYBOX_RESPONSES,
    status_code=status.HTTP_204_NO_CONTENT,  # set default status code to 204
)
async def delete_moneybox(
    request: Request,
    moneybox_id: Annotated[int, Depends(check_existence_of_moneybox_by_id)],
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
        int,
        Depends(check_existence_of_moneybox_by_id),
    ],
    deposit_transaction: Annotated[
        DepositTransactionRequest,
        Body(
            title="Deposit amount",
            description="The deposit transaction with amount to add to moneybox, has to be >=0.",
        ),
    ],
) -> MoneyboxResponse:
    """Endpoint to add amount to moneybox by moneybox_id."""

    moneybox_data = await request.app.state.db_manager.add_amount(
        moneybox_id=moneybox_id,
        deposit_transaction_data=deposit_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    return moneybox_data  # type: ignore


@moneybox_router.post(
    "/{moneybox_id}/balance/sub",
    response_model=MoneyboxResponse,
    responses=WITHDRAW_MONEYBOX_RESPONSES,
)
async def withdraw_moneybox(
    request: Request,
    moneybox_id: Annotated[
        int,
        Depends(check_existence_of_moneybox_by_id),
    ],
    withdraw_transaction: Annotated[
        WithdrawTransactionRequest,
        Body(
            title="Withdraw amount",
            description=(
                "The withdrawal transaction with amount to sub from moneybox, has to be >=0."
            ),
        ),
    ],
) -> MoneyboxResponse:
    """Endpoint to sub balance from moneybox by moneybox_id."""

    moneybox_data = await request.app.state.db_manager.sub_amount(
        moneybox_id=moneybox_id,
        withdraw_transaction_data=withdraw_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    return moneybox_data  # type: ignore


@moneybox_router.post(
    "/{moneybox_id}/balance/transfer",
    responses=TRANSFER_MONEYBOX_RESPONSES,
    status_code=status.HTTP_204_NO_CONTENT,  # set default status code to 204
)
async def transfer_balance(
    request: Request,
    moneybox_id: Annotated[
        int,
        Depends(check_existence_of_moneybox_by_id),
    ],
    transfer_transaction: Annotated[
        TransferTransactionRequest,
        Body(
            title="Transfer amount",
            description=(
                "The amount to transfer from moneybox_id to to_moneybox_id, amount has to be >=0."
            ),
        ),
    ],
) -> Response:
    """Endpoint to transfer balance from `moneybox_id` to `to_moneybox_id`."""

    await request.app.state.db_manager.transfer_amount(
        from_moneybox_id=moneybox_id,
        transfer_transaction_data=transfer_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@moneybox_router.get(
    "/{moneybox_id}/transactions",
    response_model=TransactionLogsResponse,
    responses=MONEYBOX_TRANSACTION_LOGS_RESPONSES,
)
async def get_moneybox_transaction_logs(
    request: Request,
    moneybox_id: Annotated[
        int,
        Depends(check_existence_of_moneybox_by_id),
    ],
) -> TransactionLogsResponse | Response:
    """Endpoint for getting moneybox transaction logs."""

    transaction_logs_data = await request.app.state.db_manager.get_transaction_logs(
        moneybox_id=moneybox_id,
    )

    if transaction_logs_data:
        transaction_logs_data = {
            "transaction_logs": transaction_logs_data,
        }
        return transaction_logs_data  # type: ignore

    return Response(status_code=status.HTTP_204_NO_CONTENT)
