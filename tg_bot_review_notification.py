import argparse
import os
import logging
import time
import traceback
from dotenv import load_dotenv

import telegram
import requests


logger = logging.getLogger('bot_logger')

def set_cli_args(default_chat_id):
    parser = argparse.ArgumentParser(description='Check for task updates')
    parser.add_argument('-i', '--chat_id', type=int,
                        help='enter your telegram chat_id', default=default_chat_id)
    return parser


def get_devman_reviews(devman_token, params):
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {devman_token}'}
    response = requests.get(url, headers=headers, params=params, timeout=100)
    response.raise_for_status()
    return response.json()


def prepare_text_for_tlg_message(response, task_name):
    if response['new_attempts'][0]['is_negative']:
        return f'Задание "{task_name}" проверено и направлено на доработку!'
    return f'Задание "{task_name}" выполнено'


def send_message_on_server_reply(response, bot, chat_id):
    task_name = response['new_attempts'][0]['lesson_title']
    text = prepare_text_for_tlg_message(response=response, task_name=task_name)
    bot.send_message(text=text, chat_id=chat_id)


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id
    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(text=log_entry, chat_id=self.chat_id)


def main():
    load_dotenv()
    devman_token = os.environ['DEVMAN_TOKEN']
    tg_bot_token = os.environ['TG_BOT_TOKEN']
    default_chat_id = os.environ['TG_USER_CHAT_ID']
    bot = telegram.Bot(tg_bot_token)

    cli_args = set_cli_args(default_chat_id=default_chat_id).parse_args()
    chat_id = cli_args.chat_id

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot, default_chat_id))
    params = {}
    logger.info('Бот запущен')
    while True:
        try:
            response = get_devman_reviews(devman_token=devman_token, params=params)
            if response['status'] == 'found':
                params['timestamp'] = str(response['last_attempt_timestamp'])
                send_message_on_server_reply(response=response, bot=bot, chat_id=chat_id)
        except requests.exceptions.ReadTimeout as timeout_error:
            logging.error(timeout_error)
            logger.error(timeout_error)
        except requests.exceptions.ConnectionError as connection_error:
            logging.error(connection_error)
            time.sleep(5)
        except Exception:
            logger.error('Бот упал с ошибкой:')
            logger.error(traceback.format_exc())


if __name__ == '__main__':
    main()
