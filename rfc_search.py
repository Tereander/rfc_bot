# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------

import time
import types
import requests
import random
import json
from datetime import datetime
from typing import Union

# ----------------------------------------------------------------------------------------------------------------------

from telebot import types
from urllib3 import disable_warnings, exceptions

# ----------------------------------------------------------------------------------------------------------------------

import neuron                      # работа со строкой
import configs                     # хранилище токена, ключей и паролей
import firewall_mars               # фаервол
import color_bars                  # цветной статус бар
import clues                       # блок с текстом подсказок
import postgres_init               # подключение к бд
import naumen_search               # модуль поиска в банке
import logs                        # модуль записи лога
import admins                      # блок работы с админами
import errors                      # блок работы с ошибкой
import personality_module          # модуль личности


def deep_and_hybrid_search(client: any, deep_search: str, message: dict) -> Union[bool, str, list]:
    """
    Функция вызывается когда по базовому запросу информация не была найдена.
    Система принимает запрос пользователя, разбивает на слова и делает более глубокий поиск,
    проверяя дополнительные поля в плане, а также меняет слова местами.
    :param client: Соединение с сервером telegram
    :param deep_search: запрос в несколько слов для глубокого поиска
    :param message: словарь с данными от пользователя telegram
    :return: 1 - проверка, что работы нашлись,
    2 - общий список ответа от сервера,
    3 - список словарей с совпадениями
    """
    forward_message = message.chat.id
    deep_search_list = deep_search.split()
    answer_list = []

    endpoint = f"{configs.auth_1c['link']}/ws/RFC_Details/rfc.1cws"
    body = '<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope' \
           f'/" xmlns:jet="{configs.auth_1c["link"]}">' \
           '<x:Header/><x:Body><jet:GetDetails><jet:Number>' + str(deep_search_list[0]) + \
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
    rfc_info = response.text

    rfc_info_clear = rfc_info.replace(
        '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">', ''
    )
    rfc_info_clear = rfc_info_clear.replace('<soap:Body>', '')
    rfc_info_clear = rfc_info_clear.replace(
        f'<m:GetDetailsResponse xmlns:m="{configs.auth_1c["link"]}">', ''
    )
    rfc_info_clear = rfc_info_clear.replace('<m:return xmlns:xs="http://www.w3.org/2001/XMLSchema"', '')
    rfc_info_clear = rfc_info_clear.replace('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">', '')
    rfc_info_clear = rfc_info_clear.replace('</m:return>', '')
    rfc_info_clear = rfc_info_clear.replace('</m:GetDetailsResponse>', '')
    rfc_info_clear = rfc_info_clear.replace('</soap:Body>', '')
    rfc_info_clear = rfc_info_clear.replace('</soap:Envelope>', '')
    rfc_info_clear = rfc_info_clear.replace('\r\n\t\t\t\t\t', '')
    rfc_info_clear = rfc_info_clear.replace('\r\n\t\t\t\t', '')
    rfc_info_clear = rfc_info_clear.replace('\r\n\t\t\t', '')
    rfc_info_clear = rfc_info_clear.replace('\r\n\t\t', '')
    rfc_info_clear = rfc_info_clear.replace('\r\n\t', '')
    result_list = rfc_info_clear.split('(_|_)')

    # если информация не найдена
    if ("Для указанного номера RFC данных не найдено..." in rfc_info_clear or
            "Не указан номер RFC..." in rfc_info_clear):
        return False, rfc_info, answer_list
    else:
        for el in result_list:
            rfc_info_clear = json.loads(el)  # загрузка обработанной строки в json

            answer_list.append(rfc_info_clear)
            for deep_search_el in deep_search_list:
                if deep_search_el not in (str(rfc_info_clear["Название"].lower())
                                          or str(rfc_info_clear["Описание"].lower())
                                          or str(rfc_info_clear["Цель"].lower())):
                    answer_list.remove(rfc_info_clear)
                    break
        if len(answer_list) == 0:
            return False, rfc_info, answer_list
        else:
            client.send_chat_action(forward_message, action="typing")
            return True, rfc_info, answer_list


def search_rfc_main(
        client: any, task: str, message: dict, us_id: int,
        us_name: str, us_surname: str, username: str, protect_content_check: bool) -> None:
    """
    Основная функция для поиска и вывода информации об rfc.
    Функция принимает множество параметров, подключается к ИС 1С,
    Naumen проверяет данные, формирует ответ и созависимость.
    Дополнительно вызывает клавиатуру и записывает лог
    :param client: соединение с серверами telegram
    :param task: запрос пользователя для поиска
    :param message: словарь с данными о пользователе
    :param us_id: id пользователя в telegram
    :param us_name: имя пользователя
    :param us_surname: фамилия пользователя
    :param username: никнейм пользователя
    :param protect_content_check: проверка на пересылку и копирование
    :return: процедура
    """
    cursor, conn = postgres_init.postgres_init()
    time_now = datetime.now()
    forward_message = message.chat.id
    rfc_info_check = True
    answer_list_deep = None
    try:
        # шутим шутки :)
        personality_module.personality(message, client)

        # print(protect_content_check)
        # cursor, conn = postgres_init.postgres_init()
        # поменяй и в callback
        client.send_chat_action(forward_message, action="typing")
        # Записываем данные о том кто и что ищет в журнал логов
        # current_datetime = datetime.now()
        full_name = firewall_mars.id_in_name(us_id)
        logs.log_pass(us_id, 'Запрос', f'{task}')

        # код поиска и вывода - Создаем клиент
        # ssl._create_default_https_context = ssl.create_default_context()
        endpoint = f"{configs.auth_1c['link']}/ws/RFC_Details/rfc.1cws"
        body = '<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope' \
               f'/" xmlns:jet="{configs.auth_1c["link"]}">' \
               '<x:Header/><x:Body><jet:GetDetails><jet:Number>' + str(task) + \
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
        rfc_info = response.text

        # если информация не найдена
        if ("Для указанного номера RFC данных не найдено..." in rfc_info or
                "Не указан номер RFC..." in rfc_info):
            # пробуем гибридный поиск
            client.send_chat_action(forward_message, action="typing")
            deep_and_hybrid_search_message = client.send_message(
                forward_message,
                '⚠️ Извините, информация по вашему запросу <b>не найдена в базе данных.</b> '
                'Однако бот будет пытаться найти схожие данные по контексту. '
                'Пожалуйста, помните, что <b>не всё найденное может быть полезным '
                'или совпадать с вашим запросом</b>',
                parse_mode="html"
            )
            rfc_info_check, rfc_info, answer_list_deep = deep_and_hybrid_search(client, task, message)
            if rfc_info_check is False:
                # если информация не найдена
                client.delete_message(message.chat.id, message_id=deep_and_hybrid_search_message.message_id)

                reaction_type_not_answer = ["🤷‍♂", "🤷", "🤷‍♀", '👍']
                client.set_message_reaction(message.chat.id, message_id=message.message_id,
                                            reaction=[types.ReactionTypeEmoji(random.choice(reaction_type_not_answer))],
                                            is_big=True
                                            )
                answer_text_rfc_status = "⚠ RFC не найден, проверьте данные.\n"
                client.send_chat_action(forward_message, action="typing")
                client.send_message(forward_message, str(answer_text_rfc_status),
                                    parse_mode="html", protect_content=protect_content_check)
                postgres_init.rfc_number(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                         username=username, search_rfc=0, last_rfc_number=task)
                logs.log_pass(us_id, 'Команда', f'Неизвестный номер RFC - {task}')
                cursor.execute(f'SELECT advice FROM advice_rfc WHERE user_id = {us_id}')
                advice = cursor.fetchone()[0]
                if advice == "advice on":
                    clue = "Формат поиска"
                    clue_answer = clues.clue_info(clue)
                    client.send_message(forward_message, str(clue_answer),
                                        parse_mode="html", protect_content=protect_content_check)
                return
        # если информация не найдена
        if rfc_info_check is True and answer_list_deep is None:
            rfc_info = rfc_info.replace('<soap:Envelope xmlns:soap'
                                        '="http://schemas.xmlsoap.'
                                        'org/soap/envelope/">', '')
            rfc_info = rfc_info.replace('<soap:Body>', '')
            rfc_info = rfc_info.replace(f'<m:GetDetailsResponse xmlns:m="{configs.auth_1c["link"]}">', '')
            rfc_info = rfc_info.replace('<m:return xmlns:xs="http://www.w3.org'
                                        '/2001/XMLSchema"', '')
            rfc_info = rfc_info.replace('xmlns:xsi="http://www.w3.org/2001/'
                                        'XMLSchema-instance">', '')
            rfc_info = rfc_info.replace('</m:return>', '')
            rfc_info = rfc_info.replace('</m:GetDetailsResponse>', '')
            rfc_info = rfc_info.replace('</soap:Body>', '')
            rfc_info = rfc_info.replace('</soap:Envelope>', '')
            rfc_info = rfc_info.replace('\r\n\t\t\t\t\t', '')
            rfc_info = rfc_info.replace('\r\n\t\t\t\t', '')
            rfc_info = rfc_info.replace('\r\n\t\t\t', '')
            rfc_info = rfc_info.replace('\r\n\t\t', '')
            rfc_info = rfc_info.replace('\r\n\t', '')
            result = rfc_info.split('(_|_)')
        else:
            result = answer_list_deep

        if len(result) == 1:
            rfc_info = json.loads(result[0])  # загрузка обработанной строки в json

            # пытаемся записать последний запрос в файл
            try:
                file_body = ''
                for k, v in rfc_info.items():
                    file_body += f'{k} => {v}\n \n'
                # print(file_body)
                with open(r"logging\last_1c_search.log", "w", encoding="utf-8") as file:
                    file.write(file_body)
            except (Exception,):
                pass

            # перебор словаря по значениям и замена пустых данных на отсутствие
            for value_man in rfc_info.keys():
                if rfc_info[value_man] == "":
                    rfc_info[value_man] = "Отсутствует"
            # если включено, показывать только первые 200 символов
            # print(rfc_info)
            try:
                cursor.execute(f'SELECT stop200 FROM len_200 WHERE user_id = {us_id}')
                stop200 = cursor.fetchone()[0]
            except (Exception,):
                stop200 = "True"
            stop200_check = False
            if stop200 == "True":
                if len(rfc_info["Описание"]) > 200:
                    rfc_info["Описание"] = str(rfc_info["Описание"][:200]) + " и т.д."
                    stop200_check = True
                if len(rfc_info["Цель"]) > 200:
                    rfc_info["Цель"] = str(rfc_info["Цель"][:200]) + " и т.д."
                    stop200_check = True
                if len(rfc_info["ЗатронутыеСистемы"]) > 200:
                    rfc_info["ЗатронутыеСистемы"] = str(rfc_info["ЗатронутыеСистемы"][:200]) + \
                                                    " и т.д."
                    stop200_check = True
                if len(rfc_info["СерверыОборудование"]) > 200:
                    rfc_info["СерверыОборудование"] = str(rfc_info["СерверыОборудование"][:200]) + \
                                                      " и т.д."
                    stop200_check = True

            # пустая строка типа даты в 1с - не пустая,
            # заменяем значение на читаемое - отсутствует
            # global time_to_work
            start_work = str(rfc_info["ДатаНачалаРабот"])
            if (str(rfc_info["ДатаНачалаРабот"]) == "01.01.0001 0:00:00" or
                    str(rfc_info["ДатаОкончанияРабот"]) == "01.01.0001 0:00:00"):
                time_to_work = "Не указано"
            else:
                try:
                    start_work = datetime.strptime(str(rfc_info["ДатаНачалаРабот"]),
                                                   '%d.%m.%Y %H:%M:%S')
                    finish_work = datetime.strptime(str(rfc_info["ДатаОкончанияРабот"]),
                                                    '%d.%m.%Y %H:%M:%S')
                    start_work = start_work.strftime("%H:%M %d.%m.%Y")
                    finish_work = finish_work.strftime("%H:%M %d.%m.%Y")
                except (Exception,):
                    start_work = str(rfc_info["ДатаНачалаРабот"])
                    finish_work = str(rfc_info["ДатаОкончанияРабот"])
                time_to_work = str(start_work) + " - " + str(finish_work)
            # определяем task или проект
            if "task" in str(rfc_info["TASK"]).lower():
                task_project = "Task"
                # task_init = "/"
            else:
                task_project = "Проект"
                # task_init = ""

            status_cl, status_cl_sm = color_bars.status_color(str(rfc_info["Статус"]))
            # ------------------------------------------------------------------------------------------------------
            # СПИСОК ЗАКРЫТЫХ СТАТУСОВ ПРИ КОТОРЫХ ОЦЕНКУ ПОКАЗЫВАТЬ НЕ НУЖНО
            closed_state = [
                "Согласовано",
                "Не согласовано",
                "Отменено",
                "Выполнено успешно",
                "Завершены откатом",
                "Закрыто",
                "Согласованно (SRFC)"
            ]
            block_estimate = False
            for i in closed_state:
                if str(rfc_info["Статус"]) == i:
                    block_estimate = True
            # ------------------------------------------------------------------------------------------------------
            ispl = ""
            st_bnk = ""
            tm_rfc_bnk = ""
            name_1c_st = "Статус"
            # global naumen_load
            naumen_load = None
            status_naumen = None
            full_time_work = None
            # ИНТЕГРАЦИЯ С НАУМЕН
            # ------------------------------------------------------------------------------------------------------
            code_check = None
            if str(rfc_info["УИД_ЗНИ"]) != "Отсутствует":
                # получаем ответ из naumen
                naumen_load, code_check = naumen_search.naumen_search(rfc_info["УИД_ЗНИ"])
            if str(rfc_info["УИД_ЗНИ"]) != "Отсутствует" and code_check is True:
                # запись action
                # us_action = "Запрос Naumen: "+str(naumen_load["title"])
                # user_action(us_action, us_id)
                # работа со временем
                start_work = naumen_load["beginDate"]
                finish_work = naumen_load["deadline"]
                if start_work is None or finish_work is None:
                    full_time_work = "Не указано"
                else:
                    start_work = datetime.strptime(str(start_work), '%Y.%m.%d %H:%M:%S')
                    finish_work = datetime.strptime(str(finish_work), '%Y.%m.%d %H:%M:%S')
                    start_work = start_work.strftime("%H:%M %d.%m.%Y")
                    finish_work = finish_work.strftime("%H:%M %d.%m.%Y")
                    full_time_work = str(start_work) + " - " + str(finish_work)

                # number_rfc_bank = str(naumen_load["number"])

                # работа со статусами naumen
                # global status_naumen_check_closed

                status_naumen, status_naumen_check_closed = naumen_search.status_naumen_correct(
                    naumen_load["state"]
                )

                # если работы закрыты не показывать кнопку согласования
                # if status_naumen_check_closed == True:
                #    keyboard.add(item2)
                # else:
                #    keyboard.add(item1, item2)
                # keyboard.add(item1, item2)
                # keyboard.add(item3)
                # детальный статус при закрытии работ
                detail_status_rfc_bank = naumen_load["procCodeClose"]
                if detail_status_rfc_bank is not None:
                    detail_status_bank = "Результат работ: <b><code>" + \
                                         str(detail_status_rfc_bank["title"]) + "</code></b>\n"
                else:
                    detail_status_bank = ""

                # ora = neuron.detail_naumen_search(str(naumen_load["state"]))
                # cl_bar = color_bar.color_bar(ora)
                ########
                # check_ora_status = ""
                # if not status_naumen_check_closed:
                #     check_ora_status = "Оценка RFC: <b>~ " + str(ora) + " %</b>\n" + \
                #                        str(cl_bar)

                ispl = f'Исполнители: <b><code>{naumen_load["executorZNI"]}</code></b>\n \n'
                st_bnk = "Статус в банке: <b><code>" + str(status_naumen) + "</code></b>\n" + \
                         str(detail_status_bank)
                tm_rfc_bnk = "Время работ в банке: <b><code>" + full_time_work + "</code></b>\n"

                name_1c_st = "Статус в 1С"
                # КОНЕЦ ИНТЕГРАЦИЯ С НАУМЕН

            answer_text_rfc_status = (f'{name_1c_st}: <code><b>{status_cl}</b></code>\n'
                                      f'{st_bnk}'
                                      f'{task_project}: <code><b>{rfc_info["TASK"]}</b></code>'
                                      f' \n'
                                      f'Куратор: <b><code>{rfc_info["Куратор"]}</code></b>\n'
                                      f'{ispl}'
                                      f'Время работ: <b><code>{time_to_work}</code></b>\n'
                                      f'{tm_rfc_bnk}')
            # срочность работ
            sr_n = rfc_info["Срочный"]
            if sr_n:
                answer_text_rfc_status = "<b>⚠️ Внимание! " + \
                                         "Срочные работы</b>\n \n" + \
                                         answer_text_rfc_status
                sr_n = True

            try:
                cursor.execute(f'SELECT grade_el FROM grade_el_table WHERE user_id = {us_id}')
                grade_el_table_zn = cursor.fetchone()[0]
            except (Exception,):
                grade_el_table_zn = "True"
            if grade_el_table_zn == "True" and block_estimate is False:
                ora = neuron.estimate(rfc_info["Статус"], start_work, rfc_info["УИД_ЗНИ"])
                cl_ora = color_bars.color_bar(ora)
                answer_text_rfc_status += " \n" + \
                                          f"Вероятность реализации RFC: <code><b>~ {ora} %</b></code>\n" + \
                                          f"{cl_ora} \n"

            # проверяем число ли в переменной Downtime и если да,
            # добавляем приписку мин.
            if rfc_info["Даунтайм"].isdigit():
                down_time = str(rfc_info["Даунтайм"]) + " мин."
            else:
                down_time = rfc_info["Даунтайм"]

            full_answer_text_rfc_status = (f'Описание: <code><b>{rfc_info["Описание"]}</b></code>\n'
                                           f'Цель: <code><b>{rfc_info["Цель"]}</b></code>\n'
                                           f' \n'
                                           f'Инициатор: <code><b>{rfc_info["Инициатор"]}</b></code>\n'
                                           f'Автор RFC: <code><b>{rfc_info["Автор"]}</b></code>\n'
                                           f' \n'
                                           f'Системы: <code><b>{rfc_info["ЗатронутыеСистемы"]}</b></code>\n'
                                           f'Работы проводятся на: <code>'
                                           f'<b>{rfc_info["СерверыОборудование"]}</b></code>\n'
                                           f' \n'
                                           f'Даунтайм: <code><b>{down_time}</b></code>\n'
                                           f'Дата создания: <code><b>{rfc_info["ДатаСозданияRFC"]}</b></code>\n')
            # number_bank = None

            if str(rfc_info["УИД_ЗНИ"]) != "Отсутствует" and code_check is True:
                full_name_rfc = str(naumen_load["title"])
            else:
                full_name_rfc = str(rfc_info["НомерRFC"]) + ' - ' + str(rfc_info["Название"])
            # убираем символы переноса строки

            full_name_rfc = full_name_rfc.replace("\n", "")
            full_name_rfc = full_name_rfc.replace("\r", "")
            full_name_rfc = full_name_rfc.replace("\r\n", "")

            # пробуем моно шрифт
            link_name_rfc = f'<code><b>{full_name_rfc}</b></code>'

            # link_name_rfc = "<a href='" + str(rfc_info["СсылкаWeb"]) + "'><b>" + \
            #                 str(full_name_rfc) + "</b></a>\n \n"
            # 1c ссылка
            link_name_rfc_1 = f"<a href='" + str(rfc_info["СсылкаWeb"]) + "'><b>Ссылка 1С</b></a>"
            if str(rfc_info["УИД_ЗНИ"]) != "Отсутствует" and code_check is True:
                link_name_rfc_2 = f"<a href='{configs.naumen['link']}/sd/operator/#uuid:" + \
                                  str(rfc_info["УИД_ЗНИ"]) + "'><b>Ссылка Naumen</b></a>"
                all_links = f'● {link_name_rfc_1}|{link_name_rfc_2}\n \n'
            else:
                all_links = f'● {link_name_rfc_1}\n \n'
            link_name_rfc = f'{link_name_rfc}\n{all_links}'

            answer_text_rfc_status = link_name_rfc + answer_text_rfc_status
            try:
                cursor.execute(f'SELECT view_rfc FROM full_view_rfc WHERE user_id = {us_id}')
                view_rfc = cursor.fetchone()[0]
            except (Exception,):
                view_rfc = "not full"

            if view_rfc == "full":
                answer_text_rfc_status = str(answer_text_rfc_status) + " \n" + str(full_answer_text_rfc_status)
            else:
                # отключаем подсказку о длине строки, если ответ в короткой форме
                stop200_check = False

            keyboard = types.InlineKeyboardMarkup(row_width=2)  # вывод кнопок в 1 колонку
            item1 = types.InlineKeyboardButton(text='🖥 Согласование 1С ',
                                               callback_data="Согласование 1c " + str(rfc_info["НомерRFC"]))
            item2 = types.InlineKeyboardButton(text='🖨 План работ 1C',
                                               callback_data='Скачать план ' + str(rfc_info["НомерRFC"]))

            item3 = types.InlineKeyboardButton(text='📲 Контакты исполнителей',
                                               callback_data='контакты ' + str(rfc_info["НомерRFC"]))

            item4 = types.InlineKeyboardButton(
                text='📱 WebApp 1С План работ',
                web_app=types.WebAppInfo('https://vm-aoterekhov-w10:5000/')
            )

            item8 = types.InlineKeyboardButton(text='🖥 Согласование Naumen',
                                               callback_data=f'Согласование Naumen {rfc_info["УИД_ЗНИ"]}')
            item9 = types.InlineKeyboardButton(text='🖨 План работ Naumen',
                                               callback_data=f'План работ Naumen {rfc_info["УИД_ЗНИ"]}')

            item5 = types.InlineKeyboardButton(text='🖨 Вложения',
                                               callback_data='Вложения ' + str(rfc_info["НомерRFC"]))
            item6 = types.InlineKeyboardButton(text='🗣 Обсуждение',
                                               callback_data='Обсуждение ' + str(rfc_info["НомерRFC"]))
            item7 = types.InlineKeyboardButton(text='📄 Условия RFC',
                                               callback_data='Условия работ ' + str(rfc_info["НомерRFC"]))
            item10 = types.InlineKeyboardButton(text='📄 Приложение RFC',
                                                callback_data='Приложение ' + str(rfc_info["НомерRFC"]))

            button_name_array = []
            activate_keyboard = False

            if str(rfc_info["УсловияПроведенияРабот"]) != "Отсутствует":
                button_name_array.append(item7)
                activate_keyboard = True

            if rfc_info["Вложения"]:
                button_name_array.append(item5)
                activate_keyboard = True

            if rfc_info["Приложение"]:
                button_name_array.append(item10)
                activate_keyboard = True

            if rfc_info["Обсуждения"]:
                button_name_array.append(item6)
                activate_keyboard = True
            # if rfc_info["Вложения"] != []:
            #    keyboard.add(item7, item2)
            if activate_keyboard:
                keyboard.add(*button_name_array)
            # добавляем кнопки в клавиатуру
            keyboard.add(item4)
            keyboard.add(item1, item2)
            if str(rfc_info["УИД_ЗНИ"]) != "Отсутствует":
                keyboard.add(item8, item9)
            keyboard.add(item3)
            # -----РАБОТАЕМ С ПОДКАЗКАМИ
            clue_answer_list = "HH,"

            clue = str(rfc_info["Статус"])
            clue, clue_body, clue_cod = clues.clue_bd(clue)
            clue_answer_list += clue_cod + ','

            if str(rfc_info["УИД_ЗНИ"]) != "Отсутствует":
                clue, clue_body, clue_cod = clues.clue_bd(status_naumen)
                clue_answer_list += clue_cod + ','

                if str(time_to_work) != str(full_time_work):
                    clue, clue_body, clue_cod = clues.clue_bd("Ошибка времени")
                    clue_answer_list += clue_cod + ','

            if sr_n is True:
                clue, clue_body, clue_cod = clues.clue_bd("Срочные работы")
                clue_answer_list += clue_cod + ','

            # цвет статуса
            clue, clue_body, clue_cod = clues.clue_bd(status_cl_sm)
            clue_answer_list += clue_cod + ','

            # сообщаем что время может изменится
            list_status_before_bank = ["Создание",
                                       "Оформление", "Разработка",
                                       "Технологическое согласование",
                                       "Планирование",
                                       "Доработка"]
            for list_status_before_bank_el in list_status_before_bank:
                if list_status_before_bank_el is str(rfc_info["Статус"]):
                    clue, clue_body, clue_cod = clues.clue_bd("Время проведения работ")
                    clue_answer_list += clue_cod + ','

            # вызов подсказки если больше 200 символов в тексте
            if stop200_check:
                clue, clue_body, clue_cod = clues.clue_bd("Длина ответа")
                clue_answer_list += clue_cod + ','

            if grade_el_table_zn == "True" and block_estimate is False:
                clue, clue_body, clue_cod = clues.clue_bd("Оценка RFC")
                clue_answer_list += clue_cod + ','
            # -----ЗАКАНЧИВАЕМ РАБОТАТЬ
            item10 = types.InlineKeyboardButton(text='💡 Подсказки',
                                                callback_data=clue_answer_list)
            # -----ПОДСКАЗКИ ПЛЮС ВЕБ ПЛАН РАБОТ -----------------------------------------------------------
            try:
                cursor.execute(f'SELECT advice FROM advice_rfc WHERE user_id = {us_id}')
                advice = cursor.fetchone()[0]
            except (Exception,):
                advice = "advice on"
            if advice == "advice on":
                keyboard.add(item10)
            else:
                pass

            # предупреждаем если не удалось подключиться к Naumen
            if str(rfc_info["УИД_ЗНИ"]) != "Отсутствует" and code_check is False:
                client.send_message(forward_message,
                                    '</>⚠️ Внимание! Ошибка подключения к ИС Naumen!</b>'
                                    ' \n'
                                    'Информация из банка не будет отображена',
                                    parse_mode="html",
                                    protect_content=protect_content_check)

            # проверка на длину строки
            if len(answer_text_rfc_status) > 4096:
                for x in range(0, len(answer_text_rfc_status), 4096):
                    client.send_chat_action(forward_message, action="typing")
                    client.send_message(forward_message,
                                        str(answer_text_rfc_status[x:x + 4096]),
                                        parse_mode="html", reply_markup=keyboard,
                                        protect_content=protect_content_check,
                                        link_preview_options=types.LinkPreviewOptions(is_disabled=True))
            else:
                client.send_chat_action(forward_message, action="typing")
                client.send_message(forward_message, str(answer_text_rfc_status),
                                    parse_mode="html", reply_markup=keyboard,
                                    protect_content=protect_content_check,
                                    link_preview_options=types.LinkPreviewOptions(is_disabled=True))
            # -----УВЕДОМЛЯЕМ ЕСЛИ СРОЧНЫЕ РАБОТЫ -------
            if sr_n:
                # Проверяем на закрытые статусы. Если один из закрытых статусов, не показываем уведомление
                closed_state_list = [
                    'Закрыто', 'Отменено', 'Завершены откатом', 'На паузе',
                    'Не согласовано', 'Выполнено успешно', 'Согласованно (SRFC)',
                ]
                if rfc_info["Статус"] not in closed_state_list:
                    text_sr_rfc = f'<b>⚠ Внимание! Произведен поиск по срочным работам!</b>\n' \
                                  f' \n' \
                                  f'🧑🏼‍💻 Пользователь: <b>{full_name}</b>\n' \
                                  f'⭕️ Номер срочных работ: <b>{rfc_info["НомерRFC"]}</b>\n' \
                                  f'🛑 Статус срочных работ: <b>{rfc_info["Статус"]}</b>\n'
                    # добавим статус в банке, если работы в банке
                    if str(rfc_info["УИД_ЗНИ"]) != "Отсутствует" and code_check is True:
                        text_sr_rfc += " \n" \
                                       f"Статус в банке: <b>{str(status_naumen)}</b>\n"
                    admins.admin_notification_message(client, text_sr_rfc)

            # time.sleep(1)
            return
        else:
            # модуль для красивого склонения
            st = str(len(result))  # превращаем число в строку
            # print(st)
            coincidence = None
            s = st[-1]  # берем последний символ
            if s == "1":
                coincidence = "совпадение"
            if s == "2" or s == "3" or s == "4":
                coincidence = "совпадения"
            if (s == "5" or s == "6" or s == "7" or s == "8" or
                    s == "9" or s == "0"):
                coincidence = "совпадений"
            if len(result) >= 10:
                s2 = st[-1]
                s1 = st[-2]
                s = s1 + s2
                if (s == "11" or s == "12" or s == "13" or
                        s == "14" or s == "15" or s == "16" or
                        s == "17" or s == "18" or s == "19" or s == "20"):
                    coincidence = "совпадений"
            client.send_message(forward_message, "Найдено " +
                                str(len(result)) + " " + str(coincidence) + ", по вашему запросу",
                                protect_content=protect_content_check)
            answer_message = ""
            button_name_array = []
            i = 0  # переменная для счетчика строк в сообщении
            # если больше сотни, показываем сотню
            if len(result) > 100:
                result = result[:100]
                client.send_message(forward_message,
                                    "Найдено более 100 сообщений. Будет показано только первый 100 вхождений",
                                    protect_content=protect_content_check)

            # выбираем переменную по которой будут ровняться список
            if len(result) > 10:
                x = 10
            else:
                x = len(result)
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            for result_el in result:
                if i == x:
                    '''
                    если предел по кол-ву строк пройден,
                    кидаем в пользователя часть списка
                    принудительная остановка поиска'''
                    i = 1
                    keyboard.add(*button_name_array)
                    client.send_message(forward_message,
                                        str(answer_message), parse_mode="html",
                                        reply_markup=keyboard, protect_content=protect_content_check,
                                        link_preview_options=types.LinkPreviewOptions(is_disabled=True))  #
                    keyboard = types.InlineKeyboardMarkup(row_width=3)
                    # вывод кнопок в 1 колонку

                    # загрузка обработанной строки в json
                    try:
                        rfc_info = json.loads(result_el)
                    except (Exception,):
                        rfc_info = result_el

                    # перебор словаря по значениям и замена пустых
                    # данных на отсутствие
                    for value_man in rfc_info.keys():
                        if rfc_info[value_man] == "":
                            rfc_info[value_man] = "Отсутствует"
                    # ######смайлы на статусы№№№№№№№№№№№№№№№№№№№№№№
                    status_cl, status_cl_sm = color_bars.status_color(str(rfc_info["Статус"]))
                    # ######смайлы на статусы№№№№№№№№№№№№№№№№№№№№№№

                    # #####################РАБОТАЕМ С НАЗВАНИЕМ И ССЫЛКАМИ###################################
                    if str(rfc_info["УИД_ЗНИ"]) != "Отсутствует":
                        full_name_rfc = 'ЗНИ № ' + str(rfc_info["НомерБанка"]) + ': ' + str(
                            rfc_info["НомерRFC"]) + ' - ' + str(rfc_info["Название"])

                        naumen_link = f"{configs.naumen['link']}/sd/operator/#uuid:" + \
                                      str(rfc_info["УИД_ЗНИ"])

                        link_name_rfc = "<a href='" + str(naumen_link) + "'><b>" + \
                                        str(full_name_rfc) + "</b></a>"
                    else:
                        full_name_rfc = str(rfc_info["НомерRFC"]) + ' - ' + str(rfc_info["Название"])

                        link_name_rfc = "<a href='" + str(rfc_info["СсылкаWeb"]) + "'><b>" + \
                                        str(full_name_rfc) + "</b></a>"
                    # #####################ЗАКАНЧИВАЕМ РАБОТАТЬ С НАЗВАНИЕМ И ССЫЛКАМИ###########################
                    # ####определяем task или проект
                    if "task" in str(rfc_info["TASK"]).lower():
                        # task_project = "Task"
                        task_init = "/"
                    else:
                        # task_project = "Проект"
                        task_init = " - "
                    # #####заканчиваем работать с task или проектом

                    answer_message = ""
                    button_name_array = []
                    button_name = types.InlineKeyboardButton(
                        text=str(status_cl_sm) + " " + str(rfc_info["НомерRFC"]),
                        callback_data=str(rfc_info["НомерRFC"]))
                    button_name_array.append(button_name)
                    answer_message += (f'{status_cl_sm} <b>{link_name_rfc}</b>\n'
                                       f'<b>(от {rfc_info["ДатаСозданияRFC"]}) '
                                       f'{task_init}{rfc_info["TASK"]}</b>\n \n')
                    time.sleep(1)
                else:
                    i = i + 1
                    # загрузка обработанной строки в json
                    try:
                        rfc_info = json.loads(result_el)
                    except (Exception,):
                        rfc_info = result_el

                    # перебор словаря по значениям и замена пустых данных на отсутствие
                    for value_man in rfc_info.keys():
                        if rfc_info[value_man] == "":
                            rfc_info[value_man] = "Отсутствует"
                    # перебор словаря по значениям и замена данных на отсутствие
                    for value_man in rfc_info.keys():
                        if rfc_info[value_man] == "":
                            rfc_info[value_man] = "Отсутствует"
                    # ######смайлы на статусы№№№№№№№№№№№№№№№№№№№№№№
                    status_cl, status_cl_sm = color_bars.status_color(str(rfc_info["Статус"]))
                    # ######смайлы на статусы№№№№№№№№№№№№№№№№№№№№№№
                    # #####################РАБОТАЕМ С НАЗВАНИЕМ И ССЫЛКАМИ###################################
                    if str(rfc_info["УИД_ЗНИ"]) != "Отсутствует":
                        full_name_rfc = 'ЗНИ № ' + str(rfc_info["НомерБанка"]) + ': ' + str(
                            rfc_info["НомерRFC"]) + ' - ' + str(rfc_info["Название"])

                        naumen_link = f"{configs.naumen['link']}/sd/operator/#uuid:" + \
                                      str(rfc_info["УИД_ЗНИ"])

                        link_name_rfc = "<a href='" + str(naumen_link) + "'><b>" + \
                                        str(full_name_rfc) + "</b></a>"
                    else:
                        full_name_rfc = str(rfc_info["НомерRFC"]) + ' - ' + str(rfc_info["Название"])

                        link_name_rfc = "<a href='" + str(rfc_info["СсылкаWeb"]) + "'><b>" + \
                                        str(full_name_rfc) + "</b></a>"
                    # #####################ЗАКАНЧИВАЕМ РАБОТАТЬ С НАЗВАНИЕМ И ССЫЛКАМИ###########################
                    # ####определяем task или проект
                    if "task" in str(rfc_info["TASK"]).lower():
                        # task_project = "Task"
                        task_init = "/"
                    else:
                        # task_project = "Проект"
                        task_init = " - "
                    # #####заканчиваем работать с task или проектом
                    # Button_name = "Кнопка: " + str(rfc_info["НомерRFC"])
                    button_name = types.InlineKeyboardButton(
                        text=str(status_cl_sm) + " " + str(rfc_info["НомерRFC"]),
                        callback_data=str(rfc_info["НомерRFC"]))
                    button_name_array.append(button_name)
                    # keyboard.row(Button_name)
                    answer_message += (f'{status_cl_sm} <b>{link_name_rfc}</b>\n'
                                       f'<b>(от {rfc_info["ДатаСозданияRFC"]})'
                                       f'{task_init}{rfc_info["TASK"]}</b>\n \n')
            if answer_message != "":
                keyboard.add(*button_name_array)
                client.send_message(forward_message,
                                    str(answer_message),
                                    parse_mode="html",
                                    reply_markup=keyboard,
                                    protect_content=protect_content_check)
    except Exception as er:
        full_name = firewall_mars.id_in_name(us_id)
        client.send_message(forward_message,
                            f"<b>⚠ Внимание! "
                            f"Произошла ошибка в работе системы поиска RFC!</b>\n"
                            f" \n"
                            f"🧑🏼‍💻 Пользователь: <b>{full_name}</b>\n"
                            f"⭕️ Запрос: <b>{task}</b>\n"
                            f"❌ Ошибка: <b>{er}</b>\n"
                            f" \n"
                            f"Перезагрузите систему, повторите запрос позднее, "
                            f"или обратитесь к администратору ресурса\n"
                            f"<b>(Администраторов мы уже уведомили)</b>",
                            parse_mode="html",
                            protect_content=protect_content_check)

        text_error_rfc = f'<b>⚠ Внимание! ' \
                         f'Произошла ошибка в работе системы поиска RFC!</b>\n' \
                         f' \n' \
                         f'🧑🏼‍💻 Пользователь: <b>{full_name}</b>\n' \
                         f'⭕️ Запрос: <b>{task}</b>\n' \
                         f'❌ Ошибка: <b>{er}</b>\n'
        admins.admin_notification_message(client, text_error_rfc)
        errors.error_bot(er, us_id, protect_content_check, client)

    postgres_init.rfc_number(user_id=us_id, user_name=us_name, user_surname=us_surname,
                             username=username, search_rfc=0, last_rfc_number=task)
    return
