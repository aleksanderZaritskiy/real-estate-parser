import re
import string
from datetime import datetime, timedelta
from typing import Any, Tuple

from dateutil.parser import parse
from transliterate import translit

from .constants import MONTH_NAMES_CYRILLIC_TO_LATIN, TRANSFORM_INPUT_DATA
from .exceptions import PunctuationCharError, LatinLettersLocationError, NumberInLocationError, UncorrectTimeCreateAd


# Адаптирум название места поиска под траслит
# Отправляем post запрос к yandex.translate
def place(place: str = '', eng_text: str = 'all/') -> str:
    if place:
        for char in place:
            if char.isdigit():
                raise NumberInLocationError('В названии территории не может быть чисел')
            if char in string.ascii_letters:
                raise LatinLettersLocationError('Название должно содержать только буквы кирилицы')
            if char in string.punctuation:
                raise PunctuationCharError('Название содержит недопустимые символы')
        else:
            eng_text = (translit(place, language_code='ru', reversed=True).replace(' ', '_') + '/').lower()
        
    return eng_text


# Обрабатывает данные содержащие характерисктики кваритр
def parsing_data_grinding(data_place: str) -> Tuple[str]:
    place_params = data_place.strip().split()
    if len(place_params) == 5:
        type_estate = place_params[0].split('-')
        return (type_estate[0], type_estate[1],  place_params[1] + place_params[2], place_params[3] + place_params[4])
    return (place_params[0], place_params[1], place_params[2] + place_params[3], place_params[4] + place_params[5])


# Обработка даты из заданных параметров и 
# входящих от парсера
def converter_time(times: str) -> datetime:
    now = datetime.now()
    try:
    # Обрабатываем случаи с относительными временами
        if 'мин' in times:
            minutes = int(re.search(r'\d+', times).group())
            return now - timedelta(minutes=minutes)
        elif 'час' in times:
            hours = int(re.search(r'\d+', times).group())
            return now - timedelta(hours=hours)
        elif 'сек' in times:
            seconds = int(re.search(r'\d+', times).group())
            return now - timedelta(seconds=seconds)
        elif 'недел' in times:
            weeks = int(re.search(r'\d+', times).group())
            return now - timedelta(weeks=weeks)
        elif 'день' in times or 'дн' in times:
            day = int(re.search(r'\d+', times).group())
            return now - timedelta(days=day)
        else:
            # Обрабатываем, конкретные даты
            current_month = times.split()[1][:4]
            for month in MONTH_NAMES_CYRILLIC_TO_LATIN:
                if current_month in month:
                    return parse(MONTH_NAMES_CYRILLIC_TO_LATIN[month], dayfirst=True)
    except Exception:
        raise UncorrectTimeCreateAd('Ошибка в функции "utils.conver_time" Ошибка ввода пользователя')

   
# Преобразование выбранных пользователем опций
def transform_input_answer(config_name: str, answers: str) -> Any:
    result = []
    if config_name in TRANSFORM_INPUT_DATA:
        for ans in answers:
            if ans in TRANSFORM_INPUT_DATA[config_name]:
                result.append(TRANSFORM_INPUT_DATA[config_name].get(ans))
        return result
    return answers


