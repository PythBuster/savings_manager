"""All exception_handler logic are located here."""

import logging

from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from src.data_classes.responses import HTTPErrorResponse
from src.db.exceptions import RecordNotFoundError


async def response_exception(exception: Exception) -> JSONResponse:
    """Maps got `exception` to a :class:`JSONResponse` and returns it.

    :param exception: The caught exception.
    :type exception: :class:`Exception`
    :return: The exception as a json response.
    :rtype: :class:`JSONResponse`
    """

    if issubclass(exception.__class__, RecordNotFoundError):
        return JSONResponse(
            content=jsonable_encoder(
                HTTPErrorResponse(
                    message=exception.message,  # type: ignore
                    detail=exception.details,  # type: ignore
                )
            ),
            status_code=status.HTTP_404_NOT_FOUND,
        )

    logging.exception(exception)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content="Unknown server error",
    )
