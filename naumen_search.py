import requests
import json

import re

import configs                         # хранилище токена, ключей и паролей
import rfc_search                      # модуль поиска информации о rfc
import keyboards
import logs


def naumen_search(uuid):
    url = f"{configs.naumen['link']}/sd/services/rest/get/" + str(uuid) + \
          "?accessKey=" + str(configs.naumen['accessKey'])
    payload = {}
    headers = {'Cookie': configs.naumen['cookie'],
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
               }
    response_naumen = requests.request("GET", url=url, headers=headers,
                                       data=payload)
    # print(response5.json())
    code = response_naumen.status_code
    if code == 200:
        code_check = True
    else:
        code_check = False
    naumen_load = response_naumen.json()

    # пытаемся записать последний запрос в файл
    try:
        file_body = ''
        for k, v in naumen_load.items():
            file_body += f'{k} => {v}\n \n'
        # print(file_body)
        with open(r"logging\last_naumen_search.log", "w", encoding="utf-8") as file:
            file.write(file_body)
    except (Exception,):
        pass

    return naumen_load, code_check


def naumen_search_zni(zni):

    naumen_json = {"number": int(zni)}

    url = f"{configs.naumen['link']}/sd/services/rest/find/changeRequest$changeRequest/{naumen_json}" + \
          "?accessKey=" + str(configs.naumen['accessKey'])
    payload = {}
    headers = {'Cookie': configs.naumen['cookie'],
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
               }
    response_naumen = requests.request("GET", url=url, headers=headers,
                                       data=payload)

    answer = response_naumen.text
    answer = answer[1:-1]
    naumen_load = json.loads(answer)

    code = response_naumen.status_code
    if code == 200:
        code_check = True
    else:
        code_check = False

    return naumen_load, code_check


def naumen_serch_pb(number_pb):
    """
    Функция для поиска информации по заявке на основе номера запроса системы
    :param number_pb: номер запроса в формате serviceCall$1774672498
    :return: словарь с полученными данными
    """
    url = f"{configs.naumen['link']}/sd/services/rest/get/{number_pb}" + \
          "?accessKey=" + str(configs.naumen['accessKey'])
    payload = {}
    headers = {'Cookie': configs.naumen['cookie'],
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
               }
    response_naumen = requests.request("GET", url=url, headers=headers,
                                       data=payload)

    answer = response_naumen.text
    # answer = answer[1:-1]
    json_dump = json.loads(answer)
    # for k, v in json_dump.items():
    #     print(f'{k} => {v}\n \n')
    return json_dump


def naumen_search_zni_for_bank(json_number, change_request):
    """
    Функция для поиска банковских работ по номеру ЗНИ в системе банка.
    :param json_number: Словарь типа {"number": 15734}, где значение ключа - номер работ
    :param change_request: Тип запроса в систему
    :return: Ответ api от серверов банка
    """
    url = f'{configs.naumen["link"]}/sd/services/rest/find/{change_request}/{json_number}' + \
          "?accessKey=" + str(configs.naumen['accessKey'])
    headers = {'Cookie': configs.naumen['cookie'],
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
               'Content-Type': 'application/json;charset=UTF-8'
               }
    response_naumen = requests.request("GET", url=url, headers=headers)

    return response_naumen.text


def naumen_creator_message(client, number_zni, message, us_id, us_name, us_surname, username, protect_content_check):
    """
    Функция формирования сообщения для ответа на запрос зни в банке
    :param client: Соединение с телеграм
    :param number_zni: Номер зни в банке
    :param message: блок сообщений
    :param us_id: id пользователя
    :param us_name: имя пользователя
    :param us_surname: фамилия пользователя
    :param username: никнейм пользователя
    :param protect_content_check: проверка на блокировку
    :return: процедура
    """
    logs.log_pass(us_id, 'Запрос', f' ЗНИ {number_zni}')
    json_dump = naumen_search_zni_bank(number_zni)

    # Проверка на работы infosystem jet. Если есть - работаем по алгоритму infosystem jet
    result_search = re.search(r'\d{4}/202\d', json_dump["shortTitle"])
    if result_search is not None:
        task = result_search.group(0)
        rfc_search.search_rfc_main(client, task, message, us_id, us_name, us_surname, username, protect_content_check)
        return

    link_name_rfc = f"<a href='{configs.naumen['link']}/sd/operator/#uuid:" + \
                    str(json_dump["UUID"]) + "'><b>Ссылка Naumen</b></a>"

    # статус работ
    status_naumen, status_naumen_check_closed = status_naumen_correct(json_dump["state"])
    # детальный статус при закрытии работ
    detail_status_rfc_bank = json_dump["procCodeClose"]
    if detail_status_rfc_bank is not None:
        detail_status_bank = "Результат работ: <b><code>" + \
                             str(detail_status_rfc_bank["title"]) + "</code></b>\n"
    else:
        detail_status_bank = ""

    answer = f'<code>ЗНИ {json_dump["number"]}: {json_dump["shortTitle"]}</code>\n' + \
             f'● {link_name_rfc}\n \n' + \
             f'Task: <code>{json_dump["RequestNumber"]}</code>\n' + \
             f'Статус в банке: <b><code>{status_naumen}</code></b>\n{detail_status_bank}\n' + \
             f'Системы ЗНИ: <code>{json_dump["systemZNI"]}</code>\n' + \
             f'Инициатор: <code>{json_dump["Initiator"]}</code>\n' + \
             f' \n' + \
             f'Дата регистрации: <code>{json_dump["creationDate"]}</code>\n' + \
             f'Дата проведения: <code>{json_dump["beginDate"]}</code>\n'
    client.send_message(message.chat.id, answer, parse_mode="html",
                        reply_markup=keyboards.bank_zni_message_keyboard(json_dump["UUID"]),
                        protect_content=protect_content_check)
    return


def naumen_search_zni_bank(number_zni):
    """
    Функция принимает номер ЗНИ, выполняет подключение к Naumen, и возвращает json дамп
    :param number_zni: Номер работ в банке
    :return: json с информацией по работам
    """
    naumen_json = {"number": number_zni}

    answer = naumen_search_zni_for_bank(naumen_json, 'changeRequest$changeRequest')
    if answer == '[]':
        answer = naumen_search_zni_for_bank(naumen_json, 'changeRequest$changeErr')

    answer = answer[1:-1]
    json_dump = json.loads(answer)

    # пытаемся записать последний запрос в файл
    try:
        file_body = ''
        for k, v in json_dump.items():
            file_body += f'{k} => {v}\n \n'
        # print(file_body)
        with open(r"logging\last_naumen_search.log", "w", encoding="utf-8") as file:
            file.write(file_body)
    except (Exception,):
        pass

    return json_dump


def status_naumen_correct(status_naumen_first):
    status_naumen_check_closed_b = False
    status_naumen_right = None
    if str(status_naumen_first) == "registered":
        status_naumen_right = "🔵 Зарегистрирован"
        # просто создан номер
    elif str(status_naumen_first) == "resolved":
        status_naumen_right = "🟡 Закрытие"
        # проверка результата работ и процесс закрытие
    elif str(status_naumen_first) == "closed":
        status_naumen_right = "⚫️ Закрыт"
        # закрыт, он и в африке закрыт
        status_naumen_check_closed_b = True
    elif str(status_naumen_first) == "checking":
        status_naumen_right = "🟡 Проверка и назначение"
        # проверка ЗНИ и определение исполнителей со стороны банка
    elif str(status_naumen_first) == "waiting":
        status_naumen_right = "🔴 Обновление запроса на изменение"
        # Внесение информации и ожидание новых. Доступно редактирование данных
    elif str(status_naumen_first) == "test":
        status_naumen_right = "🟣 Анализ и оценка внедренного Изменения"
        # После проведение работ оценка изменения перед закрытием.
        # Появляется возможность указать детальный статус
    elif str(status_naumen_first) == "purpose":
        status_naumen_right = "🟡 Передача плана работ исполнителю"
        # оно согласовано и планируется время
    elif str(status_naumen_first) == "intCAB":
        status_naumen_right = "🟡 Очный САВ"
        # непонятно
    elif str(status_naumen_first) == "implementation":
        status_naumen_right = "🔴 Контроль реализации"
        # все понятно
    elif str(status_naumen_first) == "analysis":
        status_naumen_right = "🟢 Планирование и анализ ЗНИ"
        # после проведения экспертизы и до определения согласующих
    elif str(status_naumen_first) == "negotiating":
        status_naumen_right = "🟡 Согласование изменения"
        # согласование
    elif str(status_naumen_first) == "opinion":
        status_naumen_right = "🟢 Подготовка экспертных заключений"
        # первый этап согласование
    elif str(status_naumen_first) == "plan":
        status_naumen_right = "🟢 Консолидация экспертных заключений"
    # status_naumen_right = f'<code>{status_naumen_right}</code>'
    return status_naumen_right, status_naumen_check_closed_b
