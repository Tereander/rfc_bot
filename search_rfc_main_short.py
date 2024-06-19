import requests
import json

# import psycopg2
from urllib3 import disable_warnings, exceptions

import configs


def search_rfc_main_short(number_rfc: str) -> dict:
    """
    Основная функция для проверки rfc. Принимает информацию для поиска.
    Подключается к базе и возвращает json файл с работами
    :param number_rfc: запрос информации для поиска в базе 1С
    :return: json файл с информацией о работах
    """

    # код поиска и вывода - Создаем клиент
    # ssl._create_default_https_context = ssl._create_unverified_context()
    endpoint = f"{configs.auth_1c['link']}/ws/RFC_Details/rfc.1cws"
    body = '<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope' \
           f'/" xmlns:jet="{configs.auth_1c["link"]}">' \
           '<x:Header/><x:Body><jet:GetDetails><jet:Number>' + str(number_rfc) + \
           '</jet:Number></jet:GetDetails></x:Body></x:Envelope>'

    # context = ssl._create_unverified_context()
    headers = {"Content-Type": "application/json ; charset=utf-8"}
    headers.update({"Content-Length": str(len(body))})
    disable_warnings(exceptions.InsecureRequestWarning)
    response = requests.request("POST", url=endpoint, headers=headers,
                                data=body.encode('utf-8'),
                                auth=(configs.auth_1c['login'],
                                      configs.auth_1c['password']),
                                verify=False)
    rfc_info_short = response.text

    rfc_info_short = rfc_info_short.replace('<soap:Envelope xmlns:soap'
                                            '="http://schemas.xmlsoap.'
                                            'org/soap/envelope/">', '')
    rfc_info_short = rfc_info_short.replace('<soap:Body>', '')
    rfc_info_short = rfc_info_short.replace(f'<m:GetDetailsResponse xmlns:m="{configs.auth_1c["link"]}">', '')
    rfc_info_short = rfc_info_short.replace('<m:return xmlns:xs="http://www.w3.org'
                                            '/2001/XMLSchema"', '')
    rfc_info_short = rfc_info_short.replace('xmlns:xsi="http://www.w3.org/2001/'
                                            'XMLSchema-instance">', '')
    rfc_info_short = rfc_info_short.replace('</m:return>', '')
    rfc_info_short = rfc_info_short.replace('</m:GetDetailsResponse>', '')
    rfc_info_short = rfc_info_short.replace('</soap:Body>', '')
    rfc_info_short = rfc_info_short.replace('</soap:Envelope>', '')
    rfc_info_short = rfc_info_short.replace('\r\n\t\t\t\t\t', '')
    rfc_info_short = rfc_info_short.replace('\r\n\t\t\t\t', '')
    rfc_info_short = rfc_info_short.replace('\r\n\t\t\t', '')
    rfc_info_short = rfc_info_short.replace('\r\n\t\t', '')
    rfc_info_short = rfc_info_short.replace('\r\n\t', '')
    # print(rfc_info)
    result = rfc_info_short.split('(_|_)')

    rfc_info_short = json.loads(result[0])  # загрузка обработанной строки в json

    # перебор словаря по значениям и замена пустых данных на отсутствие
    for value_man in rfc_info_short.keys():
        if rfc_info_short[value_man] == "":
            rfc_info_short[value_man] = "Отсутствует"
    return rfc_info_short
