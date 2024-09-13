"""All settings/global data are located here."""

from pathlib import Path

SPHINX_DIRECTORY = (Path(__file__).parent.parent / "docs" / "sphinx" / "build").resolve()
"""The current sphinx directory."""

WEB_UI_DIRECTORY = (Path(__file__).parent.parent / "static").resolve()
"""The current web ui directory."""

WORKING_DIR = Path(__file__).parent.resolve()
"""The working directory."""
