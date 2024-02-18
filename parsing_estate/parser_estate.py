import datetime
import logging
from typing import Type, Tuple, List, Dict, Any
from urllib.parse import urljoin

from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from .utils import parsing_data_grinding, converter_time


def parsing_estate_offers_avito(
    url: str, time_config: datetime, driver: Type[Driver] = None
) -> List[Tuple[str]]:
    logging.info(
        f'Начало работы парсера по сбору html кода c {url} страница #{url[url.find("p=") + 2]:}'
    )
    data = []

    try:
        driver.get(url)
        parent_element = driver.find_element(
            By.CSS_SELECTOR, 'div[data-marker="catalog-serp"]'
        )
        childrens = parent_element.get_attribute("outerHTML")
        soup = BeautifulSoup(childrens, 'lxml')
        offers = [
            data.find('div', {'class': 'styles-module-theme-CRreZ'})
            for data in soup.find('div', {'class': 'items-items-kAJAg'})
        ]
        for offer in offers:
            try:
                exists_allready = offer.find(
                    'div', {'data-marker': 'item-date/tooltip/reference'}
                ).text
                logging.info(f'{exists_allready} : {converter_time(exists_allready)}')
                if time_config > converter_time(exists_allready):
                    return data
                price = offer.find('meta', {'itemprop': 'price'})['content']
                location = offer.find(
                    'p',
                    {
                        'class': 'styles-module-root-_KFFt styles-module-size_s-awPvv styles-module-size_s-_P6ZA stylesMarningNormal-module-root-OSCNq stylesMarningNormal-module-paragraph-s-_c6vD'
                    },
                ).text
                link = urljoin(
                    'https://www.avito.ru/', offer.find('a', {'itemprop': 'url'})['href']
                )
                rooms_count, type_estate, area_estate, floor = parsing_data_grinding(
                    offer.find('h3', {'itemprop': 'name'}).text
                )
                data.append(
                    (
                        type_estate,
                        rooms_count,
                        area_estate,
                        floor,
                        price,
                        location,
                        link,
                        exists_allready,
                    )
                )
            except AttributeError:
                logging.info('Игнор, реклама.')
                continue
        button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a[data-marker="pagination-button/nextPage"]')
            )
        )
        if button:
            button.send_keys(Keys.ENTER)
            next_page_parsing = parsing_estate_offers_avito(
                driver.current_url, time_config, driver=driver
            )
            if next_page_parsing:
                data.extend(next_page_parsing)
        return [
            (
                'type_place',
                'rooms_count',
                'area',
                'floor',
                'price(Rub)',
                'location',
                'link',
                'allready_exists',
            )
        ] + data
    except Exception as error:
        logging.error(error)
        driver.close()
        driver.quit()


# Формирует эндпоинт для парсера квартир в соотвествии
# C указанными параметрами
def get_url_with_input_params_avito(**kwargs: Dict[str, Any]) -> List[Tuple[str]]:
    logging.info('Начало работы по формированию урл с указанными параметрами')
    # Перевод Selenium в фоновый режим
    driver = Driver(uc=True, headless=True)
    try:
        # Открываем ендпоинт с указанной локацией поиска
        driver.get(
            'https://www.avito.ru/'
            + kwargs.get('search_place')
            + 'kvartiry/prodam-ASgBAgICAUSSA8YQ?cd=1'
        )
        # Скролим страницу вниз, для доступа к меню
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        for id in kwargs.get('id_rooms'):
            # Выбераем указанные комнаты
            rooms = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f'span[data-marker="params[549]({id})/text"]')
                )
            )
            rooms.click()
        # Подтвержаем выбор
        accept_choise = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-marker="search-filters/submit-button"]')
            )
        )
        accept_choise.send_keys(Keys.ENTER)
        # Посты сразу отсортированы по дате
        # И текущей странице
        url = driver.current_url + '&s=104&p=1'
        logging.info(url)
        return parsing_estate_offers_avito(
            url, kwargs.get('already_exists'), driver=driver
        )
    except Exception as error:
        logging.error(error)
        driver.close()
        driver.quit()
