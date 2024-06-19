# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------

import time
import types
import random
import os.path
import json
import os.path
from datetime import datetime

# ----------------------------------------------------------------------------------------------------------------------

import telebot
import re
import schedule
from telebot import types
from telegram_bot_calendar import WMonthTelegramCalendar
import hashlib
from rich.traceback import install

# ----------------------------------------------------------------------------------------------------------------------

import log_analysis                 # обработка журнала логов
import personal_users               # работа с полным именем пользователя
import commands                     # работа с блоком команд
import blocks                       # модуль блокировки доступов
import integrations                 # базовый набор интеграций
import cerberus                     # модуль проверки и блокировки пользователей
import configs                      # хранилище токена, ключей и паролей
import firewall_mars                # фаервол
import calendars                    # работа с календарем
import mailing_list                 # рассылки
import settings_config              # модуль работы с конфигом системы
import clues                        # блок с текстом подсказок
import postgres_init                # подключение к бд
import naumen_search                # модуль поиска в банке
import logs                         # модуль записи лога
import protect_content              # модуль защиты от копирования
import keyboards                    # модуль работы с клавиатурой
import admins                       # блок работы с админами
import errors                       # блок работы с ошибкой
import rfc_search                   # модуль поиска информации о rfc
import neuron                       # модуль обработки строки и паттернов
import servers                      # модуль для запуска сервера
import long_text                    # модуль где храним длинные текста
import callbacks                    # модуль обработки callback запросов

# ----------------------------------------------------------------------------------------------------------------------

client = telebot.TeleBot(configs.telegram['token'])

cursor_main, conn_main = postgres_init.postgres_init()

# global us_id
# us_id = 0

uuid = None  # Персональный ключ рфс работ в банке
word_file = None
agreements = None
calendar_build = None
full_name = None
check_l_name = True
time_now = datetime.now()
work_time = 0
exp_rfc_search = "False"


###############################################################################
# ###########################ЗАПУСК БОТА#######################################
###############################################################################


def access_registered(message):
    protect_content_check = protect_content.protect_content_check_fn(message.chat.id)
    client.send_chat_action(message.chat.id,
                            action="typing")
    # вывод кнопок в 1 колонку
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton('📲 Зарегистрироваться',
                                       callback_data='регистрация 1с')
    item2 = types.InlineKeyboardButton('✉️ Помощь',
                                       callback_data='помощь при блоке')
    markup.add(item1, item2)
    client.send_chat_action(message.chat.id, action="typing")
    client.send_message(message.chat.id,
                        "⚠️ Доступ к чат-боту RFC заблокирован!\n"
                        "📲 Зарегистрируйтесь в системе или обратитесь к системному администратору ресурса",
                        parse_mode="html", reply_markup=markup,
                        protect_content=protect_content_check)
    return


def command_blocked(message, us_id, full_user_name, username):
    username = personal_users.user_nickname(username)
    protect_content_check = protect_content.protect_content_check_fn(us_id)

    time.sleep(2)
    login = message.text.lower()

    client.send_chat_action(message.chat.id, action="typing")
    client.send_message(message.chat.id,
                        "⚠️ Доступ к данной команде заблокирован!\n"
                        "📑 ID пользователя: <b>" + str(us_id) + "</b> \n"
                                                                "📲 Обратитесь к системному администратору ресурса, "
                                                                "для уточнения прав доступа", parse_mode="html",
                        protect_content=protect_content_check)
    client.send_message(message.chat.id,
                        "⚠️ Access to the command blocked!\n"
                        "📑 ID user: <b>" + str(us_id) + "</b> \n"
                                                        "📲 Contact the system administrator of the "
                                                        "resource to clarify access rights",
                        parse_mode="html",
                        protect_content=protect_content_check)

    text_system_command = f"⚠️<b>Обнаружена попытка использования системной команды!</b>\n" \
                          f" \n" \
                          f"Имя: <b>{full_user_name}</b> \n" \
                          f"Никнейм: <b>{username}</b> \n" \
                          f" \n" \
                          f"💾 Команда пользователя: <i><b>{login}</b></i>"
    admins.admin_notification_message(client, text_system_command)

    # запись в журнал лога
    if full_name is None:
        full_user_name = firewall_mars.id_in_name(us_id)

    logs.log_pass(us_id, 'Ошибка',
                  f'Доступ пользователю {full_user_name} к команде /{login} заблокирован')
    return


def start_script(message, us_id, protect_content_check):
    postgres_init.connect_bd(message)

    access_check = firewall_mars.access_check(message.from_user.id)
    if access_check:
        client.send_chat_action(message.chat.id, action="typing")
        # вывод кнопок в 1 колонку
        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton('✎ Начать работу', callback_data='Запуск бота')
        item2 = types.InlineKeyboardButton('📝 Основные положения', callback_data='Ознакомление с ботом')
        markup.add(item1, item2)
        client.send_message(message.chat.id,
                            "Запуск <b>RFC Informer Bot</b> v.<b>" +
                            str(configs.version) + "</b> от <b>" +
                            str(configs.data_version_update) + "</b>",
                            parse_mode="html", reply_markup=markup,
                            protect_content=protect_content_check)

        logs.log_pass(us_id, 'Действие',
                      f'Запуск RFC Informer Bot v.{configs.version} от {configs.data_version_update}')
        return
    else:
        logs.log_pass(us_id, 'Блокировка', f'доступ заблокирован')
        return


@client.message_handler(content_types=["audio", "document", "photo", "sticker", "video", "video_note", "voice",
                                       "location", "contact", "new_chat_members", "left_chat_member", "new_chat_title",
                                       "new_chat_photo", "delete_chat_photo", "group_chat_created",
                                       "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                                       "migrate_from_chat_id", "pinned_message"])
def handler_any_type(message):
    reaction_type_not_answer = ["🤷‍♂", "🤷", "🤷‍♀"]
    client.set_message_reaction(message.chat.id, message_id=message.message_id,
                                reaction=[types.ReactionTypeEmoji(random.choice(reaction_type_not_answer))])
    client.send_message(message.chat.id, random.choice(long_text.wrong_content_types),
                        parse_mode="html",)
    logs.log_pass(message, 'Ошибка', f"Неизвестный content_types")
    return


@client.message_handler(commands=['start', 'reset_1c_session'])
def start_messages(message):
    us_id = message.from_user.id
    username = message.from_user.username
    full_name_user = message.from_user.full_name

    postgres_init.initialization(user_id=us_id, user_name=full_name_user, username=username,
                                 department='', guid='', access="Доступ запрещен")

    postgres_init.protect_content_fn(user_id=us_id, protect_content_check=1)

    protect_content_check = protect_content.protect_content_check_fn(us_id)

    start_script(message, us_id, protect_content_check)

    return


@client.message_handler(commands=['reset'])
def start_messages(message):
    us_id = message.from_user.id
    username = message.from_user.username

    protect_content_check = protect_content.protect_content_check_fn(us_id)
    start_script(message, us_id, protect_content_check)

    # проверка доступ и дальнейший блок бота для пользователя
    access_check = firewall_mars.access_check(message.from_user.id)
    if not access_check:
        blocks.access_blocked(message, us_id, full_name, username, client)
        return


@client.message_handler(content_types=['text'])
def get_text(message):
    cursor, conn = postgres_init.postgres_init()

    us_id = message.from_user.id
    us_name = message.from_user.first_name
    us_surname = message.from_user.last_name
    username = message.from_user.username

    protect_content_check = protect_content.protect_content_check_fn(us_id)
    full_name_user = personal_users.user_name(us_id, message)

    # ##############################################################################
    # ######################### СТАРТ СКРИПТА ######################################
    # ##############################################################################
    if '/reset' == message.text.lower():
        start_script(message, us_id, protect_content_check)
        return

    reset_call = ['/start', '/reset', '/command06', '/command07']
    for reset_el in reset_call:
        if reset_el == message.text.lower():
            postgres_init.authentication_1c(user_id=us_id, user_login='', hash_password='',
                                            check_access=1, last_data=message.date)
            postgres_init.protect_content_fn(user_id=us_id, protect_content_check=0)
            start_script(message, us_id, protect_content_check)
            return

    # проверка доступ и дальнейший блок бота для пользователя
    access_check = firewall_mars.access_check(message.from_user.id)
    if not access_check:
        postgres_init.connect_bd(message)
        blocks.access_blocked(message, us_id, full_name_user, username, client)
        return
    # проверка активной УЗ ИС 1С
    cerberus.cerberus_check(client, us_id)
    # ##############################################################################
    # ОСНОВНОЙ СКРИПТ ##############################################################
    # ##############################################################################

    # модуль работы с рассылками
    try:
        cursor.execute('SELECT search_rfc FROM rfc_number WHERE user_id = ' + str(us_id))
        search_rfc = cursor.fetchone()[0]
    except (Exception,):
        search_rfc = 0
    if search_rfc == 19:
        mailing_list.mailing_message(client, message, protect_content_check)
        return
    # заканчиваем с рассылками

    if '/command04' == message.text.lower():
        access_check = firewall_mars.access_check(message.from_user.id)
        if access_check:
            for admin_id in firewall_mars.level_list_check('Разработчик'):
                if admin_id == message.from_user.id:
                    logs.log_pass(us_id, 'Команда', f'/command04')

                    rtb = "!"
                    client.send_message(message.chat.id, "Тест успешен" + str(rtb),
                                        parse_mode="html", protect_content=protect_content_check)
                    client.send_contact(message.chat.id,
                                        phone_number="79879534325",
                                        first_name="Терехов Александр")
                    client.set_message_reaction(message.chat.id,
                                                message_id=message.message_id,
                                                reaction=[types.ReactionTypeEmoji("👍")]
                                                )
                    return
            else:
                command_blocked(message, us_id, full_name_user, username)
                return
        else:
            blocks.access_blocked(message, us_id, full_name_user, username, client)
            return
    if '/command05' == message.text.lower():
        access_check = firewall_mars.access_check(message.from_user.id)
        if access_check:
            for admin_id in firewall_mars.level_list_check('Администратор'):
                if admin_id == message.from_user.id:
                    logs.log_pass(us_id, 'Команда', f'/command05')

                    client.send_document(message.chat.id, open(str(configs.file_log_name), "rb"),
                                         caption="Журнал логов от " + str(datetime.now().date())
                                         )
                    return
            else:
                command_blocked(message, us_id, full_name_user, username)
                return
        else:
            blocks.access_blocked(message, us_id, full_name_user, username, client)
            return
    if '/command13' == message.text.lower():
        access_check = firewall_mars.access_check(message.from_user.id)
        if access_check:
            for admin_id in firewall_mars.level_list_check('Администратор'):
                if admin_id == message.from_user.id:
                    logs.log_pass(us_id, 'Команда', f'/command13')

                    client.send_message(message.chat.id,
                                        "Включен <b>'Режима разработчика'</b>. "
                                        "Последующие действия не будут "
                                        "отображаться в журнале логов. "
                                        "Отключено уведомление об ошибках.\n",
                                        parse_mode="html", protect_content=protect_content_check)
                    postgres_init.mode_test(user_id=us_id, user_name=us_name,
                                            user_surname=us_surname, username=username, mode_test_fn="yes")
                    return
            else:
                command_blocked(message, us_id, full_name_user, username)
                return
        else:
            blocks.access_blocked(message, us_id, full_name_user, username, client)
            return
    if '/command14' == message.text.lower():
        access_check = firewall_mars.access_check(message.from_user.id)
        if access_check:
            for admin_id in firewall_mars.level_list_check('Разработчик'):
                if admin_id == message.from_user.id:
                    postgres_init.mode_test(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                            username=username, mode_test_fn="no")
                    logs.log_pass(us_id, 'Команда', f'/command14')

                    client.send_message(message.chat.id,
                                        "<b>'Режима разработчика'</b> отключен. "
                                        "Активирована запись действий в журнале "
                                        "логов и уведомления об ошибках.\n",
                                        parse_mode="html", protect_content=protect_content_check)
                    return
            else:
                command_blocked(message, us_id, full_name_user, username)
                return
        else:
            blocks.access_blocked(message, us_id, full_name_user, username, client)
            return

    if '/command16' == message.text.lower():
        access_check = firewall_mars.access_check(message.from_user.id)
        if access_check:
            for admin_id in firewall_mars.level_list_check('Разработчик'):
                if admin_id == message.from_user.id:
                    logs.log_pass(us_id, 'Команда', f'/command16')

                    client.send_message(message.chat.id,
                                        "Анализируем журнал, формируем отчет",
                                        parse_mode="html", protect_content=protect_content_check)

                    # анализируем журнал логов
                    log_analysis.main_log_analysis()
                    # отправляем файл
                    client.send_document(message.chat.id,
                                         open(configs.log_analysis_filename, 'rb'),
                                         parse_mode="html", protect_content=protect_content_check)
                    # удаляем файл
                    os.system(f'del {configs.log_analysis_filename}')
                    return
            else:
                command_blocked(message, us_id, full_name_user, username)
                return
        else:
            blocks.access_blocked(message, us_id, full_name_user, username, client)
            return

    if '/command17' == message.text.lower():
        access_check = firewall_mars.access_check(message.from_user.id)
        if access_check:
            for admin_id in firewall_mars.level_list_check('Разработчик'):
                if admin_id == message.from_user.id:
                    logs.log_pass(us_id, 'Команда', f'/command17')
                    return

            else:
                command_blocked(message, us_id, full_name_user, username)
                return
        else:
            blocks.access_blocked(message, us_id, full_name_user, username, client)
            return

    calendar_search_list = ['/command18', '/calendar', '📆 календарь работ']
    for calendar_search_list_el in calendar_search_list:
        if calendar_search_list_el == message.text.lower():
            access_check = firewall_mars.access_check(message.from_user.id)
            if access_check:
                try:
                    logs.log_pass(us_id, 'Команда', f'/calendar')
                    # функция получения guid
                    global check_l_name
                    guid_1c, check_l_name = firewall_mars.id_in_guid(us_id)
                    # print("Твой guid: "+str(guid_1c))

                    if guid_1c == "":
                        client.send_message(message.chat.id,
                                            "<b>Уважаемый пользователь,</b>\n"
                                            " \n"
                                            "Хотим проинформировать вас о том, что на вашем текущем уровне доступа "
                                            "<b>календарь не доступен</b>. Вы можете запросить функцию доступа "
                                            "к календарю в рамках отдельного сообщения.\n"
                                            " \n"
                                            "Если вам необходимо узнать ваше расписание, пожалуйста, "
                                            "направьте нам письмо, "
                                            "и мы с радостью предоставим вам доступ к календарю.\n"
                                            " \n"
                                            "<b>С уважением,\n"
                                            "RFC Informer Bot</b>\n",
                                            protect_content=protect_content_check,
                                            parse_mode="html")
                        return
                    global calendar_build
                    client.send_message(message.chat.id,
                                        "Выполняю загрузку календаря, "
                                        "ожидайте ⏱",
                                        protect_content=protect_content_check)
                    calendar_build = calendars.calendar_rfc(guid_1c)
                    calendar, step = WMonthTelegramCalendar(calendar_id=us_id, locale="ru").build()

                    client.send_message(message.chat.id,
                                        "Выбери нужную дату, "
                                        "для проведения RFC.\n"
                                        "Для получения всех работ, нажмите "
                                        "/calendar_list", reply_markup=calendar,
                                        protect_content=protect_content_check)
                    return
                except (Exception,):
                    client.send_message(message.chat.id,
                                        "Ошибка загрузки! Попробуй /reset или повтори попытку позже",
                                        protect_content=protect_content_check)
                    return
            else:
                blocks.access_blocked(message, us_id, full_name_user, username, client)
                return

    if '/command19' == message.text.lower():
        access_check = firewall_mars.access_check(message.from_user.id)
        if access_check:
            for admin_id in firewall_mars.level_list_check('Разработчик'):
                if admin_id == message.from_user.id:
                    logs.log_pass(us_id, 'Команда', f'/command19')

                    markup = types.InlineKeyboardMarkup(row_width=1)
                    item1 = types.InlineKeyboardButton('Направить',
                                                       callback_data='направить рассылку')
                    markup.add(item1)

                    client.send_message(message.chat.id,
                                        "Направить рассылку на <b>всех пользователей</b>?",
                                        parse_mode="html",
                                        reply_markup=markup, protect_content=protect_content_check)

                    return
            else:
                command_blocked(message, us_id, full_name_user, username)
                return
        else:
            blocks.access_blocked(message, us_id, full_name_user, username, client)
            return

    if '/cerberus' == message.text.lower():
        client.send_message(message.chat.id,
                            str(long_text.cerberus_command_description),
                            parse_mode="html",
                            protect_content=protect_content_check)
        return

    calendar_list = ['/command20', '/calendar_list', '📆 список работ']
    for calendar_list_el in calendar_list:
        if calendar_list_el == message.text.lower():
            access_check = firewall_mars.access_check(message.from_user.id)
            if access_check:
                logs.log_pass(us_id, 'Команда', f'/calendar_list')

                # функция получения guid
                guid_1c, check_l_name = firewall_mars.id_in_guid(us_id)
                if guid_1c == "":
                    client.send_message(message.chat.id,
                                        "<b>Уважаемый пользователь,</b>\n"
                                        " \n"
                                        "Хотим проинформировать вас о том, что на вашем текущем уровне доступа "
                                        "<b>календарь не доступен</b>. Вы можете запросить функцию доступа "
                                        "к календарю в рамках отдельного сообщения.\n"
                                        " \n"
                                        "Если вам необходимо узнать ваше расписание, пожалуйста, "
                                        "направьте нам письмо, "
                                        "и мы с радостью предоставим вам доступ к календарю.\n"
                                        " \n"
                                        "<b>С уважением,\n"
                                        "RFC Informer Bot</b>\n",
                                        parse_mode="html",
                                        protect_content=protect_content_check)
                    return
                client.send_message(message.chat.id,
                                    "Выполняю загрузку календаря, "
                                    "ожидайте ⏱", protect_content=protect_content_check)
                calendar_build = calendars.calendar_rfc(guid_1c)

                if check_l_name:
                    client.send_message(message.chat.id,
                                        "Ошибка загрузки! "
                                        "Слишком много данных! "
                                        "Воспользуйтесь обычным календарем",
                                        protect_content=protect_content_check)
                    return
                else:
                    try:
                        cursor.execute('SELECT grade_el FROM grade_el_table WHERE user_id = ' + str(us_id))
                        grade_el_table_zn = cursor.fetchone()[0]
                    except (Exception,):
                        grade_el_table_zn = "True"

                    # вытаскиваем переменную календаря
                    try:
                        cursor.execute('SELECT calendar_view FROM calendar_table WHERE user_id = ' + str(us_id))
                        calendar_view = cursor.fetchone()[0]
                    except (Exception,):
                        calendar_view = "Full"
                    answer_cl_list, answer_list, work_not_check = calendars.list_week(
                        calendar_build,
                        grade_el_table_zn,
                        calendar_view)
                    # print(answer_cl_list)
                    button_name_array = []
                    for el_bn in answer_list:
                        bn_name = types.InlineKeyboardButton(
                            text=str(el_bn["numberRFC"]),
                            callback_data=str(el_bn["numberRFC"])
                        )
                        button_name_array.append(bn_name)

                    if len(button_name_array) > 5:
                        df = 3
                    else:
                        df = 2
                    keyboard = types.InlineKeyboardMarkup(row_width=df)

                    keyboard.add(*button_name_array)

                    client.send_message(message.chat.id,
                                        str(answer_cl_list),
                                        parse_mode="html",
                                        reply_markup=keyboard,
                                        protect_content=protect_content_check,
                                        link_preview_options=types.LinkPreviewOptions(is_disabled=True))

                    cursor.execute('SELECT advice FROM advice_rfc WHERE user_id = ' + str(us_id))
                    advice = cursor.fetchone()[0]
                    if advice == "advice on":
                        try:
                            cursor.execute('SELECT grade_el FROM grade_el_table WHERE user_id = ' + str(us_id))
                            grade_el_table_zn = cursor.fetchone()[0]
                        except (Exception,):
                            grade_el_table_zn = "True"

                        clue_answer_list = []
                        if grade_el_table_zn == "True":
                            if not work_not_check:
                                clue_answer = clues.clue_info("Оценка RFC")
                                clue_answer_list.append(clue_answer)
                        if work_not_check:
                            clue_answer = clues.clue_info('Отсутствие работ')
                            clue_answer_list.append(clue_answer)

                        clue_answer_full = ""
                        for clue_answer_el in clue_answer_list:
                            clue_answer_full = clue_answer_full + clue_answer_el + \
                                               " \n"
                        clue_answer_full = clue_answer_full + clues.clue_answer_clue
                        client.send_message(message.chat.id, str(clue_answer_full),
                                            parse_mode="html",
                                            protect_content=protect_content_check)
                    return
            else:
                blocks.access_blocked(message, us_id, full_name_user, username, client)
                return

    roadmap_list = ['/command23', '/roadmap']
    for roadmap_list_el in roadmap_list:
        if roadmap_list_el == message.text.lower():
            access_check = firewall_mars.access_check(message.from_user.id)
            if access_check:

                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton(text="💡 Предложить идею",
                                                   callback_data="Предложить идею")
                markup.add(item1)

                client.send_message(message.chat.id,
                                    "Roadmap на <b>всех пользователей</b>\n"
                                    " \n"
                                    f"Версия системы: <b>{configs.version}</b> от <b>"
                                    f"{configs.data_version_update}</b> \n"
                                    "<a href='https://confluence.jet.su/pages/"
                                    "viewpage.action?pageId=162355252'>"
                                    "Список версий и история изменений RFC Informer Bot</a>\n"
                                    " \n"
                                    "Вы можете предложить идею изменения, нажав на кнопку \n"
                                    "💡 Предложить идею",
                                    parse_mode="html", reply_markup=markup,
                                    protect_content=protect_content_check)
                return
            else:
                blocks.access_blocked(message, us_id, full_name_user, username, client)
                return
    # обработчик ответного сообщения для команды 23
    try:
        cursor.execute('SELECT search_rfc FROM rfc_number WHERE user_id = ' + str(us_id))
        search_rfc = cursor.fetchone()[0]
    except (Exception,):
        search_rfc = 0
    if search_rfc == 9:
        # print("тест")
        idea_message = message.text.lower()
        full_name_from_bd = firewall_mars.id_in_name(us_id)

        text_idea = f"<b>⚠ Внимание! Получена идея от пользователей системы</b>\n" \
                    f" \n" \
                    f"🧑🏼‍💻 Пользователь: <b>{full_name_from_bd}</b>\n" \
                    f"✅ Предложение: <b>{idea_message}</b>\n"
        admins.admin_notification_message(client, text_idea)

        client.send_message(message.chat.id, "Ваше сообщение отправлено администраторам системы",
                            protect_content=protect_content_check)
        postgres_init.rfc_number(user_id=us_id, user_name=us_name, user_surname=us_surname, username=username,
                                 search_rfc=0, last_rfc_number="XXXX/202X")
        return

    if "/command26" in message.text.lower():
        access_check = firewall_mars.access_check(message.from_user.id)
        if access_check:
            config_line = message.text.lower()
            config_line_answer = settings_config.input_config_line(config_line, us_id, us_name, us_surname, username)
            if config_line_answer:
                client.send_message(message.chat.id,
                                    "✅ Конфиг настроек успешно применен",
                                    parse_mode="html",
                                    protect_content=protect_content_check)
            else:
                client.send_message(message.chat.id,
                                    "❌ Ошибка применения конфига настроек. \n"
                                    "Повторите позже или обратитесь к администратору системы",
                                    parse_mode="html",
                                    protect_content=protect_content_check)
            return
        else:
            blocks.access_blocked(message, us_id, full_name_user, username, client)
            return

    menu_call = ['запуск системы', 'главное меню', "меню", "menu", "/command08"]
    for menu_el in menu_call:
        if menu_el in message.text.lower():
            access_check = firewall_mars.access_check(message.from_user.id)
            if access_check:
                logs.log_pass(us_id, 'Команда', f'/menu')

                markup = keyboards.menu_keyboard(us_id)

                client.send_chat_action(message.chat.id, action="typing")
                client.send_message(message.chat.id,
                                    "<b>Главное меню</b>\n"
                                    " \n"
                                    "Поиск информации, статус RFC, настройка фильтров системы.\n"
                                    "Выбери интересующий тебя раздел.", reply_markup=markup,
                                    parse_mode="html",
                                    protect_content=protect_content_check)
                return
            else:
                blocks.access_blocked(message, us_id, full_name_user, username, client)
                return
    ################################################################################
    # НАСТРОЙКИ#####################################################################
    ################################################################################
    settings_call = ['settings', 'настройки',
                     "главное меню настроек",
                     "/command09"]
    for settings_el in settings_call:
        if settings_el in message.text.lower():
            access_check = firewall_mars.access_check(message.from_user.id)
            if access_check:
                logs.log_pass(us_id, 'Команда', f'/settings')

                client.send_chat_action(message.chat.id, action="typing")
                client.send_message(message.chat.id,
                                    "<b>Меню настроек</b>\n"
                                    "Разделы настроек, которые вы можете изменять. "
                                    "Каждая кнопка отображает определенный фильтр системы\n"
                                    " \n",
                                    parse_mode="html",
                                    reply_markup=keyboards.main_setting_keyboard(us_id),
                                    protect_content=protect_content_check)
                return
            else:
                blocks.access_blocked(message, us_id, full_name_user, username, client)
                return
    ################################################################################
    # ИНФОРМАЦИЯ
    ################################################################################
    info_call = ['info', 'информация', 'версия', 'инфо', "/command10"]
    for info_el in info_call:
        if info_el in message.text.lower():
            access_check = firewall_mars.access_check(message.from_user.id)
            if access_check:
                logs.log_pass(us_id, 'Команда', f'/info')

                cursor.execute(f'SELECT access FROM initialization_user WHERE user_id = {message.from_user.id}')
                access = cursor.fetchone()[0]

                unic_user = log_analysis.unic_user()
                answer_message_1 = "<b>Системная информация:</b>\n" + \
                                   "● Уровень доступа: <b>" + str(access) + "</b>\n" + \
                                   "● Версия системы: <b>" + str(configs.version) + "</b> от <b>" + \
                                   str(configs.data_version_update) + "</b> \n \n"

                answer_message_admin = "<b>Панель администрирования:</b>\n" + \
                                       "● Количество пользователей бота: <b>" + str(unic_user) + "</b>\n" + \
                                       " \n"

                answer_message_2 = "● " + str(configs.link['Список версий']) + "\n" + \
                                   " \n" + \
                                   "<b>Полезные ссылки:</b>\n" + \
                                   "● " + str(configs.link['Инструкция бот']) + "\n" + \
                                   "● " + str(configs.link['Инструкция 1c']) + "\n" + \
                                   "● " + str(configs.link["ИС '1С'"]) + "\n" + \
                                   "● " + str(configs.link['Список SRFC']) + "\n" + \
                                   " \n" + \
                                   "<b>RFC Informer Bot предназначен для поиска и " + \
                                   "фильтрации информации в ИС '1C'</b>"
                if str(access) == "Разработчик":
                    full_answer_message = answer_message_1 + \
                                          answer_message_admin + \
                                          answer_message_2
                else:
                    full_answer_message = answer_message_1 + answer_message_2

                # ------работаем с подсказками
                clue_answer_list = "HH,"

                clue, clue_body, clue_cod = clues.clue_bd("Доступа")
                clue_answer_list += clue_cod + ','

                clue, clue_body, clue_cod = clues.clue_bd(access)
                clue_answer_list += clue_cod + ','

                client.send_chat_action(message.chat.id, action="typing")
                client.send_message(message.chat.id, full_answer_message,
                                    parse_mode="html",
                                    reply_markup=keyboards.main_info_keyboard(us_id, clue_answer_list),
                                    protect_content=protect_content_check)
                return
            else:
                blocks.access_blocked(message, us_id, full_name_user, username, client)
                return

    # help и ссылка на К
    help_call = ["help", 'помощь', "/command11"]
    for help_el in help_call:
        if help_el in message.text.lower():
            access_check = firewall_mars.access_check(message.from_user.id)
            if access_check:
                logs.log_pass(us_id, 'Команда', f'/help')

                cursor.execute(f'SELECT access FROM initialization_user WHERE user_id = {message.from_user.id}')
                access = cursor.fetchone()[0]

                # print(access)
                command_list, check_status_command_list = commands.command_list(access)
                client.send_message(message.chat.id,
                                    f"{configs.link['Инструкция бот']}\n"
                                    " \n"
                                    "<b>● Команды для пользователей системы:</b>\n"
                                    f"{command_list}"
                                    " \n"
                                    f"● Почта отдела: <b>{configs.email_name}</b>\n"
                                    f"● Контакты отдела: <b>{configs.workers['rfc_manager1']['Ссылка']}</b>,"
                                    f" <b>{configs.workers['rfc_manager2']['Ссылка']}</b>\n",
                                    parse_mode="html",
                                    protect_content=protect_content_check)

                # cursor, conn = postgres_init.postgres_init()

                cursor.execute(f'SELECT advice FROM advice_rfc WHERE user_id = {us_id}')
                advice = cursor.fetchone()[0]
                if advice == "advice on":
                    clue_answer_list = []

                    clue = "Доступа"
                    clue_answer = clues.clue_info(clue)
                    clue_answer_list.append(clue_answer)

                    if check_status_command_list:
                        clue_answer = clues.clue_info("Команда недоступна")
                        clue_answer_list.append(clue_answer)

                    clue_answer_full = ""
                    for clue_answer_el in clue_answer_list:
                        clue_answer_full = clue_answer_full + clue_answer_el + " \n"
                    clue_answer_full = clue_answer_full + clues.clue_answer_clue
                    client.send_message(message.chat.id, str(clue_answer_full),
                                        parse_mode="html", protect_content=protect_content_check)
                return
            else:
                blocks.access_blocked(message, us_id, full_name_user, username, client)
                return

    if '/cerberus' in message.text.lower():
        client.send_message(message.chat.id,
                            str(long_text.cerberus_command_description),
                            parse_mode="html",
                            protect_content=protect_content_check)
        return
    ################################################################################
    # ПОИСК ПО ПРОЕКТУ##############################################################
    ################################################################################

    rfc_nb = message.text.lower()

    result_clear_5 = re.search(neuron.pattern_5_var1, rfc_nb)
    if result_clear_5 is not None:
        # проверяем есть ли также в запросе номер рфс из 1с
        result_clear_1 = re.search(neuron.pattern_5_var2, rfc_nb)
        if result_clear_1 is not None:
            task = result_clear_1.group(0)
            rfc_search.search_rfc_main(client, task, message, us_id, us_name,
                                       us_surname, username, protect_content_check)
            return
        else:
            task = result_clear_5.group(0)
            naumen_search.naumen_creator_message(client, task, message, us_id,
                                                 us_name, us_surname, username, protect_content_check)
        return

    # блок поиска информации об рфс
    status_rfc_call = ["статус rfc", 'rfc_search', "/command12", "🔎 поиск rfc"]
    for status_rfc_el in status_rfc_call:
        if status_rfc_el in message.text.lower():
            access_check = firewall_mars.access_check(message.from_user.id)
            if access_check:
                logs.log_pass(us_id, 'Действие', f'Глубокий поиск')
                client.send_chat_action(message.chat.id, action="typing")
                client.send_message(message.chat.id,
                                    "✏ Для поиска информации, введите один из следующих ключей: \n"
                                    "● Номер RFC в формате <b>XXXX/202X</b>\n"
                                    "● Номер SRFC в формате <b>SRFCXXX</b>\n"
                                    "● Название RFC или его часть\n"
                                    "● Название проекта\n"
                                    "● Номер Task в формате <b>TASKXXXXXXXX</b>\n",
                                    parse_mode="html",
                                    protect_content=protect_content_check)
                postgres_init.rfc_number(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                         username=username, search_rfc=1, last_rfc_number="XXXX/202X")
                return
            else:
                blocks.access_blocked(message, us_id, full_name_user, username, client)
                return

    # cursor, conn = postgres_init.postgres_init()

    try:
        cursor.execute('SELECT search_rfc FROM rfc_number WHERE user_id = ' + str(us_id))
        search_rfc = cursor.fetchone()[0]
    except (Exception,):
        search_rfc = 0
    if search_rfc == 1:
        rfc_nb = message.text.lower()
        if len(rfc_nb) >= 4:
            rfc_search.search_rfc_main(client, rfc_nb, message, us_id,
                                       us_name, us_surname, username, protect_content_check)
        else:
            client.send_chat_action(message.chat.id, action="typing")
            client.send_message(message.chat.id,
                                "Ошибка поиска! Слишком короткий запрос!\n"
                                "Длина запроса должна быть более 4 символов",
                                parse_mode="html",
                                protect_content=protect_content_check)
        return

    if '/command03' == message.text.lower():
        access_check = firewall_mars.access_check(message.from_user.id)
        if access_check:
            for admin_id in firewall_mars.level_list_check('Разработчик'):
                if admin_id == message.from_user.id:
                    web_access_keyboard = keyboards.web_access_keyboard()
                    client.send_message(message.chat.id,
                                        'Добрый день!\n'
                                        '\n'
                                        'Вас приветствует модуль предоставления доступа в систему.\n'
                                        'Перед предоставлением доступа рекомендуем посетить краткую '
                                        'справку по работе команды',
                                        reply_markup=web_access_keyboard)
                    return
            else:
                command_blocked(message, us_id, full_name_user, username)
                return
        else:
            blocks.access_blocked(message, us_id, full_name_user, username, client)
            return

    if '/command27' in message.text.lower():
        access_check = firewall_mars.access_check(message.from_user.id)
        if access_check:
            for admin_id in firewall_mars.level_list_check('Разработчик'):
                if admin_id == message.from_user.id:
                    web_search_1c = keyboards.web_search_1c_keyboard()
                    client.send_message(message.chat.id, 'Модуль для поиска данных о пользователя',
                                        reply_markup=web_search_1c,
                                        parse_mode='html')
                    return
            else:
                command_blocked(message, us_id, full_name_user, username)
                return
        else:
            blocks.access_blocked(message, us_id, full_name_user, username, client)
            return
    ################################################################################
    # ПОИСК ИНФОРМАЦИИ БЕЗ НАЖАТИЯ КНОПОК###########################################
    ################################################################################
    access_check = firewall_mars.access_check(message.from_user.id)
    if access_check:
        rfc_nb = message.text.lower()

        result_clear_3 = re.search(neuron.pattern_3, rfc_nb)

        if result_clear_3 is not None:
            task = result_clear_3.group(0)
            rfc_search.search_rfc_main(client, task, message, us_id, us_name,
                                       us_surname, username, protect_content_check)
            return

        result_clear_1 = re.search(neuron.pattern_1, rfc_nb)

        if result_clear_1 is not None:
            task = result_clear_1.group(0)
            task = task.replace("\\", '/')
            task = task.replace('|', '/')
            task = task.replace('-', '/')
            task = task.replace('_', '/')
            client.reply_to(message, "Возможно, вы имели в виду RFC "
                                     "<b>" + str(task) + "</b>", parse_mode="html",
                            protect_content=protect_content_check)
            rfc_search.search_rfc_main(client, task, message, us_id, us_name,
                                       us_surname, username, protect_content_check)
            return

        result_clear_4 = re.search(neuron.pattern_4, rfc_nb)
        if result_clear_4 is not None:
            # print (result_clear_4)
            task = result_clear_4.group(0)
            # print (task)
            while len(task) < 9:
                task = "0" + task
            client.reply_to(message,
                            "Возможно, вы имели в виду RFC <b>" + str(task) + "</b>",
                            parse_mode="html",
                            protect_content=protect_content_check)
            rfc_search.search_rfc_main(client, task, message, us_id, us_name,
                                       us_surname, username, protect_content_check)
            return

        result_clear_2 = re.search(neuron.pattern_2, rfc_nb)
        if result_clear_2 is not None:
            task = result_clear_2.group(0)
            # print (task)
            now = datetime.now()

            if len(task) == 4:
                client.reply_to(message,
                                f"Возможно, вы имели в виду "
                                f"RFC <b>{task}/{now.year}</b>", parse_mode="html",
                                protect_content=protect_content_check)
                task = str(task) + "/202"
                # client.setMessageReaction(message.chat.id, message_id=message, "🔥")
            elif len(task) == 8:
                client.reply_to(message, "Возможно, вы имели в виду "
                                         "<b>TASK" + str(task) + "</b>", parse_mode="html",
                                protect_content=protect_content_check)
                task = "TASK" + str(task)
            elif len(task) == 3:
                client.reply_to(message, "Возможно, вы имели в виду "
                                         "<b>SRFC" + str(task) + "</b>", parse_mode="html",
                                protect_content=protect_content_check)
                task = "SRFC" + str(task)
            elif len(task) == 5:
                client.reply_to(message, "Возможно, вы имели в виду "
                                         "<b>ЗНИ: " + str(task) + "</b>", parse_mode="html",
                                protect_content=protect_content_check)
                naumen_search.naumen_creator_message(client, task, message, us_id,
                                                     us_name, us_surname, username, protect_content_check)
                return

            rfc_search.search_rfc_main(client, task, message, us_id, us_name,
                                       us_surname, username, protect_content_check)
            return
        markup = keyboards.menu_keyboard(us_id)

        reaction_type_not_answer = ["🤷‍♂", "🤷", "🤷‍♀"]
        client.set_message_reaction(message.chat.id, message_id=message.message_id,
                                    reaction=[types.ReactionTypeEmoji(random.choice(reaction_type_not_answer))],
                                    is_big=True
                                    )

        client.send_chat_action(message.chat.id, action="typing")
        client.send_message(message.chat.id,
                            "<b>Не сработал ни один обработчик событий.</b>\n"
                            "Возможно, что-то не так. 🤔\n"
                            "Главное меню обновлено (на всякий случай)", reply_markup=markup, parse_mode="html",
                            protect_content=protect_content_check)
        logs.log_pass(us_id, 'Команда', f'Неизвестная команда - {message.text}')
        return
    else:
        blocks.access_blocked(message, us_id, full_name_user, username, client)
        return


@client.message_handler(content_types=['web_app_data'])
def web_app(message):
    us_id_admin = message.from_user.id
    # username_user = None
    full_name_admin = message.from_user.full_name
    res_data = json.loads(message.web_app_data.data)

    if 'Изменение уровня доступа' in str(message.web_app_data.button_text):
        try:
            cursor_main.execute(f'SELECT username FROM initialization_user WHERE user_id = {res_data["id"]}')
            username_user = cursor_main.fetchone()[0]
        except (Exception,):
            username_user = 'Не определен'
        protect_content_check = protect_content.protect_content_check_fn(res_data["id"])
        if protect_content_check:
            p_content = 'Копирование запрещено'
        else:
            p_content = 'Копирование разрешено'

        postgres_init.initialization(user_id=res_data["id"], user_name=res_data["name"], username=username_user,
                                     department=res_data["department"], guid=res_data["guid"],
                                     access=res_data["access"])

        if str(res_data['p_content']).lower() == 'да':
            p_content_init = 0
        elif str(res_data['p_content']).lower() == "нет":
            p_content_init = 1
        else:
            p_content_init = 1

        postgres_init.protect_content_fn(user_id=res_data["id"], protect_content_check=p_content_init)

        markup = keyboards.menu_keyboard(us_id_admin)
        client.send_message(message.chat.id,
                            f'Данные переданы в базу\n'
                            f'\n'
                            f'Имя пользователя: <code>{res_data["name"]}</code>\n'
                            f'Id пользователя: <code>{res_data["id"]}</code>\n'
                            f'Отдел пользователя: <code>{res_data["department"]}</code>\n'
                            f'guid пользователя: <code>{res_data["guid"]}</code>\n'
                            f'Уровень доступа: <code>{res_data["access"]}</code>\n'
                            f'Безопасность: <code>{p_content}</code>\n',
                            reply_markup=markup, parse_mode="html"
                            )
        logs.log_pass(us_id_admin, 'Команда', f'/command03')

        try:
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton('❌ Пропустить ознакомление',
                                               callback_data='Запуск бота')
            item2 = types.InlineKeyboardButton('📝 Основные положения',
                                               callback_data='Ознакомление с ботом')
            item3 = types.InlineKeyboardButton('Инструкция бот',
                                               url="https://confluence.jet.su/pages/"
                                                   "viewpage.action?pageId=162355250")
            markup.add(item1, item2, item3)
            client.send_message(int(res_data["id"]),
                                "✅ Доступ к RFC Informer bot, предоставлен\n"
                                " \n"
                                f'Уровень доступа: {res_data["access"]}\n'
                                " \n"
                                "📲 Для продолжения работы ознакомьтесь с мануалом",
                                parse_mode="html", reply_markup=markup,
                                protect_content=True)

            text_access_init = f'Пользователь: <b>{res_data["name"]}</b>, уведомлен о предоставлении ему доступа.\n' \
                               f" \n" \
                               f"Доступ предоставил администратор: <b>{full_name_admin}</b>\n" \
                               f'Уровень предоставляемого доступа: <b>{res_data["access"]}</b>\n'
            admins.admin_notification_message(client, text_access_init)
            return
        except (Exception,):
            client.send_message(message.chat.id,
                                "⚠️ Ошибка в работке команды. \n"
                                " \n"
                                "Для корректной работы отправьте команду в формате "
                                "<b>/command03 : id пользователя</b>\n"
                                " \n"
                                "Пр. <i>/command03:78635896</i>",
                                parse_mode="html", protect_content=False)
        return

    if 'Регистрация в системе' in str(message.web_app_data.button_text):
        hash_password = integrations.hash_password(res_data["password"])
        auth_1c_check = integrations.auth_1c_check(res_data["name"], hash_password)

        us_id_reg = message.from_user.id
        username = message.from_user.username

        if auth_1c_check == 'True':
            client.send_message(message.chat.id, 'Регистрация в ИС 1С успешна',
                                reply_markup=keyboards.menu_keyboard(us_id_reg),
                                protect_content=True
                                )

            postgres_init.initialization(user_id=us_id_admin, user_name=res_data["name"], username=username,
                                         department='', guid='', access="Пользователь")
            postgres_init.protect_content_fn(user_id=us_id_admin, protect_content_check=0)

            notification = f'⚠️ Внимание! Успешная регистрация в системе\n' \
                           f' \n' \
                           f'Пользователь: <code>{res_data["name"]}</code>\n' \
                           f'ID пользователя: <code>{us_id_reg}</code>\n'

            hash_object = hashlib.sha1(res_data["password"].encode('utf-8'))
            hash_password = hash_object.hexdigest()

            last_data = str(datetime.now().date())

            postgres_init.authentication_1c(us_id_reg, res_data["name"], hash_password, 1, last_data)

            admins.admin_notification_message(client, notification)
            logs.log_pass(us_id_reg, 'Действие', f'Успешная регистрация')
            return
        elif auth_1c_check == 'False':
            client.send_message(message.chat.id,
                                'Регистрация в ИС 1С не успешна. \n'
                                'Проверьте правильность заполнения данных.\n'
                                'Имя пользователя в формате "Фамилия Имя", на Русском языке\n'
                                'Например: Сидоров Алексей'
                                )

            # уведомление администраторов
            blocks.access_blocked(message, us_id_reg, res_data["name"], username, client)
            return

    if 'Поиск данных о пользователе' in str(message.web_app_data.button_text):
        id_user_search = res_data["id"]
        id_user_search = int(id_user_search)
        try:
            cursor_main.execute(f'SELECT * FROM initialization_user WHERE user_id = {id_user_search}')
            init_user_list = cursor_main.fetchall()[0]
            protect_content_check = protect_content.protect_content_check_fn(id_user_search)
            if protect_content_check:
                p_content = 'Копирование запрещено'
            else:
                p_content = 'Копирование разрешено'

            client.send_message(message.chat.id,
                                f'Доступная информация о пользователе,\n'
                                f'\n'
                                f'Имя пользователя: <code>{init_user_list[1]}</code>\n'
                                f'Ник пользователя: <code>{init_user_list[2]}</code>\n'
                                f'Id пользователя: <code>{init_user_list[0]}</code>\n'
                                f'Отдел пользователя: <code>{init_user_list[3]}</code>\n'
                                f'guid пользователя: <code>{init_user_list[4]}</code>\n'
                                f'Уровень доступа: <code>{init_user_list[5]}</code>\n'
                                f'Безопасность: <code>{p_content}</code>\n',
                                parse_mode="html")
        except(Exception,):
            client.send_message(us_id_admin,
                                'Ошибка поиска! Данные не найдены')
            return


# КОЛЛБЕКИ--------------------------------------------------------------------------------------------------------------
@client.callback_query_handler(func=lambda message: True)
def call_init(call):
    callbacks.callback_main_bot(call, client, calendar_build, check_l_name)


def debug_mode(debug_mode_lan):
    """
    Функция для выбора варианта запуска бота. В тестовом или прод режиме.
    В состоянии debug_mode_lan = False, бот работает в обычном режиме и перезапускается для ошибок
    В состоянии debug_mode_lan = True, бот запускается в тестовом режиме.
    Запуск происходит быстрее и перезапуск при ошибках не происходит
    :param debug_mode_lan: Переменная, которая определяет режим запуска
    :return: Процедура
    """
    if not debug_mode_lan:
        # запуск и проверка серверной части
        servers.start_server()
        while True:
            try:
                client.polling(none_stop=True, interval=0, timeout=123)
                schedule.run_pending()
                time.sleep(1)
            except BaseException as e:
                install(show_locals=True)
                errors.error_bot(e, 77777777, protect_content, client)
                client.stop_polling()
                time.sleep(3)
    else:
        client.polling(none_stop=True, interval=0, timeout=123)


# Обработчик ошибок-----------------------------------------------------------------------------------------------------
# debug_mode_lan=True, для запуска тестового режима
debug_mode(debug_mode_lan=True)
