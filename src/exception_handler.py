"""All exception_handler logic are located here."""

import logging

import sqlalchemy
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from src.data_classes.responses import HTTPErrorResponse
from src.db.exceptions import (
    DeleteInstanceError,
    RecordNotFoundError,
    UpdateInstanceError,
    InconsistentDatabaseError,
)


async def response_exception(exception: Exception) -> JSONResponse:
    """Maps `exception` to a :class:`JSONResponse` and returns it.

    :param exception: The caught exception.
    :type exception: :class:`Exception`
    :return: The exception as a json response.
    :rtype: :class:`JSONResponse`
    """

    if isinstance(exception, InconsistentDatabaseError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,
                    details=exception.details,
                )
            ),
        )

    if isinstance(exception, ConnectionRefusedError):
        _, arg_2 = exception.args

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message="No database connection.",  # type: ignore
                    details={"message": arg_2},  # type: ignore
                )
            ),
        )

    if issubclass(exception.__class__, RecordNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,  # type: ignore
                    details=exception.details,  # type: ignore
                )
            ),
        )

    if issubclass(exception.__class__, UpdateInstanceError):
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,  # type: ignore
                    details=exception.details,  # type: ignore
                )
            ),
        )

    if issubclass(exception.__class__, DeleteInstanceError):
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,  # type: ignore
                    details=exception.details,  # type: ignore
                )
            ),
        )

    if isinstance(exception, sqlalchemy.exc.IntegrityError):
        error_message = exception.args[0]
        error_parts = error_message.split(":")
        exception_type, message, *detail = error_parts
        detail = "".join(detail)

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=message.replace("\nDETAIL", "").strip(),  # type: ignore
                    details={
                        "exception": exception_type.strip(),
                        "params": exception.params,
                        "detail": detail.strip(),
                    },  # type: ignore
                )
            ),
        )

    logging.exception(exception)

    # fastapi will catch any unhandled exception and will
    # map it to a 500 Internal Server Error response
    raise exception
