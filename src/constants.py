"""All settings/global data are located here."""

from pathlib import Path

from src.custom_types import EnvironmentType

SPHINX_DIR_PATH: Path = (Path(__file__).parent.parent / "docs" / "sphinx" / "build").resolve()
"""The current sphinx directory."""

WEB_UI_DIR_PATH: Path = (Path(__file__).parent.parent / "static").resolve()
"""The current web ui directory."""

WORKING_DIR_PATH: Path = Path(__file__).parent.resolve()
"""The working directory."""

PGPASS_FILE_PATH: Path = (WORKING_DIR_PATH.parent / "temp" / ".pgpass").resolve()
"""The path to the PGPASS file."""

ENVIRONMENT_ENV_FILE_PATHS: dict[EnvironmentType, Path] = {
    EnvironmentType.TEST: WORKING_DIR_PATH.parent / "envs" / ".env.test",
    EnvironmentType.DEV: WORKING_DIR_PATH.parent / "envs" / ".env.dev",
    # EnvironmentType.PROD: WORKING_DIR_PATH.parent / "envs" / ".env.prod",
}
"""The ENVIRONMENT env file paths."""

GENERAL_ENV_FILE_PATH: Path = WORKING_DIR_PATH.parent / "envs" / ".env.general"
"""The general env file paths. Directly loaded on main module."""

SENDER_DIR_PATH: Path = Path(__file__).parent
"""The sender directory path."""