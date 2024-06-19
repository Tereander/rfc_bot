from telebot import types

import firewall_mars
import postgres_init
import configs


cursor, conn = postgres_init.postgres_init()


def menu_keyboard(us_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # поменяй кнопки в КОЛБЕКИ И В ОБРАБОТЧИКЕ СОБЫТИЙ В КОНЦЕ
    item1 = types.KeyboardButton("🔎 Поиск RFC")
    item2 = types.KeyboardButton("💬 Помощь")

    item3 = types.KeyboardButton("📚 Информация")
    item4 = types.KeyboardButton("⚙️ Настройки")

    item5 = types.KeyboardButton("📆 Календарь работ")
    item6 = types.KeyboardButton("📆 Список работ")

    markup.add(item1, item2)
    markup.add(item3, item4)
    try:
        guid_1c, check_l_name_button = firewall_mars.id_in_guid(us_id)
    except (Exception, ):
        check_l_name_button = False

    if check_l_name_button:
        markup.add(item5)
    else:
        markup.add(item5, item6)
    return markup


def main_setting_keyboard(us_id):
    """
    :param us_id: id пользователя в телеграм
    :return: возвращает пользователю клавиатуру с меню настроек
    Функция предназначена для вызова самостоятельного меню с клавиатурой,
    для главного меню настроек
    """
    keyboard_settings = types.InlineKeyboardMarkup(row_width=2)  # вывод кнопок в 1 колонку
    # zero = types.InlineKeyboardButton('Статус моих настроек',
    # callback_data='Статус настроек')
    one = types.InlineKeyboardButton('🖥 Отображение RFC',
                                     callback_data='описание Информация о RFC')
    two = types.InlineKeyboardButton('💡 Статус подсказок',
                                     callback_data='описание Статус подсказок')
    three = types.InlineKeyboardButton('✏️ Длина ответа',
                                       callback_data='длина ответа')
    four = types.InlineKeyboardButton('✉️ Рассылки',
                                      callback_data='Рассылки')
    five = types.InlineKeyboardButton('📊 Оценка алгоритмов',
                                      callback_data='оценка алгоритмов')
    six = types.InlineKeyboardButton('📅 Календарь',
                                     callback_data='вид календаря')
    seven = types.InlineKeyboardButton('🙍🏼‍♀️ Модуль личности',
                                       callback_data='модуль личности')
    eight = types.InlineKeyboardButton('🔀 Дежурные смены',
                                       callback_data='дежурные смены')
    nine = types.InlineKeyboardButton('🚫 Отображение ошибок',
                                      callback_data='отображение ошибок')
    try:
        access_level = firewall_mars.id_in_level(us_id)
    except (Exception, ):
        access_level = 5

    if access_level == 1:
        keyboard_settings.add(one, two, three, four, five, six, seven, eight, nine)
    else:
        keyboard_settings.add(one, two, three, four, five, six, seven, eight)
    # keyboard.add(zero)
    return keyboard_settings


def web_access_keyboard():
    """
    Модуль формирует и возвращает reply клавиатуру с веб-приложением для
    изменения уровня доступа/ имени и иной информации. Доступна только для администраторов
    :return: Клавиатура типа reply
    """
    web_access = types.ReplyKeyboardMarkup(resize_keyboard=True)
    one = types.KeyboardButton('Изменение уровня доступа 👨🏻‍💻',
                               web_app=types.WebAppInfo(url='https://tereander.github.io/rfc_bot/index.html')
                               )
    web_access.add(one)
    return web_access


def bank_zni_message_keyboard(uuid):
    keyboard_settings = types.InlineKeyboardMarkup(row_width=2)  # вывод кнопок в 1 колонку
    # zero = types.InlineKeyboardButton('Статус моих настроек',
    # callback_data='Статус настроек')
    item8 = types.InlineKeyboardButton(text='🖥 Согласование Naumen',
                                       callback_data=f'Согласование Naumen {uuid}')
    item9 = types.InlineKeyboardButton(text='🖨 Вложения Naumen',
                                       callback_data=f'План работ Naumen {uuid}')

    keyboard_settings.add(item8, item9)

    return keyboard_settings


def web_auth_1c_keyboard():
    """
    :return: Клавиатура типа reply
    Модуль формирует и возвращает reply клавиатуру с веб-приложением для
    открытия окна регистрации в системе. Доступна только для всех пользователей
    """
    web_auth_1c = types.ReplyKeyboardMarkup(resize_keyboard=True)
    one = types.KeyboardButton('Регистрация в системе 📲',
                               web_app=types.WebAppInfo(url='https://tereander.github.io/rfc_bot/auth.html')
                               )
    web_auth_1c.add(one)
    return web_auth_1c


def web_search_1c_keyboard():
    """
    :return: Клавиатура типа reply
    Модуль формирует и возвращает reply клавиатуру с веб-приложением для
    поиска данных о пользователе по ID. Доступна только для всех администраторов
    """
    web_search_1c = types.ReplyKeyboardMarkup(resize_keyboard=True)
    one = types.KeyboardButton('Поиск данных о пользователе 📲',
                               web_app=types.WebAppInfo(url='https://tereander.github.io/rfc_bot/search.html')
                               )
    web_search_1c.add(one)
    return web_search_1c


def cerberus_keyboard():
    """
    :return: Модуль клавиатуры с кнопками
    Модуль генерирует клавиатуру для пользователя, если его заблокировал модуль cerberus
    """
    keyboard_settings = types.InlineKeyboardMarkup(row_width=2)  # вывод кнопок в 1 колонку
    one = types.InlineKeyboardButton('📘 Сerberus ?',
                                     callback_data='Сerberus')
    two = types.InlineKeyboardButton('⛔️ Это ошибка !',
                                     callback_data='Сerberus error')
    keyboard_settings.add(one, two)
    # keyboard.add(zero)
    return keyboard_settings


def main_info_keyboard(us_id, clue_answer_list):
    """
    Функция, которая вызывает основную клавиатуру модуля информации
    :param us_id: id пользователя в телеграм
    :param clue_answer_list: текстовая переменная, с набором шифрам подсказок
    :return: Объект клавиатуры с кнопками
    """
    keyboard = types.InlineKeyboardMarkup(row_width=2)  # вывод кнопок в 1 колонку
    one = types.InlineKeyboardButton('📘 Ознакомление с ботом', callback_data='Ознакомление с ботом')
    sp_rfc = types.InlineKeyboardButton('📂 Статусы RFC', callback_data='Статусы RFC списком')
    config_line_button = types.InlineKeyboardButton('📎 Получить config настроек',
                                                    callback_data='config запрос')
    user_card = types.InlineKeyboardButton('📰 Карточка пользователя',
                                           callback_data='Карточка пользователя')
    two = types.InlineKeyboardButton('📘 Инструкция бот',
                                     url="https://confluence.jet.su/pages/"
                                         "viewpage.action?pageId=162355250")
    three = types.InlineKeyboardButton('📙 Инструкция 1C',
                                       url="https://confluence.jet.su/pages/"
                                           "viewpage.action?pageId=157929193")
    four = types.InlineKeyboardButton('📙 ИС 1C',
                                      url=f"{configs.auth_1c['link']}/ru_RU/")
    five = types.InlineKeyboardButton('📗 Список SRFC',
                                      url="https://confluence.jet.su/display/"
                                          "pochtabank/SRFC")
    six = types.InlineKeyboardButton('📄 Шаблоны',
                                     callback_data='шаблоны')
    seven = types.InlineKeyboardButton('💡 Справка',
                                       callback_data=str(clue_answer_list))

    # -----заканчиваем с подсказками

    try:
        access_level = firewall_mars.id_in_level(us_id)
    except (Exception, ):
        access_level = 5

    if access_level == 1 or access_level == 2:
        keyboard.add(sp_rfc, six)

    keyboard.add(one, two)
    keyboard.add(config_line_button, user_card)
    keyboard.add(three, four)
    keyboard.add(five)

    cursor.execute(f'SELECT advice FROM advice_rfc WHERE user_id = {us_id}')
    advice = cursor.fetchone()[0]
    if advice == "advice on":
        keyboard.add(seven)

    return keyboard
