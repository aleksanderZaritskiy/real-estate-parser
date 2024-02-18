import logging
from typing import NoReturn
import sys

from .constants import LOG_FILE_DIR


def start_logging_config() -> NoReturn:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler(LOG_FILE_DIR, encoding='UTF-8'),
            logging.StreamHandler(sys.stdout),
        ],
    )   