import time
import os
import sys

import colorama
from colorama import Fore, Style
from art import *
import hashlib
import configparser

import configs


def check_file(filename: str) -> bool:
    """
    Этот скрипт проверяет список файлов на их существование и целостность.
    Если файл не существует, выводится сообщение об ошибке.
    Если файл поврежден или не удается прочитать содержимое, также выводится сообщение об ошибке.
    :param filename: Имя файла для проверки
    :return: True если файл целый и существует
    """
    config_file = configparser.ConfigParser()
    config_file.read(r'config\hash.ini')

    filename_str = fr'src\{filename}'
    if not os.path.exists(filename_str):
        return False
    else:
        file_body = None
        try:
            file = open(filename_str, 'rb')
            file_body = file.read()
            file.close()
            # return True
        except (Exception, ):
            return False
        # проверяем хеши файла
        file_hash = hashlib.sha256(file_body)
        hash_file_return = file_hash.hexdigest()
        # print(hash_file_return)
        # print(filename['file_hash'])
        if hash_file_return == config_file['FILE_HASH'][filename]:
            return True
        else:
            return False
        # print(hash_file_return)


def start_server():
    """
    Файл старта и проверки целостности проекта при запуске.
    В случае ошибки проект автоматически закрывается
    :return: Процедура
    """
    colorama.init()
    print(Fore.BLUE + '')
    tprint('RFC Informer Bot')
    time.sleep(1)

    print(Fore.BLUE + f'Project RFC Informer Bot starting\n'
                      f'\n'
                      f'version {configs.version} / {configs.data_version_update}\n')

    count_error = 0

    print(Fore.WHITE + '╞RFC Informer Bot')
    print(Fore.WHITE + '╘╤Launch service.bat')

    config_file = configparser.ConfigParser()
    # Поднимаемся на уровень выше (из папки pilot в папку проект)
    # os.chdir(os.pardir)
    config_file.read(r'config\hash.ini')
    # print(config_file.sections())
    # config_file['FILE_HASH']['dem_token']

    for file in config_file['FILE_HASH']:
        if check_file(file):
            o = '[OK]'
            print(Fore.WHITE + ' ╞', end='')
            print(Fore.GREEN + f'{file.ljust(50, "-")}{o.rjust(10, "-")}')
        else:
            e = '[ERROR]'
            print(Fore.WHITE + ' ╞', end='')
            print(Fore.RED + f'{file.ljust(50, "-")}{e.rjust(10, "-")}')
            count_error += 1
        time.sleep(0.3)

    print('\n')
    time.sleep(1)
    if count_error == 0:
        print(Fore.GREEN + f'Start successfully\n \n')
        print(Style.RESET_ALL)
    else:
        print(Fore.RED + f'START NOT SUCCESSFULLY\n \n')
        print(Style.RESET_ALL)
        # os.chdir("..")

        # Заходим в папку src
        # os.chdir("co-pilot")

        sys.exit(1)
