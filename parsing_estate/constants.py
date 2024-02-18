import os
import datetime
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


PATTERN_VALID_MAIL = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$'
ID_ROOMS = {
    '0': '5695', 
    '1': '5696',
    '2': '5697', 
    '3': '5698', 
    '4': '5699',
    '5': '5700',
    '6': '414718', 
}
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
FILE_OUTPUT_DIR_PATH = 'results'
BASE_DIR = Path(__file__).parent
LOG_FILE_DIR = os.path.join(Path(__file__).parent.parent, 'program.log')
TEGELGRAM_TOKEN = os.getenv('TG_TOKEN')
INPUT_MAIL = 0
INPUT_LOCATION = 0
INPUT_ALLREADY_EXISTS = 0
MONTH_NAMES_CYRILLIC_TO_LATIN = {
    "январь": "January",
    "февраль": "February",
    "март": "March",
    "апрель": "April",
    "май": "May",
    "июнь": "June",
    "июль": "July",
    "август": "August",
    "сентябрь": "September",
    "октябрь": "October",
    "ноябрь": "November",
    "декабрь": "December"
}
TRANSFORM_INPUT_DATA = {
    'area': {
        '0': 'avito.ru',
        '1': 'cian',
    },
    'rooms_count': {
        '0': 'апартаменты',
        '1': '1 комната',
        '2': '2 комнаты',
        '3': '3 комнаты',
        '4': '4 комнаты',
        '5': '5 и более комнат',
        '6': 'свободная планировка',
    },
    'send_parsing_file': {
        '0': 'mail',
        '1': 'chat_bot',
    },
}
CONFIG = {
        'area': 'not specified',
        'rooms_count': 'not specified',
        'location': 'all/',
        'already_exists': datetime.datetime(1999, 1, 1, 12, 0, 0),
        'send_parsing_file': ['not specified'],
        'accepted_mail': 'not specified',
    }