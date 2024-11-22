"""The JWT classes and functions are located here."""

from asyncio import Lock
from typing import Annotated, Any

from async_fastapi_jwt_auth.auth_jwt import AuthJWT
from fastapi.security import HTTPBearer as SecurityHTTPBearer
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import Response

from src.auth.exceptions import MissingRoleError
from src.custom_types import EndpointRouteType, UserRoleType
from src.utils import get_app_data, get_app_env_variables

APP_DATA: dict[str, Any] = get_app_data()
APP_MAJOR_VERSION: int = int(APP_DATA["version"].split(".")[0])
LOGIN_REQUEST_PATH: str = f"/{EndpointRouteType.APP_ROOT}/{EndpointRouteType.APP}/login"


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


class UserAuthJWTBearer(SecurityHTTPBearer):  # pylint: disable=too-few-public-methods
    """Custom implementation of class `async_fastapi_jwt_auth.auth_jwt.AuthJWTBearer`.

    This ensures the JWT configuration is loaded with correct settings.

    The official documentations is using a decorator for config loading approach.
    But we will build an import order dependency, which is corralled with load_dotenv in main.

    Before configuration of AuthJWT, the env var `ENVIRONMENT`need to be loaded from .env.general.
    """

    _config_loaded: bool = False
    _lock: Lock = Lock()

    def __init__(self, access_limited_to_roles: list[UserRoleType] | None = None):
        self.access_limited_to_roles: list[UserRoleType] | None = access_limited_to_roles
        super().__init__()

    async def __call__(
        self,
        req: Request = None,
        res: Response = None,
    ) -> AuthJWT:
        """Returns the AuthJWT."""

        if not UserAuthJWTBearer._config_loaded:
            async with UserAuthJWTBearer._lock:
                if not UserAuthJWTBearer._config_loaded:
                    UserAuthJWTBearer._load_jwt_config()
                    UserAuthJWTBearer._config_loaded = True

        auth_jwt = AuthJWT(req=req, res=res)

        if APP_MAJOR_VERSION >= 3:
            if req.scope["path"] != LOGIN_REQUEST_PATH:
                await auth_jwt.jwt_required()

                if self.access_limited_to_roles is not None:
                    jwt_dict: dict[str, Any] = await auth_jwt.get_raw_jwt()
                    user_role: UserRoleType = UserRoleType(jwt_dict["role"])

                    if user_role not in self.access_limited_to_roles:
                        raise MissingRoleError(
                            status_code=403, message="Not authorized. Missing role."
                        )

        return auth_jwt

    @staticmethod
    def _load_jwt_config() -> None:
        """Internal method to configure the AuthJWT with custom settings."""

        print("Load AuthJWT Configuration...", flush=True)
        AuthJWT.load_config(UserAuthJWTBearer._get_jwt_config)  # type: ignore

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
