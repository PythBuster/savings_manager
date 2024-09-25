"""All settings/global data are located here."""

from pathlib import Path

SPHINX_DIR_PATH: Path = (Path(__file__).parent.parent / "docs" / "sphinx" / "build").resolve()
"""The current sphinx directory."""

WEB_UI_DIR_PATH: Path = (Path(__file__).parent.parent / "static").resolve()
"""The current web ui directory."""

WORKING_DIR_PATH: Path = Path(__file__).parent.resolve()
"""The working directory."""

PGPASS_FILE_PATH: Path = (WORKING_DIR_PATH.parent / "temp" / ".pgpass").resolve()
