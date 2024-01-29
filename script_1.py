import argparse
import os
import time
import requests
import telegram
from dotenv import load_dotenv


def bot_send_message(bot, chat_id, response, task_name):
    if response['new_attempts'][0]['is_negative']:
        text = f'Задание "{task_name}" проверено и направлено на доработку!'
        bot.send_message(chat_id=chat_id, text=text)
    elif not response['new_attempts'][0]['is_negative']:
        text = f'Задание "{task_name}" выполнено'
        bot.send_message(chat_id=chat_id, text=text)


def send_simple_request(timestamp, devman_token):
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {devman_token}', 'timestamp': f'{timestamp}'}
    response = requests.get(url, headers=headers, timeout=90)
    response.raise_for_status()
    return response.json()


def pull_push_timestamp(response, timestamps):
    if response['status'] == 'found':
        timestamp = str(response['last_attempt_timestamp'])
        timestamps.append(timestamp)
    elif response['status'] == 'timeout':
        timestamp = str(response['timestamp_to_request'])
        timestamps.append(timestamp)


def set_cli_args(default_chat_id):
    parser = argparse.ArgumentParser(description='Check for task updates')
    parser.add_argument('-i', '--chat_id', type=int,
                        help='enter your telegram chat_id', default=default_chat_id)
    return parser


def main():
    load_dotenv()
    devman_token = os.environ['DEVMAN_TOKEN']
    tg_bot_token = os.environ['TG_BOT_TOKEN']
    default_chat_id = os.environ['CHAT_ID']
    bot = telegram.Bot(tg_bot_token)
    timestamps = [None]
    response = send_simple_request(devman_token=devman_token, timestamp=timestamps[0])
    cli_args = set_cli_args(default_chat_id=default_chat_id).parse_args()
    chat_id = cli_args.chat_id
    if response['status'] == 'found':
        task_name = response['new_attempts'][0]['lesson_title']
        bot_send_message(bot=bot, chat_id=chat_id, response=response, task_name=task_name)
    pull_push_timestamp(response=response, timestamps=timestamps)
    while timestamps:
        response = send_simple_request(devman_token=devman_token, timestamp=timestamps[1])
        if response['status'] == 'found':
            task_name = response['new_attempts'][0]['lesson_title']
            bot_send_message(bot=bot, chat_id=chat_id, response=response, task_name=task_name)
        pull_push_timestamp(response=response, timestamps=timestamps)
        timestamps.pop(0)


if __name__ == '__main__':
    while True:
        try:
            main()
        except requests.exceptions.ReadTimeout as timeout_error:
            print(timeout_error)
        except requests.exceptions.ConnectionError as connection_error:
            print(connection_error)
            time.sleep(5)
