import datetime as dt
import logging
from typing import Tuple, NoReturn
import csv

from .constants import BASE_DIR, FILE_OUTPUT_DIR_PATH, DATETIME_FORMAT


def file_output(result: Tuple[str], parsing_area: str) -> NoReturn:
    results_dir = BASE_DIR / FILE_OUTPUT_DIR_PATH
    results_dir.mkdir(exist_ok=True)
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parsing_area}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as file:
        writter = csv.writer(
            file, dialect='unix', quotechar='"', quoting=csv.QUOTE_MINIMAL,
        )
        writter.writerows(result)
    logging.info('Файл с парсингом успешно добавлен')


def send_email() -> NoReturn:
    pass