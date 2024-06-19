import requests
from urllib3 import disable_warnings, exceptions

import hashlib

import configs


def hash_password(password):
    hash_object = hashlib.sha1(password.encode('utf-8'))
    hash_password_return = hash_object.hexdigest()
    return hash_password_return


def auth_1c_check(login, password):
    """
    Функция принимает на вход логин и пароль пользователя,
    отправляет запрос к веб-сервису ИС 1С и возвращает True если:
    - логин и пароль указаны верно
    - уз не заблокирована
    :param login: логин пользователя ИС 1С
    :param password: хеш пароль пользователя ИС 1С
    :return: переменную boolean значения.
    """

    aut_check = {"login": login,
                 "password": password
                 }
    endpoint = f"{configs.auth_1c['link']}/ws/RFC_UserCheck/UserCheck.1cws"

    body = '<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope' \
           f'/" xmlns:jet="{configs.auth_1c["link"]}">' \
           '<x:Header/><x:Body><jet:CheckUser><jet:InputString>' + str(aut_check) + \
           '</jet:InputString></jet:CheckUser></x:Body></x:Envelope>'
    headers = {"Content-Type": "application/json ; charset=utf-8"}
    headers.update({"Content-Length": str(len(body))})
    disable_warnings(exceptions.InsecureRequestWarning)
    answer_auth = requests.request("POST", url=endpoint, headers=headers,
                                   data=body.encode('utf-8'),
                                   auth=(configs.auth_1c['login'],
                                         configs.auth_1c['password']
                                         ),
                                   verify=False)
    answer_auth = answer_auth.text
    answer_auth = answer_auth.replace('<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">',
                                      '')
    answer_auth = answer_auth.replace('<soap:Body>', '')
    answer_auth = answer_auth.replace(f'<m:CheckUserResponse xmlns:m="{configs.auth_1c["link"]}">',
                                      '')
    answer_auth = answer_auth.replace('<m:return xmlns:xs="http://www.w3.org/2001/XMLSchema"', '')
    answer_auth = answer_auth.replace('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">', '')
    answer_auth = answer_auth.replace('</m:return>', '')
    answer_auth = answer_auth.replace('</m:CheckUserResponse>', '')
    answer_auth = answer_auth.replace('</soap:Body>', '')
    answer_auth = answer_auth.replace('</soap:Envelope>', '')
    answer_auth = answer_auth.replace('\r\n\t\t\t\t\t', '')
    answer_auth = answer_auth.replace('\r\n\t\t\t\t', '')
    answer_auth = answer_auth.replace('\r\n\t\t\t', '')
    answer_auth = answer_auth.replace('\r\n\t\t', '')
    answer_auth = answer_auth.replace('\r\n\t', '')
    answer_auth = answer_auth.replace('\r', '')
    answer_auth = answer_auth.replace('\n', '')
    answer_auth = answer_auth.replace('\t', '')
    return answer_auth
