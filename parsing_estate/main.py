import os
import glob
import logging
from typing import NoReturn

from multiprocessing import Process, Queue
from dotenv import load_dotenv

from .constants import (
    ID_ROOMS,
    PORT,
    SENDER_EMAIL,
    SEND_PASSWORD,
    SUBJECT,
    SMPT_SERVER,
    BODY,
    BASE_DIR,
    FILE_OUTPUT_DIR_PATH,
)
from .tg_bot import tg_bot
from .logging_config import start_logging_config
from .parser_estate import get_url_with_input_params_avito
from .outputs import file_output, send_email
from .exceptions import UnConnectedError

load_dotenv()


def main() -> NoReturn:
    queue = Queue()
    process_tg = Process(target=tg_bot, args=(queue,))
    process_tg.start()
    try:
        while True:
            if not queue.empty():
                input_user_data = queue.get()
                if isinstance(input_user_data, dict):
                    logging.info(f'Передан запрос на парсинг')
                    id_rooms = [ID_ROOMS[id] for id in input_user_data["rooms_count"]]
                    result = get_url_with_input_params_avito(
                        search_place=input_user_data["location"],
                        id_rooms=id_rooms,
                        already_exists=input_user_data["already_exists"],
                    )
                    file_output(result, 'avito.ru')
                    files = glob.glob(os.path.join(BASE_DIR / FILE_OUTPUT_DIR_PATH, '*'))
                    latest_file = max(files, key=os.path.getctime)
                    logging.info(f'данные собраны в {latest_file}')
                    if '0' in input_user_data["send_parsing_file"]:
                        mail = input_user_data['mail']
                        # Получаем крайний файл в папке результатов
                        send_email(
                            SMPT_SERVER,
                            PORT,
                            SENDER_EMAIL,
                            SEND_PASSWORD,
                            mail,
                            SUBJECT,
                            BODY,
                            latest_file,
                        )
                        logging.info(f'данные отправлены на {mail}')
    except UnConnectedError:
        logging.info('Разрыв, перезапуск мэйн')
        main()


if __name__ == '__main__':
    start_logging_config()
    main()
