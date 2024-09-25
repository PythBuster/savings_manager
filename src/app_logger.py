"""The logger configuration"""

import logging

from src.constants import WORKING_DIR_PATH

# Create and configure the app logger
app_logger: logging.Logger = logging.getLogger("app")
"""The global app logger"""

# Configure the logger
handler: logging.FileHandler = logging.FileHandler(
    filename=WORKING_DIR_PATH.parent / "errors.log",
    mode="a",
)
"""The log file handler"""

formatter: logging.Formatter = logging.Formatter(
    fmt="\r\n%(asctime)s: %(message)s", datefmt="%d.%m.%Y %H:%M:%S"
)
"""The log formatter"""

handler.setFormatter(formatter)
handler.setLevel(logging.ERROR)

# Add the handler to the logger
app_logger.addHandler(handler)
app_logger.setLevel(logging.ERROR)
