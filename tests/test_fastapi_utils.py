import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.custom_types import AppEnvVariables
from src.fastapi_utils import create_pgpass

@pytest.mark.dependency(
    depends=["tests/test_db_manager.py::test_reset_database_delete_app_settings"],
    scope="session",
)
def test_create_pgpass(app_env_variables: AppEnvVariables) -> None:
    TEST_PGPASS_FILE_PATH = (
        (Path(__file__).parent / "temp" / ".pgpass").resolve()
    )

    with patch(
        "src.fastapi_utils.PGPASS_FILE_PATH",
        new=TEST_PGPASS_FILE_PATH,
    ):
        create_pgpass(app_env_variables=app_env_variables)

        file_permissions = oct(
            TEST_PGPASS_FILE_PATH.stat().st_mode
        )[-3:]

        assert file_permissions == '600'
        assert os.getenv("PGPASSFILE") == str(TEST_PGPASS_FILE_PATH)
