import argparse
import os
import time
import requests
import telegram
from dotenv import load_dotenv


def set_cli_args(default_chat_id):
    parser = argparse.ArgumentParser(description='Check for task updates')
    parser.add_argument('-i', '--chat_id', type=int,
                        help='enter your telegram chat_id', default=default_chat_id)
    return parser


def get_devman_reviews(timestamp, devman_token):
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {devman_token}', 'timestamp': timestamp}
    response = requests.get(url, headers=headers, timeout=90)
    response.raise_for_status()
    return response.json()


def prepare_text_for_tlg_message(response, task_name):
    if response['new_attempts'][0]['is_negative']:
        return f'Задание "{task_name}" проверено и направлено на доработку!'
    return f'Задание "{task_name}" выполнено'


def send_message_on_server_reply(response, bot, chat_id):
    if response['status'] == 'found':
        task_name = response['new_attempts'][0]['lesson_title']
        text = prepare_text_for_tlg_message(response=response, task_name=task_name)
        bot.send_message(text=text, chat_id=chat_id)


def update_timestamp_for_next_request(response):
    if response['status'] == 'found':
        return str(response['last_attempt_timestamp'])
    return str(response['timestamp_to_request'])


def launch_bot():
    load_dotenv()
    devman_token = os.environ['DEVMAN_TOKEN']
    tg_bot_token = os.environ['TG_BOT_TOKEN']
    default_chat_id = os.environ['TG_USER_CHAT_ID']
    bot = telegram.Bot(tg_bot_token)
    cli_args = set_cli_args(default_chat_id=default_chat_id).parse_args()
    chat_id = cli_args.chat_id

    response = get_devman_reviews(devman_token=devman_token, timestamp=None)
    send_message_on_server_reply(response=response, bot=bot, chat_id=chat_id)
    timestamp = update_timestamp_for_next_request(response=response)
    response = get_devman_reviews(devman_token=devman_token, timestamp=timestamp)
    send_message_on_server_reply(response=response, bot=bot, chat_id=chat_id)
    update_timestamp_for_next_request(response=response)


if __name__ == '__main__':
    while True:
        try:
            launch_bot()
        except requests.exceptions.ReadTimeout as timeout_error:
            print(timeout_error)
        except requests.exceptions.ConnectionError as connection_error:
            print(connection_error)
            time.sleep(5)
