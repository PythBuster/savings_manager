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
    _: Request,
    exc_class_or_status_code: int | Exception,
) -> JSONResponse | FileResponse:
    """Maps `ex_class_or_status_code` to a :class:`JSONResponse` or
    :class:`FileResponse` and returns it.

    :param _: The current request instance, not used.
    :type _: :class:`Starlette.request.Request`
    :param exc_class_or_status_code: The caught exception.
    :type exc_class_or_status_code: :class:`int` | :class:`Exception`
    :return: The exception as a json response.
    :rtype: :class:`JSONResponse` | :class:
    """

    # DO NOT LOG PASSWORDS!
    # TODO: check exception (message?) if contains string like "userPassword"...
    if isinstance(exc_class_or_status_code, Exception):
        app_logger.exception(exc_class_or_status_code)
    else:
        app_logger.error(
            f"Response-Exception-Handler - got status_code: {exc_class_or_status_code}"
        )

    if exc_class_or_status_code is status.HTTP_404_NOT_FOUND:
        return FileResponse(WEB_UI_DIR_PATH / "index.html", media_type="text/html")

    if isinstance(exc_class_or_status_code, MissingTokenError):
        return JSONResponse(
            status_code=exc_class_or_status_code.status_code,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exc_class_or_status_code.message,
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exc_class_or_status_code, MissingRoleError):
        message: str = exc_class_or_status_code.message
        return JSONResponse(
            status_code=exc_class_or_status_code.status_code,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=message,
                ).model_dump(exclude_none=True)
            ),
        )

    if issubclass(exc_class_or_status_code.__class__, AuthJWTException):
        if "Signature has expired" in exc_class_or_status_code.message:  # type: ignore
            status_code = status.HTTP_401_UNAUTHORIZED
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exc_class_or_status_code.message,  # type: ignore
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exc_class_or_status_code, BadUsernameOrPasswordError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exc_class_or_status_code.message,
                    details={"user_name": exc_class_or_status_code.user_name},
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exc_class_or_status_code, InconsistentDatabaseError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exc_class_or_status_code.message,
                    details=exc_class_or_status_code.details,
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exc_class_or_status_code, ConnectionRefusedError):
        _, arg_2 = exc_class_or_status_code.args

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message="No database connection.",  # type: ignore
                    details={"message": arg_2},  # type: ignore
                ).model_dump(exclude_none=True)
            ),
        )

    if issubclass(exc_class_or_status_code.__class__, RecordNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exc_class_or_status_code.message,  # type: ignore
                    details=exc_class_or_status_code.details,  # type: ignore
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exc_class_or_status_code, OverflowMoneyboxDeleteError):
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exc_class_or_status_code.message,  # type: ignore
                    details=exc_class_or_status_code.details,  # type: ignore
                ).model_dump(exclude_none=True)
            ),
        )

    if issubclass(exc_class_or_status_code.__class__, CrudDatabaseError):
        error_message: str = exc_class_or_status_code.message  # type: ignore

        if "error" in exc_class_or_status_code.details:  # type: ignore
            db_violation: DBViolationErrorType = await extract_database_violation_error(
                exc_class_or_status_code.details["error"]  # type: ignore
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
                    details=exc_class_or_status_code.details,  # type: ignore
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exc_class_or_status_code, sqlalchemy.exc.IntegrityError):
        # NOTE: This IntegrityError parsing assumes PostgreSQL's error message format.
        #       It will raise if used with other SQL dialects.
        error_message = exc_class_or_status_code.args[0]
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
                        "params": exc_class_or_status_code.params,
                        "detail": detail.strip(),
                    },  # type: ignore
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exc_class_or_status_code, MissingSMTPSettingsError):
        error_message = exc_class_or_status_code.args[0]

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=error_message,
                ).model_dump(exclude_none=True)
            ),
        )

    if issubclass(exc_class_or_status_code.__class__, SMTPException):
        smtp_base_exception: SMTPException = cast(
            SMTPException,
            exc_class_or_status_code,
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

    if isinstance(
        exc_class_or_status_code, (RequestValidationError, ResponseValidationError, ValidationError)
    ):
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
                            for error in exc_class_or_status_code.errors()
                        ],
                    },
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exc_class_or_status_code, RateLimitExceeded):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message="Rate limit exceeded",
                    details={"limit": exc_class_or_status_code.detail},
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exc_class_or_status_code, InvalidFileError):
        error_message = exc_class_or_status_code.message
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=error_message,
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exc_class_or_status_code, MissingDependencyError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exc_class_or_status_code.message,
                ).model_dump(exclude_none=True)
            ),
        )

    if isinstance(exc_class_or_status_code, ProcessCommunicationError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exc_class_or_status_code.message,
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
                    "exception": exc_class_or_status_code.__class__.__name__,
                    "args": cast(Exception, exc_class_or_status_code).args,
                },
            ).model_dump(exclude_none=True)
        ),
    )
