import pytest
from aiosmtplib import SMTPException
from async_fastapi_jwt_auth.exceptions import (
    AccessTokenRequired,
    MissingTokenError,
    RefreshTokenRequired,
    RevokedTokenError,
)
from fastapi.exceptions import RequestValidationError
from limits import RateLimitItemPerMinute
from pydantic import BaseModel, Field, ValidationError
from slowapi.errors import RateLimitExceeded
from slowapi.wrappers import Limit
from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, JSONResponse

from src.auth.exceptions import MissingRoleError
from src.custom_types import DBViolationErrorType
from src.db.exceptions import (
    CrudDatabaseError,
    InconsistentDatabaseError,
    InvalidFileError,
    MissingDependencyError,
    OverflowMoneyboxDeleteError,
    ProcessCommunicationError,
    RecordNotFoundError,
)
from src.exception_handler import response_exception
from src.routes.exceptions import BadUsernameOrPasswordError, MissingSMTPSettingsError


@pytest.mark.asyncio
async def test_404_returns_file_response(monkeypatch):
    fake_path = "/fake/index.html"

    class DummyFileResponse(FileResponse):
        def __init__(self, *a, **kw):
            super().__init__(fake_path, media_type="text/html")

    monkeypatch.setattr("src.exception_handler.FileResponse", DummyFileResponse)
    monkeypatch.setattr("src.constants.WEB_UI_DIR_PATH", "/fake")

    result = await response_exception(None, HTTPException(status_code=status.HTTP_404_NOT_FOUND))
    assert isinstance(result, FileResponse)
    assert result.path.endswith("index.html")
    assert result.media_type == "text/html"


# ---------------------------------------------------------------------------
# Auth / JWT / Role related Exceptions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_missing_token_error_maps_correctly():
    exc = MissingTokenError(status_code=status.HTTP_401_UNAUTHORIZED, message="Token missing")
    result = await response_exception(None, exc)
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token missing" in result.body.decode()


@pytest.mark.asyncio
async def test_revoked_token_error_maps_to_400():
    exc = RevokedTokenError(status_code=status.HTTP_400_BAD_REQUEST, message="Token revoked")
    result = await response_exception(None, exc)
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert "revoked" in result.body.decode()


@pytest.mark.asyncio
async def test_access_token_required_maps_to_400():
    exc = AccessTokenRequired(
        status_code=status.HTTP_400_BAD_REQUEST, message="Access token required"
    )
    result = await response_exception(None, exc)
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert "Access token" in result.body.decode()


@pytest.mark.asyncio
async def test_refresh_token_required_maps_to_400():
    exc = RefreshTokenRequired(
        status_code=status.HTTP_400_BAD_REQUEST, message="Refresh token required"
    )
    result = await response_exception(None, exc)
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert "Refresh token" in result.body.decode()


@pytest.mark.asyncio
async def test_access_token_expired_signature_maps_to_401():
    """AuthJWTException (expired signature) → 401."""
    # Wir verwenden eine konkrete Unterklasse, wie sie async-fastapi-jwt-auth werfen würde.
    exc = AccessTokenRequired(
        status_code=status.HTTP_401_UNAUTHORIZED, message="Signature has expired"
    )

    result = await response_exception(None, exc)

    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    body = result.body.decode()
    assert "Signature has expired" in body


@pytest.mark.asyncio
async def test_missing_role_error_maps_to_status():
    exc = MissingRoleError(message="Missing required role", status_code=status.HTTP_403_FORBIDDEN)
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_403_FORBIDDEN
    assert "Missing required role" in result.body.decode()


@pytest.mark.asyncio
async def test_bad_username_or_password_error():
    exc = BadUsernameOrPasswordError(user_name="john")
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    body = result.body.decode()
    assert "john" in body


# ---------------------------------------------------------------------------
# Database related Exceptions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_connection_refused_error():
    exc = ConnectionRefusedError("db", "connection lost")
    result = await response_exception(None, exc)
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    body = result.body.decode()
    assert "No database connection" in body
    assert "connection lost" in body


@pytest.mark.asyncio
async def test_integrity_error_postgres_format():
    pg_message = (
        "psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "
        '"users_email_key": DETAIL: Key (email)=(test@example.com) already exists.'
    )
    statement = "INSERT INTO users (email) VALUES (%(email)s)"
    params = {"email": "test@example.com"}
    orig = Exception(pg_message)
    exc = IntegrityError(statement=statement, params=params, orig=orig)
    exc.args = (str(orig), statement, params)
    result = await response_exception(None, exc)
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    body = result.body.decode()
    assert "duplicate key value violates unique constraint" in body
    assert "users_email_key" in body
    assert "email" in body
    assert "IntegrityError" in body or "UniqueViolation" in body


@pytest.mark.asyncio
async def test_inconsistent_database_error():
    exc = InconsistentDatabaseError("Conflict in data", details={"foo": "bar"})
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_409_CONFLICT
    assert "Conflict" in result.body.decode()


@pytest.mark.asyncio
async def test_record_not_found_error():
    exc = RecordNotFoundError(record_id=1, message="Item not found", details={"id": 1})
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert "Item not found" in result.body.decode()


@pytest.mark.asyncio
async def test_overflow_moneybox_delete_error():
    exc = OverflowMoneyboxDeleteError(moneybox_id=99)
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "It is not allowed to delete the Overflow Moneybox!" in result.body.decode()


@pytest.mark.asyncio
async def test_crud_database_error_with_violation(monkeypatch):
    async def fake_extract(_):
        return DBViolationErrorType.SET_REPORTS_VIA_EMAIL_BUT_NO_EMAIL_ADDRESS

    monkeypatch.setattr("src.exception_handler.extract_database_violation_error", fake_extract)
    exc = CrudDatabaseError(record_id=1, message="DB violation", details={"error": "dummy"})
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_409_CONFLICT
    assert "Email reports can't be activated" in result.body.decode()


@pytest.mark.asyncio
async def test_crud_database_error_with_unknown_violation(monkeypatch):
    """CrudDatabaseError → DBViolationErrorType.UNKNOWN raises ValueError."""

    async def fake_extract(_):
        return DBViolationErrorType.UNKNOWN

    monkeypatch.setattr("src.exception_handler.extract_database_violation_error", fake_extract)

    exc = CrudDatabaseError(record_id=1, message="DB violation", details={"error": "dummy"})

    with pytest.raises(ValueError) as err:
        await response_exception(None, exc)

    assert "Not allowed state" in str(err.value)
    assert "DBViolationErrorType.UNKNOWN" in str(err.value)


# ---------------------------------------------------------------------------
# Validation and Rate-Limit exceptions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_request_validation_error():
    exc = RequestValidationError(
        errors=[{"type": "value_error", "msg": "invalid value", "loc": ("body", "age")}]
    )
    result = await response_exception(None, exc)
    assert isinstance(result, JSONResponse)
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    body = result.body.decode()
    assert "Validation Error" in body
    assert "age" in body
    assert "invalid" in body


@pytest.mark.asyncio
async def test_pydantic_validation_error():
    class Model(BaseModel):
        x: int = Field(..., ge=0)

    try:
        Model(x=-1)
    except ValidationError as exc:
        result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    body = result.body.decode()
    assert "Validation Error" in body
    assert "x" in body
    assert "greater than or equal to 0" in body


@pytest.mark.asyncio
async def test_rate_limit_exceeded():
    limit_item = RateLimitItemPerMinute(5)
    limit = Limit(
        limit=limit_item,
        key_func=lambda *a, **kw: "test-key",
        scope="test-scope",
        per_method=False,
        methods=None,
        error_message="Too many requests",
        exempt_when=None,
        cost=1,
        override_defaults=False,
    )
    exc = RateLimitExceeded(limit)
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    body = result.body.decode()
    assert "Rate limit" in body
    assert "Too many" in body


# ---------------------------------------------------------------------------
# SMTP, File, Dependency, Process related Exceptions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_missing_smtp_settings_error():
    exc = MissingSMTPSettingsError()
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "SMTP settings incomplete." in result.body.decode()


@pytest.mark.asyncio
async def test_smtp_exception_maps_to_409():
    exc = SMTPException("Mailbox full")
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_409_CONFLICT
    assert "Mailbox full" in result.body.decode()


@pytest.mark.asyncio
async def test_invalid_file_error():
    exc = InvalidFileError("File corrupt")
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert "File corrupt" in result.body.decode()


@pytest.mark.asyncio
async def test_missing_dependency_error():
    exc = MissingDependencyError("Dependency missing")
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Dependency missing" in result.body.decode()


@pytest.mark.asyncio
async def test_process_communication_error():
    exc = ProcessCommunicationError("Process error")
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Process error" in result.body.decode()


# ---------------------------------------------------------------------------
# Generic / unmapped exceptions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_http_exception_falls_back_to_unknown_error():
    exc = HTTPException(status_code=418, detail="I'm a teapot")
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    body = result.body.decode()
    assert "Unknown Error" in body
    assert "HTTPException" in body


@pytest.mark.asyncio
async def test_unknown_exception_fallback():
    class SomeWeirdError(Exception):
        pass

    exc = SomeWeirdError("Something odd")
    result = await response_exception(None, exc)
    assert result.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    body = result.body.decode()
    assert "Unknown Error" in body
    assert "SomeWeirdError" in body
    assert "Something odd" in body
