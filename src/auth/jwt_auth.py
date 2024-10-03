"""The JWT classes and functions are located here."""
import os
from asyncio import Lock
from typing import Annotated

from async_fastapi_jwt_auth.auth_jwt import AuthJWT, AuthJWTBearer
from blib2to3.pgen2.parse import lam_sub
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import lambda_stmt

from src.custom_types import AppEnvVariables
from src.utils import get_app_env_variables


class JWTSettings(BaseModel):
    """The JWT settings model for"""

    authjwt_access_cookie_key: Annotated[
        str,
        Field(
            default="savings_manager",
            description="JWT Access Cookie Key",
        ),
    ]
    """JWT Access Cookie Key"""

    authjwt_secret_key: Annotated[
        str,
        Field(
            min_length=8,
            description="The JWT secret key",
        ),
    ]
    """The JWT secret key"""

    authjwt_cookie_secure: Annotated[
        bool,
        Field(
            default=True,
            description="Only allow JWT cookies to be sent over https",
        ),
    ]
    """Only allow JWT cookies to be sent over https"""

    authjwt_token_location: Annotated[
        set,
        Field(
            default="The JWT token location",
        ),
    ]
    """The JWT token location"""

    authjwt_cookie_csrf_protect: Annotated[
        bool,
        Field(
            default=True,
            description="Enable csrf double submit protection. default is True",
        ),
    ]
    """Enable csrf double submit protection. default is True"""

    authjwt_cookie_samesite: Annotated[
        str,
        Field(
            default=None,
            description=(
                "Change to 'lax' in production to make your website more secure "
                "from CSRF Attacks, default is None."
            ),
        ),
    ]
    """Change to 'lax' in production to make your website more secure
    from CSRF Attacks, default is None."""


class UserAuthJWTBearer:
    """Helper class to initialize and provide a singleton instance of AuthJWTBearer
    for FastAPI endpoints.

    This ensures the JWT configuration is loaded once, avoiding repeated initialization and
    enhancing performance. Since the JWT settings do not change during the app's runtime,
    reloading them is unnecessary.

    This acts as a workaround for the `async_fastapi_jwt_auth` package (which is enabling
    JWT authentication in FastAPI).
    """

    _auth_jwt_instance: AuthJWTBearer | None = None
    _lock: Lock = Lock()

    async def __call__(self) -> AuthJWTBearer:
        """Returns the singleton instance of AuthJWTBearer, initializing it if needed."""

        if UserAuthJWTBearer._auth_jwt_instance is None:
            async with UserAuthJWTBearer._lock:
                # check twice to avoid re-init from waiting task
                if UserAuthJWTBearer._auth_jwt_instance is None:
                    self._initialize_jwt()

        return UserAuthJWTBearer._auth_jwt_instance

    @staticmethod
    def _initialize_jwt() -> None:
        """Internal method to initialize the AuthJWTBearer and load configuration."""

        print("Initializing AuthJWTBearer...", flush=True)

        # Load the JWT configuration
        try:
            AuthJWT.load_config(lambda: UserAuthJWTBearer._get_jwt_config())  # type: ignore
            UserAuthJWTBearer._auth_jwt_instance = AuthJWTBearer()
        except Exception as e:
            print(f"Failed to initialize AuthJWTBearer: {e}", flush=True)
            raise e

    @staticmethod
    def _get_jwt_config() -> JWTSettings:
        """Retrieve the JWT configuration settings.

        :return: JWT settings
        :rtype: :class:`JWTSettings`
        """
        _, app_env_variables = get_app_env_variables()

        # Use fallback if the value is not set
        same_site_str = (
            app_env_variables.authjwt_cookie_samesite
            if app_env_variables.authjwt_cookie_samesite
            else "none"
        )

        return JWTSettings(
            authjwt_access_cookie_key="savings_manager",
            authjwt_secret_key=app_env_variables.authjwt_secret_key.get_secret_value(),
            authjwt_token_location={"cookies"},
            authjwt_cookie_secure=app_env_variables.authjwt_cookie_secure,
            authjwt_cookie_csrf_protect=app_env_variables.authjwt_cookie_csrf_protect,
            authjwt_cookie_samesite=same_site_str,
        )
