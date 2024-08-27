"""The logger configuration"""

import logging

from src.constants import WORKING_DIR

# Create and configure the app logger
app_logger = logging.getLogger("app")

# Configure the logger
handler = logging.FileHandler(WORKING_DIR.parent / "errors.log", mode="a")
formatter = logging.Formatter("\r\n%(asctime)s: %(message)s", datefmt="%d.%m.%Y %H:%M:%S")
handler.setFormatter(formatter)
handler.setLevel(logging.ERROR)

# Add the handler to the logger
app_logger.addHandler(handler)
app_logger.setLevel(logging.ERROR)
