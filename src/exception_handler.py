"""All exception_handler logic are located here."""

import sqlalchemy
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from slowapi.errors import RateLimitExceeded
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.app_logger import app_logger
from src.data_classes.responses import HTTPErrorResponse
from src.db.exceptions import (
    CrudDatabaseError,
    InconsistentDatabaseError,
    InvalidFileError,
    RecordNotFoundError,
)
from src.routes.exceptions import MissingSMTPSettingsError


async def response_exception(  # pylint: disable=too-many-return-statements, too-many-branches
    _: Request,
    exception: Exception,
) -> JSONResponse:
    """Maps `exception` to a :class:`JSONResponse` and returns it.

    :param _: The current request instance, not used.
    :type _: :class:`Starlette.request.Request`
    :param exception: The caught exception.
    :type exception: :class:`Exception`
    :return: The exception as a json response.
    :rtype: :class:`JSONResponse`
    """

    app_logger.exception(exception)

    if isinstance(exception, AuthJWTException):
        if "Signature has expired" in exception.message:
            status_code = status.HTTP_401_UNAUTHORIZED
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,
                )
            ),
        )

    if isinstance(exception, InconsistentDatabaseError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message="No database connection.",  # type: ignore
                    details={"message": arg_2},  # type: ignore
                )
            ),
        )

    if issubclass(exception.__class__, RecordNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,  # type: ignore
                    details=exception.details,  # type: ignore
                )
            ),
        )

    if issubclass(exception.__class__, CrudDatabaseError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,  # type: ignore
                    details=exception.details,  # type: ignore
                )
            ),
        )

    if isinstance(exception, sqlalchemy.exc.IntegrityError):
        error_message: str = exception.args[0]
        error_parts: list[str] = error_message.split(":")
        exception_type, message, *details = error_parts
        detail: str = "".join(details)

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
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

    if isinstance(exception, MissingSMTPSettingsError):
        error_message = exception.args[0]

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=error_message,
                )
            ),
        )

    if isinstance(exception, RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message="Invalid request data",
                    details={
                        "args": exception.args,
                        "body": exception.body,
                    },
                )
            ),
        )

    if isinstance(exception, ResponseValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message="Invalid response data",
                    details={
                        "args": exception.args,
                        "body": exception.body,
                    },
                )
            ),
        )

    if isinstance(exception, RateLimitExceeded):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message="Rate limit exceeded",
                    details={"limit": exception.detail},
                )
            ),
        )

    if isinstance(exception, InvalidFileError):
        message = exception.message
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=message,
                )
            ),
        )

    # all other unmapped exceptions
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            HTTPErrorResponse(
                message="Unknown Error",
                details={
                    "exception": exception.__class__.__name__,
                    "args": exception.args,
                },
            )
        ),
    )
