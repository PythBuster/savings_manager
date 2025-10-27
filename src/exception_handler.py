"""All exception_handler logic are located here."""

from typing import cast

import sqlalchemy
from aiosmtplib import SMTPException
from async_fastapi_jwt_auth.exceptions import AuthJWTException, MissingTokenError
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic import ValidationError
from slowapi.errors import RateLimitExceeded
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse

from src.app_logger import app_logger
from src.auth.exceptions import MissingRoleError
from src.constants import WEB_UI_DIR_PATH
from src.custom_types import DBViolationErrorType
from src.data_classes.responses import HTTPErrorResponse
from src.db.exceptions import (
    CrudDatabaseError,
    InconsistentDatabaseError,
    InvalidFileError,
    MissingDependencyError,
    OverflowMoneyboxDeleteError,
    ProcessCommunicationError,
    RecordNotFoundError,
)
from src.routes.exceptions import BadUsernameOrPasswordError, MissingSMTPSettingsError
from src.utils import extract_database_violation_error


async def response_exception(  # pylint: disable=too-many-return-statements, too-many-branches
    request: Request,
    exception: Exception,
) -> JSONResponse | FileResponse:
    """Maps `exception` to a :class:`JSONResponse` or
    :class:`FileResponse` and returns it.

    :param request: The current request instance.
    :type request: :class:`Starlette.request.Request`
    :param exception: The caught exception.
    :type exception: :class:`int` | :class:`Exception`
    :return: The exception as a json response.
    :rtype: :class:`JSONResponse` | :class:`FileResponse`
    """

    # DO NOT LOG PASSWORDS!
    # TODO: check exception (message?) if contains string like "userPassword"...
    app_logger.exception(exception)

    if isinstance(exception, HTTPException) and exception.status_code == status.HTTP_404_NOT_FOUND:
        if request.url.path.startswith("/api") or request.url.path.endswith((".js", ".css", ".png", ".jpg", ".ico")):
            return JSONResponse(
                status_code=404,
                content={"detail": "Not Found"},
            )
        return FileResponse(WEB_UI_DIR_PATH / "index.html", media_type="text/html")

    if isinstance(exception, MissingTokenError):
        return JSONResponse(
            status_code=exception.status_code,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exception, MissingRoleError):
        message: str = exception.message
        return JSONResponse(
            status_code=exception.status_code,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=message,
                ).model_dump(exclude_none=True)
            ),
        )

    if issubclass(exception.__class__, AuthJWTException):
        if "Signature has expired" in exception.message:  # type: ignore
            status_code = status.HTTP_401_UNAUTHORIZED
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,  # type: ignore
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exception, BadUsernameOrPasswordError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,
                    details={"user_name": exception.user_name},
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exception, InconsistentDatabaseError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,
                    details=exception.details,
                ).model_dump(exclude_none=True)
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
                ).model_dump(exclude_none=True)
            ),
        )

    if issubclass(exception.__class__, RecordNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,  # type: ignore
                    details=exception.details,  # type: ignore
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exception, OverflowMoneyboxDeleteError):
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,  # type: ignore
                    details=exception.details,  # type: ignore
                ).model_dump(exclude_none=True)
            ),
        )

    if issubclass(exception.__class__, CrudDatabaseError):
        error_message: str = exception.message  # type: ignore

        if "error" in exception.details:  # type: ignore
            db_violation: DBViolationErrorType = await extract_database_violation_error(
                exception.details["error"]  # type: ignore
            )

            match db_violation:
                case DBViolationErrorType.SET_REPORTS_VIA_EMAIL_BUT_NO_EMAIL_ADDRESS:
                    error_message = "Email reports can't be activated, no email address set."

                case DBViolationErrorType.UNKNOWN:
                    raise ValueError(f"Not allowed state: {db_violation=}")

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=error_message,  # type: ignore
                    details=exception.details,  # type: ignore
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exception, sqlalchemy.exc.IntegrityError):
        # NOTE: This IntegrityError parsing assumes PostgreSQL's error message format.
        #       It will raise if used with other SQL dialects.
        error_message = exception.args[0]
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
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exception, MissingSMTPSettingsError):
        error_message = exception.args[0]

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=error_message,
                ).model_dump(exclude_none=True)
            ),
        )

    if issubclass(exception.__class__, SMTPException):
        smtp_base_exception: SMTPException = cast(
            SMTPException,
            exception,
        )
        error_message = smtp_base_exception.message

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=error_message,
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exception, (RequestValidationError, ResponseValidationError, ValidationError)):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message="Validation Error",
                    details={
                        "errors": [
                            {
                                "type": error["type"],
                                "message": error["msg"],
                                "field": error["loc"][-1],
                            }
                            for error in exception.errors()
                        ],
                    },
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exception, RateLimitExceeded):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message="Rate limit exceeded",
                    details={"limit": exception.detail},
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exception, InvalidFileError):
        error_message = exception.message
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=error_message,
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exception, MissingDependencyError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exception, ProcessCommunicationError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,
                ).model_dump(exclude_none=True)
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
            ).model_dump(exclude_none=True)
        ),
    )
