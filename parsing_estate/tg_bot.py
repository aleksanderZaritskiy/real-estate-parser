import datetime
import re
import logging
from typing import Type, NoReturn

from multiprocessing import Queue
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    MessageHandler,
    Filters,
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
)
from telegram.error import BadRequest

from .constants import (
    TEGELGRAM_TOKEN,
    INPUT_LOCATION,
    INPUT_ALLREADY_EXISTS,
    INPUT_MAIL,
    CONFIG,
    PATTERN_VALID_MAIL,
)
from .utils import transform_input_answer, place, converter_time
from .exceptions import (
    PunctuationCharError,
    LatinLettersLocationError,
    NumberInLocationError,
    UncorrectTimeCreateAd,
    ImportantConfigsDoNotExists,
)
from .db_config import Chat, Config, start_session, Session
from .logging_config import start_logging_config


session: Session = start_session()


def button(update: Type[Update], context: Type[CallbackContext]) -> None:
    query = update.callback_query
    query.answer()
    selected_option = query.data
    cur_option = context.user_data.get('params')
    if not cur_option:
        query.message.reply_text('Сессия устарела, для выбора перевызовите команду')
    current_param_data = context.user_data[cur_option]
    logging.info(
        f'Пользователь указывает настройки к: {cur_option} выбор: {transform_input_answer(cur_option, [query.data])}'
    )
    if selected_option in current_param_data['input_answer']:
        current_param_data['input_answer'].remove(selected_option)
    else:
        current_param_data['input_answer'].append(selected_option)

    keyboard = current_param_data['keyboard']
    for index in range(len(keyboard)):
        ans = keyboard[index][0].callback_data
        text = keyboard[index][0].text
        if ans in current_param_data['input_answer'] and text == 'Готово':
            current_param_data['input_answer'].remove(ans)
            if (
                cur_option == 'send_parsing_file'
                and '0' in current_param_data['input_answer']
            ):
                query.edit_message_text(
                    f'Введите почту на которую отправлять данные. Что бы завершить настройки почты введите "/ok"'
                )
            else:
                query.edit_message_text(f'Опции для {cur_option} сохранены')
            return
        elif ans not in current_param_data['input_answer'] and " (выбран)" in text:
            keyboard[index][0].text = keyboard[index][0].text.rstrip(' (выбран)')
        elif ans in current_param_data['input_answer'] and " (выбран)" not in text:
            keyboard[index][0].text += " (выбран)"
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        query.edit_message_text(
            text=current_param_data['text_message'], reply_markup=reply_markup
        )
    except BadRequest:
        query.message.reply_text(
            current_param_data['text_message'], reply_markup=reply_markup
        )


def area_command(update: Type[Update], context: Type[CallbackContext]) -> NoReturn:
    keyboard = [
        [InlineKeyboardButton("avito.ru", callback_data='0')],
        [InlineKeyboardButton("Готово", callback_data='1')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'Выберите площадки для поиска, затем нажмите "Готово":', reply_markup=reply_markup
    )

    context.user_data['params'] = 'area'
    context.user_data['area'] = {
        'keyboard': [
            [InlineKeyboardButton(f"{place}", callback_data=str(i))]
            for i, place in enumerate(['avito.ru', 'Готово'])
        ],
        'text_message': "Выберите площадки для поиска, затем нажмите 'Готово':",
        'input_answer': [],
    }


def rooms_count_command(update: Type[Update], context: Type[CallbackContext]) -> NoReturn:
    keyboard = [
        [
            InlineKeyboardButton("апартаменты", callback_data='0'),
            InlineKeyboardButton("1 комната", callback_data='1'),
        ],
        [
            InlineKeyboardButton("2 комнаты", callback_data='2'),
            InlineKeyboardButton("3 комнаты", callback_data='3'),
        ],
        [
            InlineKeyboardButton("4 комнаты", callback_data='4'),
            InlineKeyboardButton("5 комнат и больше", callback_data='5'),
        ],
        [InlineKeyboardButton("свободная планировка", callback_data='6')],
        [InlineKeyboardButton("Готово", callback_data='7')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'Выберите количество комнат, затем нажмите "Готово":', reply_markup=reply_markup
    )

    context.user_data['params'] = 'rooms_count'
    context.user_data['rooms_count'] = {
        'keyboard': [
            [InlineKeyboardButton(f"{place}", callback_data=str(i))]
            for i, place in enumerate(
                [
                    'апартаменты',
                    '1 комната',
                    '2 комнаты',
                    '3 комнаты',
                    '4 комнаты',
                    '5 комнат и более',
                    'свободная планировка',
                    'Готово',
                ]
            )
        ],
        'text_message': "Выберите количество комнат, затем нажмите 'Готово':",
        'input_answer': [],
    }


def send_parsing_file_command(
    update: Type[Update], context: Type[CallbackContext]
) -> int:
    keyboard = [
        [InlineKeyboardButton("почта", callback_data='0')],
        [InlineKeyboardButton("Готово", callback_data='1')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'Выберите место для выгрузки файла с собранными данными, затем нажмите "Готово":',
        reply_markup=reply_markup,
    )

    context.user_data['params'] = 'send_parsing_file'
    context.user_data['send_parsing_file'] = {
        'keyboard': [
            [InlineKeyboardButton(f"{place}", callback_data=str(i))]
            for i, place in enumerate(['почта', 'Готово'])
        ],
        'text_message': "Выберите площадки для поиска, затем нажмите 'Готово':",
        'input_answer': [],
    }
    return INPUT_MAIL


def info_command(update: Type[Update], context: Type[CallbackContext]) -> NoReturn:
    chat_data = update.message.to_dict().get('chat')
    update.message.reply_text(
        f'Приветствую, {chat_data.get("first_name")} {chat_data.get("last_name")}! Для работы бота вам необходимо указать желаемые конфигуграции. Это сделать вы можете вызвав команду /config и следуя указаниям.\nЕсли вы хотите посмотреть текущие настройки вызовите команду /get_current_config.\nЕсли конфигурации указаны, вызовите команду /start'
    )


def сonfig_command(update: Type[Update], context: Type[CallbackContext]) -> NoReturn:
    update.message.reply_text(
        f'Команда /send_parsing_file - выбор места выгрузки собранных данных. По умолчанию файлы выгружаются в чат с ботом.\nКоманда /area - выбор площадок для поиска (обязательная настройка)\nКоманда /rooms_count - фильтрация поиска по количеству комнат (обязательная настройка)\nКоманда /location - выбор территории поиска. По умолчанию вся страна.\nКоманда /already_exists - поиск будет ограничен указанной датой/время или временной дельтой. По умолчанию ограничения нет (рекомендуется ограничивать поиск)'
    )


def get_current_config_command(
    update: Type[Update], context: Type[CallbackContext]
) -> NoReturn:
    for key in CONFIG:
        if key in context.user_data:
            CONFIG[key] = transform_input_answer(
                key, context.user_data[key]['input_answer']
            )
            if key == 'send_parsing_file' and context.user_data['send_parsing_file'].get(
                'accepted_mail'
            ):
                CONFIG['accepted_mail'] = context.user_data['send_parsing_file'].get(
                    'accepted_mail'
                )

    update.message.reply_text(
        f"Площадки : {CONFIG['area']}\nКоличество комнат: {CONFIG['rooms_count']}\nЛокация : {CONFIG['location']}\nОбъявления до (включительно): {CONFIG['already_exists']}\nВыгрузка данных: {CONFIG['send_parsing_file']}\nУказанная почта : {CONFIG['accepted_mail']}"
    )


def input_mail(update: Type[Update], context: Type[CallbackContext]) -> NoReturn:
    text = update.message.text
    logging.info(f'Указывает почту {text}')
    match = re.fullmatch(PATTERN_VALID_MAIL, text)
    if match:
        context.user_data['send_parsing_file']['accepted_mail'] = text
        update.message.reply_text(
            f'Вы указали почту {text}. Корректно? Если да - введите "/ok", если нет - Введите почту ещё раз'
        )
    else:
        update.message.reply_text(f'Вы указали почту {text}. Почта не валидна')


def end_input_mail(update: Type[Update], context: Type[CallbackContext]) -> int:
    if not context.user_data['send_parsing_file'].get('accepted_mail'):
        context.user_data['send_parsing_file']['input_answer'].remove('0')
        update.message.reply_text(
            f'Настройки почты не приняты. Если хотите выбрать способ отправки файлов - "почта", введите команду "/send_parsing_file -> "почта" и укажите валидную почту"'
        )
    else:
        update.message.reply_text(f'Настройки почты приняты.')
    return ConversationHandler.END


def location_command(update: Type[Update], context: Type[CallbackContext]) -> int:
    update.message.reply_text(
        'Укажите регион/город или любой населенный пункт, что бы бот искал в рамках указаной локации.\nНеобходимо ввести локацию на русском языке, без ошибок, регистр неважен.\nНапример "симферополь", "краснодар"\nДля завершения ввода введите "/ok"'
    )
    return INPUT_LOCATION


def input_location(update: Type[Update], context: Type[CallbackContext]) -> NoReturn:
    context.user_data['location'] = {'input_answer': 'all/'}
    text = update.message.text
    logging.info(f'Указывает локацию {text}')
    try:
        current_location = place(text)
    except (
        PunctuationCharError,
        LatinLettersLocationError,
        NumberInLocationError,
    ) as error:
        logging.error(f'{error.__class__.__name__} : {error.args}')
        update.message.reply_text(f'{error.args}')
    else:
        context.user_data['location']['input_answer'] = current_location
        update.message.reply_text(
            f'Указанный город {text} принят. Если хотите изменить, введите город повторно, для завершения - команда "/ok"'
        )


def end_input_location(update: Type[Update], context: Type[CallbackContext]) -> int:
    if context.user_data['location']['input_answer'] == 'all/':
        update.message.reply_text(
            'Название населенного пункт не принятно. Локация остаётся "по всей стране". Для повторного набора вызовите команду "/location"'
        )
    return ConversationHandler.END


def already_exists_command(update: Type[Update], context: Type[CallbackContext]) -> int:
    update.message.reply_text(
        'Укажите временную дельту отбора объявлений.\nНапример "30 минут", "1 час", "2 недели".\nБот будет добавлять объявления, которые размещены до указанной дельты(включительно).\nТакже вы можете указать дату и время.\nНапример "15 января 18:35". Принцин добавления объявлений будет тот же.\nЧтобы завершить /ok'
    )
    return INPUT_ALLREADY_EXISTS


def input_already_exists(
    update: Type[Update], context: Type[CallbackContext]
) -> NoReturn:
    text = update.message.text
    context.user_data['already_exists'] = {
        'input_answer': datetime.datetime(1999, 1, 1, 12, 0, 0)
    }
    try:
        current_time = converter_time(text)
        logging.info(current_time)
        logging.info(type(current_time))
    except UncorrectTimeCreateAd as error:
        logging.error(f'{error.__class__.__name__} : {error.args}')
        update.message.reply_text(
            f'{text} Некорректный формат дельты. Ознакомьтесь с инструкцией ввода'
        )
    else:
        context.user_data['already_exists'] = {'input_answer': current_time}
        update.message.reply_text(
            f'Временная дельта {text} принят. Если хотите изменить, введите значение повторно, для завершения - команда "/ok"'
        )


def end_input_already_exists(update: Type[Update], context: Type[CallbackContext]) -> int:
    if (
        not context.user_data.get('already_exists')
        or datetime.datetime(1999, 1, 1, 12, 0, 0)
        == context.user_data['already_exists']['input_answer']
    ):
        update.message.reply_text(
            'Временная дельта не принята. Поиск остаётся по объявлениям "за весь период". Для повторного набора вызовите команду "/already_exists"'
        )
    return ConversationHandler.END


def start_command(update: Type[Update], context: Type[CallbackContext]) -> None:
    chat = update['message']['chat']['id']
    chat_obj = session.query(Chat).get(chat)
    queue = context.bot_data['queue']

    if chat_obj:
        data = {
            'area': chat_obj.config.area,
            'rooms_count': chat_obj.config.rooms_count,
            'location': chat_obj.config.location,
            'already_exists': chat_obj.config.already_exists,
            'send_parsing_file': chat_obj.config.send_parsing_file,
            'mail': chat_obj.config.mail,
        }
        params = [
            ('area', ''),
            ('rooms_count', ''),
            ('location', ''),
            ('already_exists', ''),
            ('send_parsing_file', 'accepted_mail'),
        ]
        for param, specific in params:
            if param in context.user_data:
                if param == 'send_parsing_file' and context.user_data[param].get(
                    specific
                ):
                    data[param] = context.user_data[param].get('input_answer')
                    data['mail'] = context.user_data[param].get(specific)
                elif context.user_data[param]['input_answer']:
                    data[param] = context.user_data[param]['input_answer']

        config = session.query(Config).filter_by(chat_id=chat).first()
        config.bulk_update(**data)
        session.commit()

        queue.put(data)
        logging.info(f'Объект {chat_obj} добавлен в очередь')
        update.message.reply_text(
            f'Сбор данных займет время. Результат будет выслан на почту. Ожидайте'
        )
        return
    try:
        area = context.user_data['area']['input_answer']
        rooms_count = context.user_data['rooms_count']['input_answer']
        send_parsing_file = context.user_data['send_parsing_file']['input_answer']
        mail = context.user_data['send_parsing_file']['accepted_mail']
        if any([not area, not rooms_count, not send_parsing_file, not mail]):
            raise ImportantConfigsDoNotExists(
                'Не указаны настройки для /area, /rooms_count или /send_parsing_file'
            )
    except KeyError as error:
        logging.info(f'{error.args}')
        update.message.reply_text(f'Не указана конфигурация для: {error.args}')
        return
    params = [
        ('location', ''),
        ('already_exists', ''),
        ('send_parsing_file', 'accepted_mail'),
    ]
    for param, specific in params:
        if param in context.user_data:
            data[param] = context.user_data[param].get('input_answer')
        else:
            data[param] = CONFIG[param]

    else:
        chat_obj = Chat(chat=chat)
        config = Config(
            area=area,
            rooms_count=rooms_count,
            send_parsing_file=data['send_parsing_file'],
            location=data['location'],
            already_exists=data['already_exists'],
            mail=data['accepted_mail'],
        )
        chat_obj.config = config
        session.add(chat_obj)
        session.commit()
        logging.info(f'Добавлен новый объект в базу: {chat_obj.chat}')
        data = {
            'area': chat_obj.config.area,
            'rooms_count': chat_obj.config.rooms_count,
            'location': chat_obj.config.location,
            'already_exists': chat_obj.config.already_exists,
            'send_parsing_file': chat_obj.config.send_parsing_file,
            'mail': chat_obj.config.mail,
        }
        queue.put(data)
        logging.info(f'Объект чата {chat_obj} добавлен в очередь')
        update.message.reply_text(
            f'Сбор данных займет время. Результат будет выслан на почту. Ожидайте'
        )
        return


def tg_bot(queue: Type[Queue]) -> NoReturn:
    updater = Updater(TEGELGRAM_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['queue'] = queue
    start_logging_config()

    conv_handler_mail = ConversationHandler(
        entry_points=[CommandHandler('send_parsing_file', send_parsing_file_command)],
        states={
            INPUT_MAIL: [MessageHandler(Filters.text & ~Filters.command, input_mail)],
        },
        fallbacks=[CommandHandler('ok', end_input_mail)],
    )

    conv_handler_location = ConversationHandler(
        entry_points=[CommandHandler('location', location_command)],
        states={
            INPUT_LOCATION: [
                MessageHandler(Filters.text & ~Filters.command, input_location)
            ]
        },
        fallbacks=[CommandHandler('ok', end_input_location)],
    )

    conv_handler_already_exists = ConversationHandler(
        entry_points=[CommandHandler('already_exists', already_exists_command)],
        states={
            INPUT_ALLREADY_EXISTS: [
                MessageHandler(Filters.text & ~Filters.command, input_already_exists)
            ]
        },
        fallbacks=[CommandHandler('ok', end_input_already_exists)],
    )

    info_handler = CommandHandler('info', info_command)
    config_handler = CommandHandler('config', сonfig_command)
    area_handler = CommandHandler('area', area_command)
    rooms_count_handler = CommandHandler('rooms_count', rooms_count_command)
    get_current_config = CommandHandler('get_current_config', get_current_config_command)
    start_handler = CommandHandler('start', start_command)

    dispatcher.add_handler(info_handler)
    dispatcher.add_handler(config_handler)
    dispatcher.add_handler(area_handler)
    dispatcher.add_handler(rooms_count_handler)
    dispatcher.add_handler(conv_handler_mail)
    dispatcher.add_handler(conv_handler_location)
    dispatcher.add_handler(conv_handler_already_exists)
    dispatcher.add_handler(get_current_config)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

    updater.idle()
