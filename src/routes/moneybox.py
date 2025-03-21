"""The moneybox routes."""

from typing import Annotated, Any, cast

from fastapi import APIRouter, Body, Path
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
from src.db.db_manager import DBManager
from src.routes.responses.moneybox import (
    DELETE_MONEYBOX_RESPONSES,
    GET_MONEYBOX_RESPONSES,
    GET_MONEYBOX_TRANSACTION_LOGS_RESPONSES,
    PATCH_MONEYBOX_RESPONSES,
    POST_MONEYBOX_DEPOSIT_RESPONSES,
    POST_MONEYBOX_RESPONSES,
    POST_MONEYBOX_WITHDRAW_RESPONSES,
    POST_TRANSFER_MONEYBOX_RESPONSES,
)

moneybox_router: APIRouter = APIRouter(
    prefix=f"/{EndpointRouteType.MONEYBOX}",
    tags=[EndpointRouteType.MONEYBOX],
)
"""The moneybox router."""


@moneybox_router.get(
    "/{moneybox_id}",
    response_model=MoneyboxResponse,
    responses=GET_MONEYBOX_RESPONSES,
)
async def get_moneybox_endpoint(
    request: Request,
    moneybox_id: Annotated[
        int, Path(title="Moneybox ID", description="Moneybox ID to be retrieved.")
    ],
) -> MoneyboxResponse:
    """Endpoint for getting moneybox by moneybox_id.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param moneybox_id: The moneybox ID to be retrieved.
    :type moneybox_id: :class:`int`
    :return: The requested moneybox data.
    :rtype: :class:`MoneyboxResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    moneybox_data: dict[str, Any] = await db_manager.get_moneybox(moneybox_id=moneybox_id)

    return moneybox_data  # type: ignore


@moneybox_router.post(
    "",
    response_model=MoneyboxResponse,
    responses=POST_MONEYBOX_RESPONSES,
)
async def post_moneybox_endpoint(
    request: Request,
    moneybox_create_request: Annotated[
        MoneyboxCreateRequest,
        Body(title="Post Data", description="The new moneybox data."),
    ],
) -> MoneyboxResponse:
    """Endpoint for adding moneybox.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param moneybox_create_request: The new moneybox data.
    :type moneybox_create_request: :class:`MoneyboxCreateRequest`
    :return: The created moneybox data.
    :rtype: :class:`MoneyboxResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    moneybox_data: dict[str, Any] = await db_manager.add_moneybox(
        moneybox_data=moneybox_create_request.model_dump()
    )
    return moneybox_data  # type: ignore


@moneybox_router.patch(
    "/{moneybox_id}",
    response_model=MoneyboxResponse,
    responses=PATCH_MONEYBOX_RESPONSES,
)
async def patch_moneybox_endpoint(
    request: Request,
    moneybox_id: Annotated[
        int, Path(title="Moneybox ID", description="Moneybox ID to be updated.")
    ],
    moneybox_update_request: Annotated[
        MoneyboxUpdateRequest,
        Body(title="Update Data", description="The updating moneybox data."),
    ],
) -> MoneyboxResponse:
    """Endpoint for updating moneybox by moneybox_id.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param moneybox_id: The moneybox ID to be updated.
    :type moneybox_id: :class:`int`
    :param moneybox_update_request: The new moneybox data.
    :type moneybox_update_request: :class:`MoneyboxUpdateRequest`
    :return: The updated moneybox data.
    :rtype: :class:`MoneyboxResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    moneybox_data: dict[str, Any] = await db_manager.update_moneybox(
        moneybox_id=moneybox_id,
        moneybox_data=moneybox_update_request.model_dump(exclude_unset=True),
    )
    return moneybox_data  # type: ignore


@moneybox_router.delete(
    "/{moneybox_id}",
    responses=DELETE_MONEYBOX_RESPONSES,
    status_code=status.HTTP_204_NO_CONTENT,  # set default status code to 204
)
async def delete_moneybox_endpoint(
    request: Request,
    moneybox_id: Annotated[
        int,
        Path(title="Moneybox ID", description="Moneybox ID to be deleted."),
    ],
) -> Response:
    """Endpoint for deleting moneybox by moneybox_id.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param moneybox_id: The moneybox ID to be deleted.
    :type moneybox_id: :class:`int`
    :return: The response object with the status code included.
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    await db_manager.delete_moneybox(
        moneybox_id=moneybox_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@moneybox_router.post(
    "/{moneybox_id}/deposit",
    response_model=MoneyboxResponse,
    responses=POST_MONEYBOX_DEPOSIT_RESPONSES,
)
async def post_moneybox_deposit_endpoint(
    request: Request,
    moneybox_id: Annotated[
        int, Path(title="Moneybox ID", description="Moneybox ID to be deposited.")
    ],
    deposit_transaction: Annotated[
        DepositTransactionRequest,
        Body(
            title="Deposit amount",
            description="The deposit transaction with amount to add to moneybox, has to be >=0.",
        ),
    ],
) -> MoneyboxResponse:
    """Endpoint to add amount to moneybox by moneybox_id (deposit).
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param moneybox_id: The moneybox ID to be deposited.
    :type moneybox_id: :class:`int`
    :param deposit_transaction: The data of the deposit.
    :type deposit_transaction: :class:`DepositTransactionRequest`
    :return: The updated moneybox data.
    :rtype: :class:`MoneyboxResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    moneybox_data: dict[str, Any] = await db_manager.add_amount(
        moneybox_id=moneybox_id,
        deposit_transaction_data=deposit_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    return moneybox_data  # type: ignore


@moneybox_router.post(
    "/{moneybox_id}/withdraw",
    response_model=MoneyboxResponse,
    responses=POST_MONEYBOX_WITHDRAW_RESPONSES,
)
async def post_moneybox_withdraw_endpoint(
    request: Request,
    moneybox_id: Annotated[
        int, Path(title="Moneybox ID", description="Moneybox ID to be withdrawn.")
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
    """Endpoint to sub balance from moneybox by moneybox_id (withdraw).
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param moneybox_id: The moneybox ID to be withdrawn.
    :type moneybox_id: :class:`int`
    :param withdraw_transaction: The data of the withdrawal.
    :type withdraw_transaction: :class:`WithdrawTransactionRequest`
    :return: The updated moneybox data.
    :rtype: :class:`MoneyboxResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    moneybox_data: dict[str, Any] = await db_manager.sub_amount(
        moneybox_id=moneybox_id,
        withdraw_transaction_data=withdraw_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )

    return moneybox_data  # type: ignore


@moneybox_router.post(
    "/{moneybox_id}/transfer",
    responses=POST_TRANSFER_MONEYBOX_RESPONSES,
    status_code=status.HTTP_204_NO_CONTENT,  # set default status code to 204
)
async def post_moneybox_transfer_endpoint(
    request: Request,
    moneybox_id: Annotated[
        int, Path(title="Moneybox ID", description="Moneybox ID to be transferred from.")
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
    """Endpoint to transfer a specified amount from `moneybox_id` to `to_moneybox_id`.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param moneybox_id: The moneybox ID where the specified amount shall be transferred from.
    :param transfer_transaction: The data of the transfer, including the moneybox id
        where the balance shall be transferred to.
    :return: The response object with the status code included.
    :rtype: :class:`Response`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    await db_manager.transfer_amount(
        from_moneybox_id=moneybox_id,
        transfer_transaction_data=transfer_transaction.model_dump(),
        transaction_type=TransactionType.DIRECT,
        transaction_trigger=TransactionTrigger.MANUALLY,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@moneybox_router.get(
    "/{moneybox_id}/transactions",
    response_model=TransactionLogsResponse,
    responses=GET_MONEYBOX_TRANSACTION_LOGS_RESPONSES,
)
async def get_moneybox_transaction_logs(
    request: Request,
    moneybox_id: Annotated[
        int,
        Path(
            title="Moneybox ID",
            description="Moneybox ID of the transactions to be retrieved.",
        ),
    ],
) -> TransactionLogsResponse | Response:
    """Endpoint for getting moneybox transaction logs.
    \f

    :param request: The current request object.
    :type request: :class:`Request`
    :param moneybox_id: The moneybox ID where the transaction logs shall
        be retrieved.
    :type moneybox_id: :class:`int`
    :return: The requested moneybox transaction logs.
    :rtype: :class:`TransactionLogsResponse`
    """

    db_manager: DBManager = cast(DBManager, request.app.state.db_manager)
    transaction_logs_data: list[dict[str, Any]] = await db_manager.get_transaction_logs(
        moneybox_id=moneybox_id,
    )

    if transaction_logs_data:
        return {"transaction_logs": transaction_logs_data}  # type: ignore

    return Response(status_code=status.HTTP_204_NO_CONTENT)
