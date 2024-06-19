import logging
from datetime import datetime
import time
# import os

import colorama
from colorama import Fore, Style

import postgres_init
import configs
import firewall_mars

# print(os.getcwd())
# os.chdir(os.pardir)

# настройка конфига журнала логов
logging.basicConfig(
    format='%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] %(message)s',
    datefmt='%H:%M:%S %d.%m.%Y',
    level=logging.INFO,
    filename=configs.file_log_name,
    encoding='utf-8'
)


def log_pass(us_id: int, type_search: str, search: str,) -> None:
    """
    :param us_id: id пользователя
    :param type_search: тип запроса
    :param search: текст запроса
    :return: записывает данные в лог, и выводит данные в консоль
    """
    time_unix_format = time.time()
    # spinner = Spinner('Loading ')
    # while state != 'FINISHED':
    #     # Do some work
    #     spinner.next()
    # state == 'FINISHED'

    full_user_name = firewall_mars.id_in_name(us_id)

    time_log = datetime.now().strftime("%H:%M:%S %d.%m.%Y")

    logging.info(f'ID: {us_id}, Пользователь: {full_user_name}, {type_search}: {search}')

    """Выводим на экран сервера текст лога. Если это ошибка, выводим это красным цветом"""
    if type_search == 'Ошибка':
        colorama.init()
        print(Fore.RED + '')
        print(f'Время: {time_log}, ID: {us_id}, Пользователь: {full_user_name}, {type_search}: {search}')
        print(Style.RESET_ALL)
    else:
        print(f'Время: {time_log}, ID: {us_id}, Пользователь: {full_user_name}, {type_search}: {search}')

    postgres_init.last_message_fn(us_id, int(time_unix_format))
