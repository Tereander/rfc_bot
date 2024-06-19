# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------

import time
import types
import os.path
import requests
import json
import base64
import os.path
from datetime import datetime

# ----------------------------------------------------------------------------------------------------------------------

import re
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar

# ----------------------------------------------------------------------------------------------------------------------

import configs                         # хранилище токена, ключей и паролей
import calendars                       # работа с календарем
import rfc_statistic                   # веб сервис со списком работ по статусно
import settings_config                 # модуль работы с конфигом системы
import clues                           # блок с текстом подсказок
import postgres_init                   # подключение к бд\
import search_rfc_main_short           # краткий вариант функции поиска rfc
import naumen_search                   # модуль поиска в банке
import logs                            # модуль записи лога
import protect_content                 # модуль защиты от копирования
import keyboards                       # модуль работы с клавиатурой
import admins                          # блок работы с админами
import errors                          # блок работы с ошибкой
import rfc_search                      # модуль поиска информации о rfc
import neuron                          # модуль обработки строки и паттернов
import long_text                       # модуль где храним длинные текста
import file_processing

# ----------------------------------------------------------------------------------------------------------------------


def callback_main_bot(call, client, calendar_build, check_l_name):
    """
    Основная функция для обработки объектов типа callback, который передает
    telegram бот.
    :param call: Json объект типа callback, со всей информацией что передают сервера telegram.
    :param client: Соединение с ботом.
    :param calendar_build: Массив данных, который бот получает из 1С для формирования календаря.
    :param check_l_name: Boolean значение для отображения возможности показа списка работ
    :return: процедура
    """
    cursor, conn = postgres_init.postgres_init()

    us_id = call.from_user.id
    us_name = call.from_user.first_name
    us_surname = call.from_user.last_name
    username = call.from_user.username
    full_name_user = call.from_user.full_name

    protect_content_check = protect_content.protect_content_check_fn(us_id)

    if 'Согласование 1c' in call.data:
        # проверка, заполнен ли лист согласования
        agreements_body = None
        agreement = str(call.data)
        agreements_list = agreement.split()
        number_rfc = agreements_list[2]
        rfc_short_json = search_rfc_main_short.search_rfc_main_short(number_rfc)
        number_rfc = str(rfc_short_json["НомерRFC"])
        name_rfc = rfc_short_json["Название"]
        agreements_from_1c = rfc_short_json["Согласования"]

        if not agreements_from_1c:
            agreements_body = "● История согласования RFC отсутствует"
        if agreements_from_1c is not None:
            agreements_body = ""
            for s in agreements_from_1c:
                if str(s['Согласующий']) == '':
                    s['Согласующий'] = 'ИС 1С'

                name_list = str(s['Согласующий']).split(' ')
                name_agreements = str(name_list[0]) + ' ' + str(name_list[1])

                sm_color = ''

                if str(s['Результат']) == '':
                    s['Результат'] = 'Смена статуса'  # ⚪️
                    sm_color = '️⚪️ '
                if str(s['Результат']) == 'Согласовано':
                    s['Результат'] = 'Согласовано'  # 🟢
                    sm_color = '🟢 '
                if str(s['Результат']) == 'Не согласовано':
                    s['Результат'] = 'Не согласовано'  # 🔴
                    sm_color = '️🔴 '
                if str(s['Результат']) == 'Согласовано с замечаниями':
                    s['Результат'] = 'Согласовано с замечаниями'  # 🟡
                    sm_color = '️🟡 '

                if str(s['Комментарий']) != '':
                    s['Комментарий'] = '- ' + str(s['Комментарий'])
                if str(s['Комментарий']) == '':
                    s['Комментарий'] = '- Согласовано'

                agreements_body += "● <b>" + str(name_agreements) + "</b> " + \
                                   "(" + str(s['Период'][:-3]) + ")\n" + \
                                   str(sm_color) + "<b>" + str(s['Результат']) + "</b> " + \
                                   "<code>" + str(s['Комментарий']) + "</code>\n \n"

        answer_agreement = "История согласования RFC \n" + \
                           "<b>" + str(number_rfc) + " - " + str(name_rfc) + "</b>\n" + \
                           " \n" + str(agreements_body)

        # проверка на длину строки
        if len(answer_agreement) > 4096:
            for x in range(0, len(answer_agreement), 4096):
                client.send_chat_action(call.message.chat.id, action="typing")
                client.send_message(call.message.chat.id,
                                    str(answer_agreement[x:x + 4096]),
                                    parse_mode="html",
                                    protect_content=protect_content_check,
                                    link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        else:
            client.send_chat_action(call.message.chat.id, action="typing")
            client.send_message(call.message.chat.id, answer_agreement,
                                parse_mode="html",
                                protect_content=protect_content_check,
                                link_preview_options=types.LinkPreviewOptions(is_disabled=True))

        logs.log_pass(us_id, 'Действие', f'Из ИС "1С" получен список согласования {number_rfc}')
        return

    if 'Скачать план' in call.data:
        # global word_file
        # if word_file is None:
        #     old_request()
        #     return

        # agreements_body = None
        word_file_body = str(call.data)
        word_file_body_list = word_file_body.split()
        number_rfc = word_file_body_list[2]
        rfc_short_json = search_rfc_main_short.search_rfc_main_short(number_rfc)
        # speaking = rfc_info["Обсуждения"]
        # vlogs = rfc_info["Вложения"]
        # usl_work = rfc_info["УсловияПроведенияРабот"]
        st_rfc_1c = str(rfc_short_json["Статус"])
        # uuid = str(rfc_info["УИД_ЗНИ"])
        # number_rfc = str(rfc_info["НомерRFC"])
        # number_rfc_bank = rfc_info["НомерБанка"]
        name_rfc = str(rfc_short_json["Название"])
        # word_file = str(rfc_info["ФайлWord"])
        # agreements = rfc_info["Согласования"]
        word_file_document = rfc_short_json["ФайлWord"]

        # client.send_chat_action(call.message.chat.id, action = "typing")
        # client.send_message(call.message.chat.id, "Формирую план, ожидайте",
        # parse_mode="html", protect_content=protect_content_check)
        decoded = base64.b64decode(word_file_document)

        file_word_name = str(number_rfc) + " - " + str(name_rfc) + ".docx"
        file_word_name = file_word_name.replace("<", "_")
        file_word_name = file_word_name.replace(">", "_")
        file_word_name = file_word_name.replace(":", "_")
        file_word_name = file_word_name.replace('"', "_")
        file_word_name = file_word_name.replace("/", "_")
        file_word_name = file_word_name.replace('\n', '')
        file_word_name = file_word_name.replace('\r', '')
        file_word_name = file_word_name.replace('\r\n', '')
        file_word_name = file_word_name.replace('\\', '_')
        # file_word_name = file_word_name.replace('''\n''', '_')
        file_word_name = file_word_name.replace("|", "_")
        file_word_name = file_word_name.replace("?", "_")
        file_word_name = file_word_name.replace("*", "_")
        file_word_name = file_word_name.replace(",", " ")
        file_word_name = file_processing.sanitize_filename(file_word_name)
        file_word_name = r'files\\' + str(file_word_name)

        image_result = open(str(file_word_name), 'wb')
        # создание документа, доступного для записи, и запись результата
        # декодирования
        image_result.write(decoded)
        # добавить подпись к доку
        if str(st_rfc_1c) == "Финальное согласование":
            client.send_document(call.message.chat.id,
                                 open(str(file_word_name), "rb"),
                                 caption="RFC было отправлен в банк, данный план работ "
                                         "<b>может быть</b> не точный",
                                 parse_mode="html")
        else:
            client.send_document(call.message.chat.id, open(str(file_word_name), "rb"))

        image_result.close()
        os.remove(str(file_word_name))

        # full_user_name = firewall_mars.id_in_name(us_id)
        logs.log_pass(us_id, 'Действие', f'Из ИС "1С" скачан документ: {file_word_name}')

        # word_file = None
        # меню подсказки
        cursor.execute('SELECT advice FROM advice_rfc WHERE user_id = ' + str(us_id))
        advice = cursor.fetchone()[0]
        if advice == "advice on":
            clue_answer_check = False
            clue_answer_list = []

            if str(st_rfc_1c) == "Финальное согласование":
                clue_answer_check = True
                clue_answer = clues.clue_info("План работ 1C/Naumen")
                clue_answer_list.append(clue_answer)

            clue_answer_full = ""
            for clue_answer_el in clue_answer_list:
                clue_answer_full = clue_answer_full + clue_answer_el + " \n"
            clue_answer_full = clue_answer_full + clues.clue_answer_clue

            if clue_answer_check:
                client.send_message(call.message.chat.id,
                                    str(clue_answer_full),
                                    parse_mode="html",
                                    protect_content=protect_content_check)
        # uuid = None
        return
    if 'Вложения' in call.data:
        vlogs = str(call.data)
        vlogs_list = vlogs.split()
        number_rfc = vlogs_list[1]
        rfc_short_json = search_rfc_main_short.search_rfc_main_short(number_rfc)
        # speaking = rfc_info["Обсуждения"]
        # vlogs = rfc_info["Вложения"]
        # usl_work = rfc_info["УсловияПроведенияРабот"]
        # st_rfc_1c = str(rfc_info["Статус"])
        # uuid = str(rfc_info["УИД_ЗНИ"])
        # number_rfc = str(rfc_info["НомерRFC"])
        # number_rfc_bank = rfc_info["НомерБанка"]
        # name_rfc = str(rfc_info["Название"])
        # word_file = str(rfc_info["ФайлWord"])
        # agreements = rfc_info["Согласования"]
        vlogs = rfc_short_json["Вложения"]
        number_rfc = rfc_short_json["НомерRFC"]
        name_rfc = rfc_short_json["Название"]
        client.send_message(call.message.chat.id,
                            "У RFC <b>" + str(number_rfc) + " - " + str(name_rfc) + "</b> " +
                            "найдено вложений: " + str(len(vlogs)),
                            parse_mode="html",
                            protect_content=protect_content_check)
        for vg in vlogs:
            try:
                decoded = base64.b64decode(vg["Base64"])
                file_vlog_name = r'files\\' + str(vg["Название"])
                image_result = open(file_vlog_name, 'wb')
                # создание документа, доступного для записи, и запись результата
                # декодирования
                image_result.write(decoded)
                image_result.close()
                client.send_document(call.message.chat.id, open(file_vlog_name), "rb")

                os.remove(file_vlog_name)
            except Exception as er:
                client.send_message(call.message.chat.id,
                                    "Ошибка отправки файла: " + str(vg["Название"]) + "\n"
                                    "Обратитесь к администраторам системы или попробуйте позднее.\n"
                                    "(Администраторов об ошибке мы уведомили)",
                                    parse_mode="html",
                                    protect_content=protect_content_check
                                    )
                text_error_vlogs = f'<b>⚠ Внимание! ' \
                                   f'Произошла ошибка в выдаче вложения!</b>\n' \
                                   f' \n' \
                                   f'🧑🏼‍💻 Пользователь: <b>{full_name_user}</b>\n' \
                                   f'⭕️ Запрос: <b>{number_rfc}</b>\n' \
                                   f'❌ Имя сбойного файла: <b>{vg["Название"]}</b>\n'
                admins.admin_notification_message(client, text_error_vlogs)
                errors.error_bot(er, us_id, protect_content, client)
        return

    if 'контакты' in call.data:
        contact = str(call.data)
        contact_list = contact.split()
        number_rfc = contact_list[1]
        rfc_short_json = search_rfc_main_short.search_rfc_main_short(number_rfc)
        contact_user = rfc_short_json["Исполнители"]
        check_contact_send = False
        for el in contact_user:
            if el['Телефон'] != '':
                client.send_contact(call.message.chat.id,
                                    phone_number=el['Телефон'],
                                    first_name=el['ФИО']
                                    )
                check_contact_send = True
                if el['Почта'] != '':
                    client.send_message(call.message.chat.id,
                                        f"{el['ФИО']}:\n"
                                        f"<code>{el['Почта']}</code>\n"
                                        f"<code>{el['Телефон']}</code>",
                                        parse_mode="html")
        if not check_contact_send:
            client.send_message(call.message.chat.id, 'Отсутствуют доступные контакты для отправки')
        return

    if 'План работ Naumen' in call.data:
        # if naumen_load is None:
        #     old_request()
        #     return
        naumen_file_body = str(call.data)
        naumen_file_body_list = naumen_file_body.split()
        uuid_1c = naumen_file_body_list[3]
        naumen_load, code_check = naumen_search.naumen_search(uuid_1c)
        file_list_naumen = naumen_load["ContentFiles"]

        # Функция сохранения файла ЗНИ
        def download_file_base64(uuid_file):
            # print(str(uuid_file))
            url_file = f"{configs.naumen['link']}/sd/services/rest/exec?" + \
                       "accessKey=" + str(configs.naumen['accessKey']) + \
                       "&func=modules.sdRest.getFile&params=" + str(uuid_file) + ",user"
            payload_file = {}
            headers_file = {
                'Cookie': configs.naumen['cookie'],
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }

            response = requests.request("GET", url_file, headers=headers_file,
                                        data=payload_file)
            # print (response.text)
            response_json = json.loads(response.text)

            return response_json["content"]

        if len(file_list_naumen) > 1:
            client.send_message(call.message.chat.id,
                                "● Найдено файлов: " + str(len(file_list_naumen)) + ", загружаю.",
                                parse_mode="html", protect_content=protect_content_check)
        time.sleep(1)
        full_name_file = ""
        for i in file_list_naumen:
            # print("Первый файл : "+str(i))
            name_naumen_file = i['title']

            name_naumen_file = name_naumen_file.replace("\\", "")
            name_naumen_file = name_naumen_file.replace("\n", "")
            name_naumen_file = name_naumen_file.replace("\r", "")
            name_naumen_file = name_naumen_file.replace("\r\n", "")
            name_naumen_file = file_processing.sanitize_filename(name_naumen_file)

            full_name_file += name_naumen_file + ", "
            name_naumen_file = r'files\\' + str(name_naumen_file)
            # print("Имя: "+str(i['title']))
            file_id = i['UUID']
            # print("код файла: "+str(i['UUID']))
            file_id = file_id.replace("file$", "")
            tr = download_file_base64(file_id)
            decoded = base64.b64decode(tr)
            with open(name_naumen_file, "wb") as file:
                file.write(decoded)
                client.send_document(call.message.chat.id, open(str(name_naumen_file), "rb"))
            os.remove(str(name_naumen_file))

        logs.log_pass(us_id, 'Действие', f'Из Naumen скачан документ: {full_name_file}')
        return

    if 'Согласование Naumen' in call.data:

        naumen_expert_body = str(call.data)
        naumen_expert_body_list = naumen_expert_body.split()
        uuid_naumen = naumen_expert_body_list[2]
        naumen_load, code_check = naumen_search.naumen_search(uuid_naumen)

        # full_user_name = firewall_mars.id_in_name(us_id)
        logs.log_pass(us_id, 'Действие',
                      f'Из Naumen получен список согласования {naumen_load["title"]}')

        def tasks_exec():
            str_exec = ""

            def status_task_expert(task_expert_st_input):
                # task_expert_st_input = None
                if task_expert_st == "closed":
                    task_expert_st_input = "⚫️ Закрыт"
                if task_expert_st == "inprogress":
                    task_expert_st_input = "🟢 В работе"
                if task_expert_st == "registered":
                    task_expert_st_input = "🟢 Назначено"
                if task_expert_st == "accepted":
                    task_expert_st_input = "🟢 Согласовано"
                return task_expert_st_input

            for el in naumen_load["tasksExec"]:
                # print(str(i["UUID"]))
                url_task = f"{configs.naumen['link']}/sd/services/rest/get/" + \
                           str(el['UUID']) + "?accessKey=" + str(configs.naumen['accessKey'])
                payload_task = {}
                headers_task = {
                    'Cookie': configs.naumen['cookie'],
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                response = requests.request("GET", url_task, headers=headers_task, data=payload_task)
                # response.encoding = "utf-8"
                task_expert = response.json()
                # print(task_expert)
                expert_list = task_expert['respEmplFlex']

                if expert_list is not None:
                    # заменяем таски
                    task_expert_st = str(task_expert['state'])
                    new_status_task_expert = status_task_expert(task_expert_st)
                    # проверяем детальное решение
                    if task_expert['solution'] is not None:
                        description_solution = " - " + str(task_expert['solution'])
                        description_solution = description_solution.replace('</div>', "")
                        description_solution = description_solution.replace('<div>', "")
                        description_solution = description_solution.replace('&nbsp;', " ")
                        description_solution = re.sub(r'<[^>]*>', '', description_solution)
                    else:
                        description_solution = ""
                    # формируем сообщение
                    str_exec += '● ' + str(task_expert["respEmplFlex"]["title"]) + '\n' + \
                                '<code><b>' + str(new_status_task_expert) + '</b>' + str(
                        description_solution) + '</code>\n \n'
            return str_exec

        # список экспертов
        if naumen_load['experts'] is not None:
            info_approvers_list = "<b>➖ Задачи экспертам: </b>\n"
            info_exec_list = tasks_exec()
            if info_exec_list == "":
                info_exec_list = ""
            else:
                info_exec_list = info_approvers_list + info_exec_list + " \n"
        else:
            info_exec_list = ""

        # список согласующих
        task_n = naumen_load['negotTask']
        if task_n is not None:
            url = f"{configs.naumen['link']}/sd/services/rest/get/" + \
                  str(task_n['UUID']) + "?accessKey=" + str(configs.naumen['accessKey'])
            payload = {}
            headers = {
                'Cookie': configs.naumen['cookie'],
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
            response2 = requests.request("GET", url, headers=headers,
                                         data=payload)
            t2 = response2.json()
            info_approvers_list = "<b>➖ Список согласования:</b>\n"
            y = 0
            for i in t2["partFormResol"]:
                # print(i)
                url = f"{configs.naumen['link']}/sd/services/rest/get/" + \
                      str(t2["voteLinksTpl"][y]["UUID"]) + \
                      "?accessKey=" + str(configs.naumen['accessKey'])
                payload = {}
                headers = {
                    'Cookie': configs.naumen['cookie'],
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                response3 = requests.request("GET", url, headers=headers,
                                             data=payload)
                t3 = response3.json()
                # print(t3)
                description = re.sub(r'<[^>]*>', '', t3["description"])
                # делаем красивую иконку и кружок
                status_system_icon = str(t3["system_icon"]["title"])
                # определяем время согласования
                status_time = str(t3["stateStartTime"])
                status_time = datetime.strptime(str(status_time), '%Y.%m.%d %H:%M:%S')
                status_time = status_time.strftime("%H:%M %d.%m.%Y")

                if status_system_icon == "Отказано":
                    status_system_icon = "🔴 Отказано"
                if status_system_icon == "Согласовано":
                    status_system_icon = "🟢 Согласовано"
                # формируем сообщение
                info_approvers_list += "● " + str(t3["author"]["title"]) + \
                                       " <b>(" + str(status_time) + ")</b>\n" + \
                                       "<code><b>" + str(status_system_icon) + "</b> - " + \
                                       str(description) + "</code>\n \n"
                y += 1

            for i_el in t2["participants"]:
                info_approvers_list += "● " + str(i_el["title"]) + "\n" + \
                                       "<code><b>🟡 Ожидаем согласования</b></code>\n \n"
        else:
            info_approvers_list = ""

        # объединение ответа от согласования и экспертов
        full_answer_bank = info_exec_list + info_approvers_list
        if full_answer_bank == "":
            full_answer_bank = "<b>❎ Список согласующих не определен</b>"

        answer_text_rfc_status = "Согласование: <b>" + str(naumen_load["title"]) + "</b> \n" + \
                                 " \n" + str(full_answer_bank)

        # проверка на длину строки
        if len(answer_text_rfc_status) > 4096:
            for x in range(0, len(answer_text_rfc_status), 4096):
                client.send_chat_action(call.message.chat.id, action="typing")
                client.send_message(call.message.chat.id,
                                    str(answer_text_rfc_status[x:x + 4096]),
                                    parse_mode="html",
                                    protect_content=protect_content_check,
                                    link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        else:
            client.send_chat_action(call.message.chat.id, action="typing")
            client.send_message(call.message.chat.id, str(answer_text_rfc_status),
                                parse_mode="html",
                                protect_content=protect_content_check,
                                link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        return

    if 'Условия работ' in call.data:
        usl_works = str(call.data)
        usl_works_list = usl_works.split()
        number_rfc = usl_works_list[2]
        rfc_short_json = search_rfc_main_short.search_rfc_main_short(number_rfc)
        # speaking = rfc_info["Обсуждения"]
        # vlogs = rfc_info["Вложения"]
        usl_work = rfc_short_json["УсловияПроведенияРабот"]
        # st_rfc_1c = str(rfc_info["Статус"])
        # uuid = str(rfc_info["УИД_ЗНИ"])
        # number_rfc = str(rfc_info["НомерRFC"])
        # number_rfc_bank = rfc_info["НомерБанка"]
        # name_rfc = str(rfc_info["Название"])
        # word_file = str(rfc_info["ФайлWord"])
        # agreements = rfc_info["Согласования"]
        # vlogs = rfc_short_json["Вложения"]
        number_rfc = rfc_short_json["НомерRFC"]
        name_rfc = rfc_short_json["Название"]

        # full_user_name = firewall_mars.id_in_name(us_id)
        logs.log_pass(us_id, 'Действие', f'Запрошено условие для проведения работ {number_rfc}')

        full_usl_work = "Условия проведения работ " + \
                        "<b>" + str(number_rfc) + " - " + str(name_rfc) + "</b>\n" + \
                        " \n" + \
                        f'● <code>{usl_work}</code>'

        client.send_message(call.message.chat.id,
                            str(full_usl_work),
                            parse_mode="html", protect_content=protect_content_check)
        return

    if 'Обсуждение' in call.data:

        speaking = str(call.data)
        speaking_list = speaking.split()
        number_rfc = speaking_list[1]
        rfc_short_json = search_rfc_main_short.search_rfc_main_short(number_rfc)
        speaking = rfc_short_json["Обсуждения"]
        # vlogs = rfc_info["Вложения"]
        # usl_work = rfc_info["УсловияПроведенияРабот"]
        # st_rfc_1c = str(rfc_info["Статус"])
        # uuid = str(rfc_info["УИД_ЗНИ"])
        # number_rfc = str(rfc_info["НомерRFC"])
        # number_rfc_bank = rfc_info["НомерБанка"]
        # name_rfc = str(rfc_info["Название"])
        # word_file = str(rfc_info["ФайлWord"])
        # agreements = rfc_info["Согласования"]
        # vlogs = rfc_short_json["Вложения"]
        number_rfc = rfc_short_json["НомерRFC"]
        name_rfc = rfc_short_json["Название"]

        full_speaking_answer = "История обсуждения RFC \n" + \
                               "<b>" + str(number_rfc) + " - " + str(name_rfc) + "</b>\n" + \
                               " \n"
        for sp in speaking:
            full_speaking_answer += "● <b>" + str(sp['Период'][:-3]) + "</b> \n" + \
                                    str(sp['Отправитель']) + " ➡️ " + str(sp['Получатель']) + "\n" + \
                                    "<b>" + str(sp['ТекстСообщения']) + "</b>\n \n"
        # проверка на длину строки
        if len(full_speaking_answer) > 4096:
            for x in range(0, len(full_speaking_answer), 4096):
                client.send_chat_action(call.message.chat.id, action="typing")
                client.send_message(call.message.chat.id,
                                    str(full_speaking_answer[x:x + 4096]),
                                    parse_mode="html", protect_content=protect_content_check,
                                    link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        else:
            client.send_chat_action(call.message.chat.id, action="typing")
            client.send_message(call.message.chat.id, full_speaking_answer,
                                parse_mode="html", protect_content=protect_content_check,
                                link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        return

    if 'Приложение' in call.data:
        speaking = str(call.data)
        speaking_list = speaking.split()
        number_rfc = speaking_list[1]
        rfc_short_json = search_rfc_main_short.search_rfc_main_short(number_rfc)
        add_list = rfc_short_json["Приложение"]
        # vlogs = rfc_info["Вложения"]
        # usl_work = rfc_info["УсловияПроведенияРабот"]
        # st_rfc_1c = str(rfc_info["Статус"])
        # uuid = str(rfc_info["УИД_ЗНИ"])
        # number_rfc = str(rfc_info["НомерRFC"])
        # number_rfc_bank = rfc_info["НомерБанка"]
        # name_rfc = str(rfc_info["Название"])
        # word_file = str(rfc_info["ФайлWord"])
        # agreements = rfc_info["Согласования"]
        # vlogs = rfc_short_json["Вложения"]
        number_rfc = rfc_short_json["НомерRFC"]
        name_rfc = rfc_short_json["Название"]

        full_speaking_answer = "Приложение к RFC \n" + \
                               "<b>" + str(number_rfc) + " - " + str(name_rfc) + "</b>\n" + \
                               " \n" + \
                               f"{add_list}\n"

        # проверка на длину строки
        if len(full_speaking_answer) > 4096:
            for x in range(0, len(full_speaking_answer), 4096):
                client.send_chat_action(call.message.chat.id, action="typing")
                client.send_message(call.message.chat.id,
                                    str(full_speaking_answer[x:x + 4096]),
                                    parse_mode="html", protect_content=protect_content_check,
                                    link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        else:
            client.send_chat_action(call.message.chat.id, action="typing")
            client.send_message(call.message.chat.id, full_speaking_answer,
                                parse_mode="html", protect_content=protect_content_check,
                                link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        return

    # ПОИСК ПРИ НАЖАТИИ НА КНОПКУ, ИЗ КЛАВИАТУРЫ ВАРИАНТОВ
    result_number = re.search(neuron.pattern_5_callback,
                              call.data)
    if result_number is not None:
        result_number = result_number.group(0)
        # Записываем данные о том кто и что ищет в журнал логов
        rfc_search.search_rfc_main(client, result_number, call.message, us_id,
                                   us_name, us_surname, username, protect_content_check)
        return

    if call.data == 'Отсутствует':
        client.send_message(call.message.chat.id, "⚠ Информация о RFC отсутствует"
                                                  " и недоступна для просмотра.\n"
                                                  " \n"
                                                  "Возможно RFC находится в статусе <b>Создание</b> и "
                                                  "еще не зарегистрировано. "
                                                  "Повторите запрос позже", parse_mode="html",
                            protect_content=protect_content_check)
        cursor.execute(f'SELECT advice FROM advice_rfc WHERE user_id = {us_id}')
        advice = cursor.fetchone()[0]
        if advice == "advice on":
            clue = "Создание"
            clue_answer = clues.clue_info(clue)
            client.send_message(call.message.chat.id, str(clue_answer), parse_mode="html",
                                protect_content=protect_content_check)
        return

    if call.data == 'шаблоны':
        client.send_message(call.message.chat.id,
                            'Список шаблонов для работы\n'
                            ' \n'
                            f'● <code>{long_text.body_mailing}</code>\n'
                            ' \n'
                            f'● <code>{long_text.body_mailing_inaccessibility}</code>\n'
                            ' \n'
                            f'● <code>{long_text.body_mailing_dost}</code>\n',
                            protect_content=protect_content_check, parse_mode="html")
        return

    if call.data == 'направить рассылку':
        client.send_message(call.message.chat.id,
                            "Вы в данный момент находитесь в разделе отправки рассылок. \n"
                            "Сообщение, которое вы сейчас отправите, "
                            "будет использовано в качестве содержания рассылки. \n"
                            "Просим указать текст рассылки. Если вы хотите выйти из этого раздела, "
                            "введите команду /cancellation",
                            parse_mode="html",
                            protect_content=protect_content_check)

        postgres_init.rfc_number(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                 username=username, search_rfc=19, last_rfc_number="XXXX/202X")
        return

    if call.data == 'помощь при блоке':
        client.send_message(call.message.chat.id,
                            "● Почта отдела: <b>" + str(configs.email_name) + "</b>\n"
                                                                              "● Контакты отдела: <b>" + str(
                                configs.workers['rfc_manager1']['Ссылка']) + "</b>,"
                                                                             " <b>" + str(
                                configs.workers['rfc_manager2']['Ссылка']) + "</b>\n"
                                                                             ' \n' +
                            'Доступные инструкции: \n' +
                            str(configs.link['Инструкция бот']) + '\n' +
                            str(configs.link['Инструкция 1c']) + '\n', parse_mode="html",
                            protect_content=protect_content_check)
        return
    if call.data == 'регистрация 1с':
        client.send_chat_action(call.message.chat.id, action="typing")
        client.send_message(call.message.chat.id,
                            "Для регистрации введите имя пользователя "
                            "ИС 1С, в формате: <b>'Смирнов Александр'</b>\n",
                            parse_mode="html",
                            protect_content=protect_content_check)
        postgres_init.authentication_1c(user_id=us_id, user_login='', hash_password='',
                                        check_access=1, last_data=call.message.date)
        return
    if call.data == 'Запуск бота':
        markup = keyboards.menu_keyboard(us_id)
        client.send_chat_action(call.message.chat.id, action="typing")
        client.send_message(call.message.chat.id, "<b>Главное меню</b>\n"
                                                  " \n"
                                                  "Поиск информации, статус RFC, настройка фильтров системы.\n"
                                                  "Выбери интересующий тебя раздел.", reply_markup=markup,
                            parse_mode="html",
                            protect_content=protect_content_check)
        return
    if call.data == 'Предложить идею':
        client.send_chat_action(call.message.chat.id, action="typing")
        client.send_message(call.message.chat.id, "<b>Предложить идею</b>\n"
                                                  " \n"
                                                  "Опишите ваше предложение или идею. "
                                                  "Ваше сообщение получат администраторы системы.\n",
                            parse_mode="html", protect_content=protect_content_check)
        postgres_init.rfc_number(user_id=us_id, user_name=us_name, user_surname=us_surname, username=username,
                                 search_rfc=9, last_rfc_number="XXXX/202X")
        return
    if call.data == 'Ознакомление с ботом':
        logs.log_pass(us_id, 'Действие', f'Ознакомление с ботом')

        client.send_chat_action(call.message.chat.id, action="typing")
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('✔ Ознакомлен',
                                           callback_data='Запуск бота')
        markup.add(item1)
        client.send_message(call.message.chat.id,
                            str(long_text.familiarization),
                            reply_markup=markup, parse_mode="html", protect_content=protect_content_check)
        return
    if call.data == 'Статусы RFC списком':
        answer_rfc_statistic = rfc_statistic.simple_rfc_statistic()
        # print(answer_rfc_statistic)
        client.send_message(call.message.chat.id,
                            answer_rfc_statistic,
                            parse_mode="html", protect_content=protect_content_check)
        return
    if call.data == 'Карточка пользователя':
        # premium_ch = 'Не определена'
        if call.from_user.is_premium:
            premium_ch = 'Подключена'
        else:
            premium_ch = 'Отключена'

        if call.message.chat.username is not None:
            username = f'@{call.message.chat.username}'
        else:
            username = "Отсутствует"

        cursor.execute(f'SELECT user_login FROM authentication_1c WHERE user_id = {us_id}')
        user_login = cursor.fetchone()[0]
        cursor.execute(f'SELECT department FROM initialization_user WHERE user_id = {us_id}')
        department = cursor.fetchone()[0]
        cursor.execute(f'SELECT guid FROM initialization_user WHERE user_id = {us_id}')
        guid_1c = cursor.fetchone()[0]

        answer_user_card = f'<b>📰 Карточка пользователя</b>\n' \
                           '\n' \
                           f'● ID пользователя: <code>{call.message.chat.id}</code>\n' \
                           f'● Имя пользователя: <code>{user_login}</code>\n' \
                           f'● Отдел пользователя: <code>{department}</code>\n' \
                           f'● GUID пользователя: <code>{guid_1c}</code>\n' \
                           f'\n' \
                           f'● Никнейм пользователя: <b>{username}</b>\n' \
                           f'● Язык пользователя: <b>{call.from_user.language_code}</b>\n' \
                           f'● Премиум подписка: <b>{premium_ch}</b>\n'

        client.send_message(call.message.chat.id, answer_user_card,
                            parse_mode="html", protect_content=protect_content_check)
        return

    if 'HH' in call.data:
        my_st = call.data

        clue_list = my_st.split(",")
        clue_list.pop(0)
        clue_answer_text = ''

        for clue_el in clue_list:
            if clue_el != '':
                clue_paragraph = clues.clue_info(clue_el)
                clue_answer_text += clue_paragraph + ' \n'

        msg_clue_answer = client.send_message(call.message.chat.id, clue_answer_text,
                                              parse_mode="html",
                                              protect_content=protect_content_check)
        time.sleep(15)
        client.delete_message(call.message.chat.id, msg_clue_answer.message_id)
        return

    if call.data == 'config запрос':
        config_line = settings_config.output_config_line(us_id)
        client.send_message(call.message.chat.id,
                            "Направляю Вам config системы: \n"
                            "<b><code>" + str(config_line) + "</code></b>",
                            parse_mode="html", protect_content=protect_content_check)
        return

    if call.data == 'Сerberus error':
        client.send_message(call.message.chat.id,
                            'Если Вы уверены в легитимности доступа к системе, то попробуйте '
                            'повторно зарегистрироваться, воспользовавшись командой /start, '
                            'либо обратиться к администраторам ресурса.\n',
                            parse_mode="html", protect_content=protect_content_check)
        return

    if call.data == 'Сerberus':
        client.send_message(call.message.chat.id,
                            str(long_text.cerberus_command_description),
                            parse_mode="html", protect_content=protect_content_check)
        return

    if call.data == 'Меню настроек':
        client.send_chat_action(call.message.chat.id, action="typing")
        # получаем клавиатуру с настройками
        keyboard = keyboards.main_setting_keyboard(us_id)
        client.send_message(call.message.chat.id, "<b>Меню настроек</b>\n"
                                                  " \n"
                                                  "Разделы настроек, которые вы можете изменять. "
                                                  "Каждая кнопка отображает определенный фильтр системы\n"
                                                  " \n",
                            parse_mode="html", reply_markup=keyboard, protect_content=protect_content_check)
        return
    ################################################################################
    # МЕНЮ НАСТРОЕК#################################################################
    ################################################################################
    # установить переменную показа push
    show_alert_pr = False
    # ------------------------------------------------------------------------------------------------------------------
    if call.data == 'описание Информация о RFC':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        one = types.InlineKeyboardButton('🔴 Полная информация',
                                         callback_data='полное')
        two = types.InlineKeyboardButton('🟢 Краткая информация',
                                         callback_data='краткое')
        keyboard.add(one, two)
        # keyboard.add(Button_setting)

        # пытаемся получить текущее значение настройки пользователя
        try:
            cursor.execute(f'SELECT view_rfc FROM full_view_rfc WHERE user_id = {us_id}')
            view_rfc = cursor.fetchone()[0]
        except (Exception,):
            view_rfc = 'Не определенно'

        if view_rfc == "full":
            view_rfc = "Полная информация"
        else:
            view_rfc = "Краткая информация"
        # ---------------------------------------------------------

        client.send_message(call.message.chat.id,
                            "<b>● Формат отображения информации о RFC</b>\n"
                            " \n"
                            "Краткая информация, отображает основную информацию о RFC. "
                            "Полная информация включает дополнительные, "
                            "но редко используемые данные.\n"
                            " \n"
                            f"Сейчас: <b>{view_rfc}</b>",
                            parse_mode="html", reply_markup=keyboard, protect_content=protect_content_check)
        return
    if call.data == 'полное':
        postgres_init.full_view_rfc(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                    username=username, view_rfc="full")
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Установлен режим отображения полной информации о RFC",
                                     show_alert=False)
        logs.log_pass(us_id, 'Действие', f'Изменения настроек описания информации об RFC (Полное)')
        return
    elif call.data == 'краткое':
        postgres_init.full_view_rfc(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                    username=username, view_rfc="not full")
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Установлен режим отображения краткой информации о RFC",
                                     show_alert=show_alert_pr)
        logs.log_pass(us_id, 'Действие', f'Изменения настроек описания информации об RFC (Краткое)')
        return
    # ------------------------------------------------------------------------------------------------------------------
    # callback меню настройка отображения подсказок
    if call.data == 'описание Статус подсказок':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        one = types.InlineKeyboardButton('🔴 Отключить подсказки',
                                         callback_data='Отключить')
        two = types.InlineKeyboardButton('🟢 Включить подсказки',
                                         callback_data='Включить')
        keyboard.add(one, two)

        # пытаемся получить текущее значение настройки пользователя
        try:
            cursor.execute(f'SELECT advice FROM advice_rfc WHERE user_id = {us_id}')
            advice = cursor.fetchone()[0]
        except (Exception,):
            advice = 'Не определенно'

        if advice == "advice off":
            advice = "Подсказки отключены"
        else:
            advice = "Подсказки включены"
        # ---------------------------------------------------------

        client.send_message(call.message.chat.id, "<b>● Отображение советов</b>\n"
                                                  " \n"
                                                  "Подсказки отображают описание статусов RFC "
                                                  "и советы по использованию бота\n"
                                                  " \n"
                                                  f"Сейчас: <b>{advice}</b>",
                            parse_mode="html", reply_markup=keyboard, protect_content=protect_content_check)
        return
    elif call.data == 'Отключить':
        postgres_init.advice_rfc(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                 username=username, advice="advice off")
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Подсказки отключены",
                                     show_alert=show_alert_pr)
        logs.log_pass(us_id, 'Действие', f'Изменения настроек статуса подсказок (Отключены)')
        return
    elif call.data == 'Включить':
        postgres_init.advice_rfc(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                 username=username, advice="advice on")
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Подсказки включены",
                                     show_alert=show_alert_pr)
        logs.log_pass(us_id, 'Действие', f'Изменения настроек статуса подсказок (Включены)')
        return

    # ------------------------------------------------------------------------------------------------------------------
    # callback меню настройка длины ответа
    if call.data == 'длина ответа':
        client.send_chat_action(call.message.chat.id, action="typing")
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        one = types.InlineKeyboardButton('🔴 Полный ответ',
                                         callback_data='полный ответ')
        two = types.InlineKeyboardButton('🟢 Сокращенный ответ',
                                         callback_data='сокращенный ответ')
        keyboard.add(one, two)

        # пытаемся получить текущее значение настройки пользователя
        try:
            cursor.execute(f'SELECT stop200 FROM len_200 WHERE user_id = {us_id}')
            stop200 = cursor.fetchone()[0]
        except (Exception,):
            stop200 = 'Не определенно'

        if stop200 == "False":
            stop200 = "Ограничение снято"
        else:
            stop200 = "Ограничение установлено"
        # ---------------------------------------------------------

        client.send_message(call.message.chat.id,
                            "<b>● Длина ответа информации о RFC</b>\n"
                            " \n"
                            "Данная настройка позволяет сокращать длину ответа, более 200 символов. "
                            "Сокращенный ответ, отображает только первые 200 символов в ответе. "
                            "Полный ответ, снимает данное ограничение.\n"
                            " \n"
                            f"Сейчас: <b>{stop200}</b>",
                            parse_mode="html", reply_markup=keyboard, protect_content=protect_content_check)
        return
    if call.data == 'полный ответ':
        postgres_init.len_200(user_id=us_id, user_name=us_name, user_surname=us_surname,
                              username=username, stop200="False")
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Снято ограничение на 200 символов в ответе",
                                     show_alert=show_alert_pr)
        logs.log_pass(us_id, 'Действие', f'Изменения настроек длины ответа (Полный)')
        return
    if call.data == 'сокращенный ответ':
        postgres_init.len_200(user_id=us_id, user_name=us_name, user_surname=us_surname,
                              username=username, stop200="True")
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Установлено ограничение на 200 символов в ответе",
                                     show_alert=show_alert_pr)
        logs.log_pass(us_id, 'Действие', f'Изменения настроек длины ответа (Краткий)')
        return

    # ------------------------------------------------------------------------------------------------------------------
    # настройка блока оценки процентов
    if call.data == 'оценка алгоритмов':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        one = types.InlineKeyboardButton('🟢 Включить',
                                         callback_data='оценка включена')
        two = types.InlineKeyboardButton('🔴 Отключить',
                                         callback_data='оценка отключена')
        keyboard.add(one, two)

        # пытаемся получить текущее значение настройки пользователя
        try:
            cursor.execute(f'SELECT grade_el FROM grade_el_table WHERE user_id = {us_id}')
            grade_el = cursor.fetchone()[0]
        except (Exception,):
            grade_el = 'Не определенно'

        if grade_el == "True":
            grade_el = "Функция включена"
        else:
            grade_el = "Функция отключена"
        # ---------------------------------------------------------

        client.send_message(call.message.chat.id,
                            "<b>● Оценка алгоритмов</b>\n"
                            " \n"
                            "Данная настройка позволяет включить/отключить оценку попадания RFC "
                            "в план работ. "
                            "Включенная функция, производит оценку и анализ RFC. Скорость работы "
                            "может понизиться. \n"
                            "Выключенная функция увеличивает скорость работы"
                            "По умолчанию оценка включена\n"
                            " \n"
                            f"Сейчас: <b>{grade_el}</b>",
                            reply_markup=keyboard,
                            parse_mode="html", protect_content=protect_content_check)
        return
    if call.data == 'оценка включена':
        postgres_init.grade_el_fn(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                  username=username, grade_el="True")
        logs.log_pass(us_id, 'Действие', f'Изменения настроек оценки алгоритмов (Разрешена)')
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Вы включили функцию оценки алгоритмов",
                                     show_alert=show_alert_pr)
        return
    if call.data == 'оценка отключена':
        postgres_init.grade_el_fn(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                  username=username, grade_el="False")
        logs.log_pass(us_id, 'Действие', f'Изменения настроек оценки алгоритмов (Запрещена)')
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Вы отключили функцию оценки алгоритмов",
                                     show_alert=show_alert_pr)
        return

    # ------------------------------------------------------------------------------------------------------------------
    # настройка блока оценки рассылок
    if call.data == 'Рассылки':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        one = types.InlineKeyboardButton('🟢 Разрешить',
                                         callback_data='Рассылки разрешены')
        two = types.InlineKeyboardButton('🔴 Заблокировать',
                                         callback_data='Рассылки заблокированы')
        keyboard.add(one, two)

        # пытаемся получить текущее значение настройки пользователя
        try:
            cursor.execute(f'SELECT add_block FROM add_block_table WHERE user_id = {us_id}')
            add_block = cursor.fetchone()[0]
        except (Exception,):
            add_block = 'Не определенно'

        if add_block == "False":
            add_block = "Рассылки разрешены"
        else:
            add_block = "Рассылки отключены"
        # ---------------------------------------------------------

        client.send_message(call.message.chat.id,
                            "<b>● Параметры рассылок</b>\n"
                            " \n"
                            "Данная настройка позволяет отключить уведомления и рассылки. "
                            "RFC Informer bot использует рассылки для уведомления пользователей об "
                            "обновлениях. "
                            "По умолчанию рассылки включены\n"
                            " \n"
                            f"Сейчас: <b>{add_block}</b>",
                            reply_markup=keyboard,
                            parse_mode="html", protect_content=protect_content_check)
        return
    if call.data == 'Рассылки разрешены':
        postgres_init.add_block_fn(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                   username=username, add_block="False")
        logs.log_pass(us_id, 'Действие', f'Изменения настроек рассылок (Разрешены)')
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Вы разрешили отправлять вам рассылки",
                                     show_alert=show_alert_pr)
        return
    if call.data == 'Рассылки заблокированы':
        postgres_init.add_block_fn(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                   username=username, add_block="True")
        logs.log_pass(us_id, 'Действие', f'Изменения настроек рассылок (Запрещены)')
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Вы запретили отправлять вам рассылки",
                                     show_alert=show_alert_pr)
        return
    # ------------------------------------------------------------------------------------------------------------------
    # настройка блока отправки ошибок
    if call.data == 'отображение ошибок':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        one = types.InlineKeyboardButton('🟢 Разрешить',
                                         callback_data='Ошибки отображаются')
        two = types.InlineKeyboardButton('🔴 Заблокировать',
                                         callback_data='Ошибки не отображаются')
        keyboard.add(one, two)

        # пытаемся получить текущее значение настройки пользователя
        try:
            cursor.execute(f'SELECT error FROM error_table WHERE user_id = {us_id}')
            add_block = cursor.fetchone()[0]
        except (Exception,):
            add_block = 'yes'

        if add_block == "yes":
            add_block = "Ошибки отображаются"
        else:
            add_block = "Ошибки не отображаются"
        # ---------------------------------------------------------

        client.send_message(call.message.chat.id,
                            "<b>● Параметры отображения ошибок</b>\n"
                            " \n"
                            "Данная настройка позволяет администраторам проекта отключить уведомления об ошибках. "
                            "RFC Informer bot использует записи ошибок для уведомления администраторов об "
                            "критических сбоях в системе. "
                            "По умолчанию ошибки отображаются всем администраторам\n"
                            " \n"
                            f"Сейчас: <b>{add_block}</b>",
                            reply_markup=keyboard,
                            parse_mode="html", protect_content=protect_content_check)
        return
    if call.data == 'Ошибки отображаются':
        postgres_init.error_table_fn(user_id=us_id, error='yes')
        logs.log_pass(us_id, 'Действие', f'Изменение настроек отображения ошибок (Включены)')
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Вы разрешили уведомлять вас об ошибках",
                                     show_alert=show_alert_pr)
        return
    if call.data == 'Ошибки не отображаются':
        postgres_init.error_table_fn(user_id=us_id, error='no')
        logs.log_pass(us_id, 'Действие', f'Изменение настроек отображения ошибок (Отключены)')
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Вы запретили уведомлять вас об ошибках",
                                     show_alert=show_alert_pr)
        return

    # ------------------------------------------------------------------------------------------------------------------
    # настройка календаря
    if call.data == 'вид календаря':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        one = types.InlineKeyboardButton('🔴 Полный',
                                         callback_data='календарь полный')
        two = types.InlineKeyboardButton('🟢 Основной',
                                         callback_data='календарь основной')
        keyboard.add(one, two)

        # пытаемся получить текущее значение настройки пользователя
        try:
            cursor.execute(f'SELECT calendar_view FROM calendar_table WHERE user_id = {us_id}')
            calendar_view = cursor.fetchone()[0]
        except (Exception,):
            calendar_view = 'Не определенно'

        if calendar_view == "Full":
            calendar_view = "Вид календаря (Полный)"
        else:
            calendar_view = "Вид календаря (Основной)"

        client.send_message(call.message.chat.id,
                            "<b>● Календарь</b>\n"
                            " \n"
                            "Данная настройка позволяет настраивать вид календаря работ "
                            "и отображающую в нем информацию. Доступны два режима: \n"
                            "Основной - отображает только RFC находящиеся в банке. \n"
                            "Полный - все RFC данного пользователя. \n"
                            "По умолчанию отображаются все RFC\n"
                            " \n"
                            f"Сейчас: <b>{calendar_view}</b>",
                            reply_markup=keyboard, parse_mode="html", protect_content=protect_content_check)
        return
    if call.data == 'календарь полный':
        postgres_init.calendar_fn(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                  username=username, calendar_view="Full")
        logs.log_pass(us_id, 'Действие', f'Изменение вида календаря (Полный)')
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Вы установили режим отображения всех RFC в календаре работ",
                                     show_alert=show_alert_pr)
        return
    if call.data == 'календарь основной':
        postgres_init.calendar_fn(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                  username=username, calendar_view="Not Full")
        logs.log_pass(us_id, 'Действие', f'Изменение вида календаря (Основной)')
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Вы установили режим отображения только основных RFC в календаре работ",
                                     show_alert=show_alert_pr)
        return
    # ------------------------------------------------------------------------------------------------------------------
    # настройка персонального модуля
    if call.data == 'модуль личности':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        one = types.InlineKeyboardButton('🔴 Деактивировать',
                                         callback_data='модуль личности деактивирован')
        two = types.InlineKeyboardButton('🟢 Активировать',
                                         callback_data='модуль личности активирован')
        keyboard.add(one, two)

        # пытаемся получить текущее значение настройки пользователя
        try:
            cursor.execute(f'SELECT personal_mode FROM personal_mode_table WHERE user_id = {us_id}')
            personal_mode = cursor.fetchone()[0]
        except (Exception,):
            personal_mode = 'Не определенно'

        if personal_mode == "on":
            personal_mode = "Модуль активирован"
        else:
            personal_mode = "Модуль деактивирован"

        client.send_message(call.message.chat.id,
                            "<b>● Модуль личности</b>\n"
                            " \n"
                            "Модуль личности активирует блок кода, который отвечает за "
                            "более легкую интеграцию и взаимодействие с RFC Informer Bot. "
                            "Доступны два режима: \n"
                            "Активирован - Пользователь получает дополнительные сообщения. \n"
                            "Деактивирован - Пользователь получает только информацию о RFC. \n"
                            "По умолчанию модуль активирован\n"
                            " \n"
                            f"Сейчас: <b>{personal_mode}</b>",
                            reply_markup=keyboard, parse_mode="html", protect_content=protect_content_check)
        return
    if call.data == 'модуль личности деактивирован':
        postgres_init.personal_mode_fn(user_id=us_id, personal_mode='off')
        logs.log_pass(us_id, 'Действие', f'Модуль личности деактивирован')
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Вы деактивировали модуль личности",
                                     show_alert=show_alert_pr)
        return
    if call.data == 'модуль личности активирован':
        postgres_init.personal_mode_fn(user_id=us_id, personal_mode='on')
        logs.log_pass(us_id, 'Действие', f'Модуль личности активирован')
        client.answer_callback_query(callback_query_id=call.id,
                                     text="Вы активировали модуль личности",
                                     show_alert=show_alert_pr)
        return
    # ------------------------------------------------------------------------------------------------------------------
    # настройка модуля дежурных смен
    if call.data == 'дежурные смены':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        one = types.InlineKeyboardButton('✅ Дежурный windows администратор',
                                         callback_data='+ Дежурный windows администратор')
        two = types.InlineKeyboardButton('❌ Дежурный windows администратор',
                                         callback_data='- Дежурный windows администратор')
        three = types.InlineKeyboardButton('✅ Дежурный unix администратор',
                                           callback_data='+ Дежурный unix администратор')
        four = types.InlineKeyboardButton('❌ Дежурный unix администратор',
                                          callback_data='- Дежурный unix администратор')
        keyboard.add(one, two)
        keyboard.add(three, four)

        client.send_message(call.message.chat.id,
                            "<b>● Дежурные смены в календаре</b>\n"
                            " \n"
                            "Данная настройка позволяет добавлять или удалять в календаре "
                            "работы различных дежурных смен. "
                            "Доступны два режима: \n"
                            "Добавить - Пользователь добавляет в свой календарь работы выбранного дежурного \n"
                            "Удалить - Пользователь удаляет информацию о выбранном дежурном в календаре \n",
                            reply_markup=keyboard, parse_mode="html", protect_content=protect_content_check)
        return

    if call.data == '+ Дежурный windows администратор':
        cursor.execute(f'SELECT * FROM initialization_user WHERE user_id = {us_id}')
        user_list = cursor.fetchall()[0]
        guid = f'{user_list[4]},01e22cdd-9707-11ed-8103-005056844352'

        postgres_init.initialization(user_id=user_list[0], user_name=user_list[1], username=user_list[2],
                                     department=user_list[3], guid=guid, access=user_list[5])

        client.answer_callback_query(callback_query_id=call.id,
                                     text="Работы добавлены",
                                     show_alert=show_alert_pr)
        logs.log_pass(us_id, 'Действие', f'Добавлены работы windows администраторов')

    if call.data == '+ Дежурный unix администратор':
        cursor.execute(f'SELECT * FROM initialization_user WHERE user_id = {us_id}')
        user_list = cursor.fetchall()[0]
        guid = f'{user_list[4]},c5c2591b-973e-11ed-8103-005056844352'

        postgres_init.initialization(user_id=user_list[0], user_name=user_list[1], username=user_list[2],
                                     department=user_list[3], guid=guid, access=user_list[5])

        client.answer_callback_query(callback_query_id=call.id,
                                     text="Работы добавлены",
                                     show_alert=show_alert_pr)
        logs.log_pass(us_id, 'Действие', f'Добавлены работы unix администраторов')

    if call.data == '- Дежурный windows администратор':
        cursor.execute(f'SELECT * FROM initialization_user WHERE user_id = {us_id}')
        user_list = cursor.fetchall()[0]

        guid = user_list[4]

        guid = guid.replace(',01e22cdd-9707-11ed-8103-005056844352', '')

        postgres_init.initialization(user_id=user_list[0], user_name=user_list[1], username=user_list[2],
                                     department=user_list[3], guid=guid, access=user_list[5])

        client.answer_callback_query(callback_query_id=call.id,
                                     text="Работы удалены",
                                     show_alert=show_alert_pr)
        logs.log_pass(us_id, 'Действие', f'Убраны работы windows администраторов')

    if call.data == '- Дежурный unix администратор':
        cursor.execute(f'SELECT * FROM initialization_user WHERE user_id = {us_id}')
        user_list = cursor.fetchall()[0]

        guid = user_list[4]

        guid = guid.replace(',c5c2591b-973e-11ed-8103-005056844352', '')

        postgres_init.initialization(user_id=user_list[0], user_name=user_list[1], username=user_list[2],
                                     department=user_list[3], guid=guid, access=user_list[5])

        client.answer_callback_query(callback_query_id=call.id,
                                     text="Работы удалены",
                                     show_alert=show_alert_pr)
        logs.log_pass(us_id, 'Действие', f'Убраны работы unix администраторов')

    us_id = call.from_user.id

# КАЛЕНДАРЬ КОЛБЕК----------------------------------------------------------------------------------------------
    # calendar, step = DetailedTelegramCalendar(calendar_id=us_id).build()
    result, key, step = DetailedTelegramCalendar(locale="ru", calendar_id=us_id).process(call.data)
    if not result and key:
        client.edit_message_text("Выбери интересующую дату",
                                 call.message.chat.id,
                                 call.message.message_id,
                                 reply_markup=key)
    elif result:
        # ОСНОВНАЯ ФУНКЦИЯ КАЛЕНДАРЯ КОТОРАЯ ФОРМИРУЕТ КАДЛЕНДАРЬ И ВОЗВРАЩАЕТ
        # ОТВЕТ, ЧЕК ПОВТОР И СПИСОК РАБОТ В МАСИВЕ ДЛЯ КНОПОК
        if calendar_build is None:
            client.send_message(call.message.chat.id,
                                "Данные устарели. "
                                "Пожалуйста обновите запрос /calendar",
                                parse_mode="html",
                                # protect_content=protect_content_check
                                )
            return
        try:
            cursor.execute('SELECT grade_el FROM grade_el_table WHERE user_id = '+str(us_id))
            grade_el_table_zn = cursor.fetchone()[0]
        except (Exception,):
            grade_el_table_zn = "True"
        # вытаскиваем переменную календаря
        try:
            cursor.execute('SELECT calendar_view FROM calendar_table WHERE user_id = '+str(us_id))
            calendar_view = str(cursor.fetchone()[0])
        except (Exception,):
            calendar_view = "Full"
        answer, repeat_cldr, answer_list = calendars.answer_calendar_rfc(result,
                                                                         calendar_build,
                                                                         check_l_name,
                                                                         grade_el_table_zn,
                                                                         calendar_view)
        if not repeat_cldr:
            client.answer_callback_query(callback_query_id=call.id,
                                         text=answer,
                                         show_alert=True)
        else:
            logs.log_pass(us_id, 'Действие', f'Из календаря запрошена дата: {result}')

            button_name_array = []
            for el_bn in answer_list:
                bn_name = types.InlineKeyboardButton(text=str(el_bn["numberRFC"]),
                                                     callback_data=str(el_bn["numberRFC"]))
                button_name_array.append(bn_name)

            if len(button_name_array) > 5:
                df = 3
            else:
                df = 2
            keyboard = types.InlineKeyboardMarkup(row_width=df)

            keyboard.add(*button_name_array)
            client.send_message(call.message.chat.id, answer,
                                reply_markup=keyboard, parse_mode="html",
                                # protect_content=protect_content_check
                                )
            cursor.execute('SELECT advice FROM advice_rfc WHERE user_id = '+str(us_id))
            advice = cursor.fetchone()[0]
            if advice == "advice on":
                try:
                    cursor.execute('SELECT grade_el FROM grade_el_table WHERE user_id = '+str(us_id))
                    grade_el_table_zn = cursor.fetchone()[0]
                except (Exception,):
                    grade_el_table_zn = "True"

                if grade_el_table_zn == "True":
                    clue_answer_list = []

                    clue_answer = clues.clue_info("Оценка RFC")
                    clue_answer_list.append(clue_answer)

                    clue_answer_full = ""
                    for clue_answer_el in clue_answer_list:
                        clue_answer_full = clue_answer_full + clue_answer_el + \
                                           " \n"
                    clue_answer_full = clue_answer_full + clues.clue_answer_clue
                    client.send_message(call.message.chat.id, str(clue_answer_full),
                                        parse_mode="html",
                                        # protect_content=protect_content_check
                                        )
        return
