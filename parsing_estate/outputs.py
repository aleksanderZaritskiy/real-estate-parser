import datetime as dt
import logging
from typing import Tuple, NoReturn

import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

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
            file,
            dialect='unix',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )
        writter.writerows(result)
    logging.info('Файл с парсингом успешно добавлен')


def send_email(
    smtp_server,
    port,
    sender_email,
    sender_password,
    recipient_email,
    subject,
    body,
    attachment_path,
) -> NoReturn:
    # Создаем сообщение
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Открываем файл вложения и добавляем его в сообщение
    with open(attachment_path, 'rb') as attachment_file:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(attachment_file.read())
        encoders.encode_base64(attachment)
        attachment.add_header(
            'Content-Disposition', f'attachment; filename={attachment_path}'
        )
        msg.attach(attachment)

    # Отправляем сообщение через SMTP-сервер
    with smtplib.SMTP_SSL(smtp_server, port) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
