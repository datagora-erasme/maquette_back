from app.config import config as app_config
from app import app
from loguru import logger
import logging
import os

# Import utils
from app.utils.methods import *


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Retrieve context where the logging call occurred, this happens to be
        # in the 6th frame upward
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


# Events Logs

logger.add(
    "logs/info.log",
    level="DEBUG",
    format="{time} {level} {message}",
    backtrace=True,
    rotation="1 day",
    retention="2 weeks",
)

# Warn logs

logger.add(
    "logs/warnings.log",
    level="WARNING",
    format="{time} {level} {message}",
    backtrace=True,
    rotation="1 day",
    retention="2 weeks",
)

app.logger.addHandler(InterceptHandler())
logging.basicConfig(handlers=[InterceptHandler()], level=20)

# Launch (main)
if __name__ == "__main__":
    ENV = get_environment()
    app.run(host=app_config[ENV].HOST, port=app_config[ENV].PORT)
