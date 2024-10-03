"""The JWT classes and functions are located here."""

from typing import Annotated

from async_fastapi_jwt_auth.auth_jwt import AuthJWT, AuthJWTBearer
from pydantic import BaseModel, Field

from src.custom_types import AppEnvVariables
from src.utils import get_app_env_variables

auth_dep = AuthJWTBearer()


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


@AuthJWT.load_config
def get_config() -> JWTSettings:
    """Get config helper for AuthJWT.

    :return: JWT settings
    :rtype: :class:`JWTSettings`
    """

    app_env_variables: AppEnvVariables = get_app_env_variables()
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
