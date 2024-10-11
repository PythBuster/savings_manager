"""All auth related exceptions are located here."""

from async_fastapi_jwt_auth.exceptions import AuthJWTException


class MissingRoleError(AuthJWTException):
    """Custom MissingRole Error"""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
