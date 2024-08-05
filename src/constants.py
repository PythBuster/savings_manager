"""All settings/global data are located here."""

from pathlib import Path

SPHINX_DIRECTORY = (Path(__file__).parent.parent / "docs" / "sphinx" / "build").resolve().absolute()
"""The current sphinx directory."""

WORKING_DIR = Path(__file__).parent.resolve().absolute()
"""The working directory."""
