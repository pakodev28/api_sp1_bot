import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


bot = telegram.Bot(token=TELEGRAM_TOKEN)


def get_file_handler():
    file_handler = RotatingFileHandler(
        'homework.log',
        maxBytes=50000000,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s,%(levelname)s,%(message)s,%(name)s'))
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s,%(levelname)s,%(message)s,%(name)s'))
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger


logger = get_logger(__name__)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(
        url, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    logger.info(msg='Отправка сообщения')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    logger.debug(msg='Бот запущен')
    current_timestamp = int(time.time())
    while True:
        try:
            homework = get_homeworks(current_timestamp)
            if homework.get('homeworks'):
                send_message(parse_homework_status(
                    homework.get('homeworks')[0]))
            current_timestamp = homework.get(
                'current_date',
                current_timestamp)
            time.sleep(300)
        except Exception as e:
            logger.exception(f'Бот упал с ошибкой: {e}')
            send_message(e)
            time.sleep(5)


if __name__ == '__main__':
    main()
