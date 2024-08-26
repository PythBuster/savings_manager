"""The logger configuration"""

import logging

from src.constants import WORKING_DIR

logging.basicConfig(
    filename=WORKING_DIR.parent / "errors.log",
    filemode="a",  # Use "a" to append to the log file instead of overwriting
    level=logging.ERROR,
    format="\r\n%(asctime)s: %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
)

# Get the global logger instance
logger = logging.getLogger()
