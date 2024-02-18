import logging
from typing import Type, NoReturn, Tuple, List, Dict

from multiprocessing import Process, Queue

from .constants import ID_ROOMS
from .tg_bot import tg_bot
from .logging_config import start_logging_config
from .parser_estate import get_url_with_input_params_avito, get_url_with_input_params_cian
from .outputs import file_output


URL_ESTATE_AREA = {
    '0': ('https://www.avito.ru/', get_url_with_input_params_avito),
    '1': ('https://www.cian.ru/', get_url_with_input_params_cian),
}


def main() -> NoReturn:
    queue = Queue()
    process_tg = Process(target=tg_bot, args=(queue,))
    process_tg.start()
    while True:
        if not queue.empty():
            input_user_data = queue.get()
            logging.info(f'Передан запрос на парсинг')

            id_rooms = [ID_ROOMS[id] for id in input_user_data["rooms_count"]]

            logging.info(f'id_rooms : {id_rooms}')
            logging.info(f'locations : {input_user_data["location"]}')
            
            parsers = [None, None]
            for index in range(len(input_user_data["area"])):
                parsers[index] = URL_ESTATE_AREA[input_user_data["area"][index]]
                logging.info(f' parsers[index] {parsers[index]}')
            first_parser = parsers[0]
            second_parser = parsers[1] 
            if first_parser:
                # Запуск парсера
                logging.info(f'first_parser : {first_parser}')
                parsing_func = first_parser[1]
                url = first_parser[0]
                result = parsing_func(url=url, id_rooms=id_rooms, search_place=input_user_data["location"], already_exists=input_user_data["already_exists"])
            if second_parser:
                pass

            logging.info('данные собраны')
            if '0' in input_user_data["send_parsing_file"]:
                pass 

            file_output(result, 'avito.ru')
            logging.info('данные отправлены')



if __name__ == '__main__':
    start_logging_config()
    main()