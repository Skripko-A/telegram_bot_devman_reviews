# Бот для уведомлений
Телеграм бот, который присылает сообщение пользователю в телеграм, при появлении нового ревью от менторов Devman
### Как установить
Для работы вам понадобится токен доступа к api Девмана.  
Создать бота в телеграм:  
@BotFather (https://t.me/BotFather)
```
/start
```
```
/newbot
```
Сохраните ваш токен api Devman, токен вашего бота в .env файл:
```
DEVMAN_TOKEN = "ваш токен к API Devman"
TG_BOT_TOKEN = 'токен вашего телеграм бота'
TG_USER_CHAT_ID = 'дефолтный id чата в телеграм, куда бот будет писать уведомления'
```
Python3 должен быть установлен.  
Установите зависимости:
```commandline
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```
### Запуска скрипта
```commandline
python3 script_1.py -i=ваш chat_id пользователя телеграм
```
Если запустить скрипт без аргумента -i, бот использует chat_id указанный в вашем .env
```commandline
python3 scirpt_1.py
```
Пока скрипт запущен и имеет доступ ко всемирной сети, бот мониторит api devman и присылает сообщения вам в телеграм о появлении нового ревью вашей работы.  
ВНИМАНИЕ! Бот не заметит ревью, появившегося до запуска скрипта.
### Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
