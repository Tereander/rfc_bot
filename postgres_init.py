import colorama
from colorama import Fore, Style
import psycopg2
from psycopg2 import Error
import psycopg2.extensions
import configparser

import configs


config_file = configparser.ConfigParser()
config_file.read('config.ini')

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)


def postgres_init():
    try:
        # Подключение к существующей базе данных
        conn = psycopg2.connect(database=str(configs.sql_database['database']),
                                user=str(configs.sql_database['user']),
                                password=str(configs.sql_database['password']),
                                host=str(configs.sql_database['host']),
                                port=str(configs.sql_database['port'])
                                )
        # print(conn)
        # conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # Курсор для выполнения операций с базой данных
        cursor = conn.cursor()
        # colorama.init()
        # print(Fore.BLUE + "POSTGRESQL CONNECTED SUCCESSFULLY")
        # print(Style.RESET_ALL)
        # cursor, conn = postgres_init()
        return cursor, conn
    except (Exception, Error) as error:
        colorama.init()
        print(Fore.RED + "POSTGRESQL CONNECTED ERROR", error)
        print(Style.RESET_ALL)
        # уведомляем администраторов
        # text_notification = ''
        # admins.admin_notification_message(client, text_notification)
        return

    # Подключение к существующей базе данных
    # conn = psycopg2.connect(database=config.sql_database['database'],
    #                         user=config.sql_database['user'],
    #                         password=config.sql_database['password'],
    #                         host=config.sql_database['host'],
    #                         port=config.sql_database['port'],
    #                         )
    # conn.set_client_encoding('UTF8')
    # cursor = conn.cursor()
    # return cursor, conn


def authentication_1c(user_id: int, user_login: str, hash_password: str, check_access: int, last_data: str):
    cursor_authentication_1c, conn_authentication_1c = postgres_init()
    cursor_authentication_1c.execute('INSERT INTO authentication_1c '
                                     '(user_id, user_login, hesh_password, check_access, last_data) '
                                     'VALUES (%s, %s, %s, %s, %s) '
                                     'ON CONFLICT (user_id) '
                                     'DO UPDATE SET (user_id, user_login, hesh_password, check_access, last_data) = '
                                     '(EXCLUDED.user_id, EXCLUDED.user_login, EXCLUDED.hesh_password, '
                                     'EXCLUDED.check_access, EXCLUDED.last_data);',
                                     (user_id, user_login, hash_password, check_access, last_data))
    conn_authentication_1c.commit()


def exp_search3658(user_id: int, user_name: str, user_surname: str, username: str, activate: str):
    cursor_exp, conn_exp = postgres_init()
    cursor_exp.execute('INSERT INTO exp_rfc_search '
                       '(user_id, user_name, user_surname, username, activate) '
                       'VALUES (%s, %s, %s, %s, %s) '
                       'ON CONFLICT (user_id) '
                       'DO UPDATE SET (user_id, user_name, user_surname, username, activate) = '
                       '(EXCLUDED.user_id, EXCLUDED.user_name, EXCLUDED.user_surname, '
                       'EXCLUDED.username, EXCLUDED.activate);',
                       (user_id, user_name, user_surname, username, activate))
    conn_exp.commit()
    # cursor.close()
    # conn.close()


def initialization(user_id: int, user_name: str, username: str, department: str, guid: str, access: str):
    cursor_initialization, conn_initialization = postgres_init()
    cursor_initialization.execute('INSERT INTO initialization_user'
                                  '(user_id, user_name, username, department, guid, access)'
                                  'VALUES (%s, %s, %s, %s, %s, %s) '
                                  'ON CONFLICT (user_id) '
                                  'DO UPDATE SET (user_id, user_name, username, department, guid, access) = '
                                  '(EXCLUDED.user_id, EXCLUDED.user_name, EXCLUDED.username, '
                                  'EXCLUDED.department, EXCLUDED.guid, EXCLUDED.access);',
                                  (user_id, user_name, username, department, guid, access))
    conn_initialization.commit()
    # cursor.close()
    # conn.close()


def rfc_number(user_id: int, user_name: str, user_surname: str, username: str, search_rfc: int, last_rfc_number: str):
    cursor_rfc_number, conn_rfc_number = postgres_init()
    cursor_rfc_number.execute('INSERT INTO rfc_number '
                              '(user_id, user_name, user_surname, username, search_rfc, last_rfc_number)'
                              ' VALUES (%s, %s, %s, %s, %s, %s) '
                              'ON CONFLICT (user_id) '
                              'DO UPDATE SET (user_id, user_name, user_surname, username, '
                              'search_rfc, last_rfc_number) = '
                              '(EXCLUDED.user_id, EXCLUDED.user_name, EXCLUDED.user_surname, EXCLUDED.username, '
                              'EXCLUDED.search_rfc, EXCLUDED.last_rfc_number);',
                              (user_id, user_name, user_surname, username, search_rfc, last_rfc_number))
    conn_rfc_number.commit()
    # cursor.close()
    # conn.close()


def full_view_rfc(user_id: int, user_name: str, user_surname: str, username: str, view_rfc: str):
    cursor_full_view_rfc, conn_full_view_rfc = postgres_init()
    cursor_full_view_rfc.execute('INSERT INTO full_view_rfc '
                                 '(user_id, user_name, user_surname, username, view_rfc) '
                                 'VALUES (%s, %s, %s, %s, %s) '
                                 'ON CONFLICT (user_id) '
                                 'DO UPDATE SET (user_id, user_name, user_surname, username, view_rfc) = '
                                 '(EXCLUDED.user_id, EXCLUDED.user_name, EXCLUDED.user_surname, '
                                 'EXCLUDED.username, EXCLUDED.view_rfc);',
                                 (user_id, user_name, user_surname, username, view_rfc))
    conn_full_view_rfc.commit()
    # cursor.close()
    # conn.close()


def advice_rfc(user_id: int, user_name: str, user_surname: str, username: str, advice: str):
    cursor_advice, conn_advice = postgres_init()
    cursor_advice.execute('INSERT INTO advice_rfc '
                          '(user_id, user_name, user_surname, username, advice) '
                          'VALUES (%s, %s, %s, %s, %s) '
                          'ON CONFLICT (user_id) '
                          'DO UPDATE SET (user_id, user_name, user_surname, username, advice) = '
                          '(EXCLUDED.user_id, EXCLUDED.user_name, EXCLUDED.user_surname, '
                          'EXCLUDED.username, EXCLUDED.advice);',
                          (user_id, user_name, user_surname, username, advice))
    conn_advice.commit()
    # cursor.close()
    # conn.close()


def len_200(user_id: int, user_name: str, user_surname: str, username: str, stop200: str):
    cursor_len_200, conn_len_200 = postgres_init()
    cursor_len_200.execute('INSERT INTO len_200 '
                           '(user_id, user_name, user_surname, username, stop200) '
                           'VALUES (%s, %s, %s, %s, %s) '
                           'ON CONFLICT (user_id) '
                           'DO UPDATE SET (user_id, user_name, user_surname, username, stop200) = (EXCLUDED.user_id, '
                           'EXCLUDED.user_name, EXCLUDED.user_surname, EXCLUDED.username, EXCLUDED.stop200);',
                           (user_id, user_name, user_surname, username, stop200))
    conn_len_200.commit()
    # cursor.close()
    # conn.close()


def mode_test(user_id: int, user_name: str, user_surname: str, username: str, mode_test_fn: str):
    cursor_mode_test, conn_mode_test = postgres_init()
    cursor_mode_test.execute('INSERT INTO mode_test '
                             '(user_id, user_name, user_surname, username, mode_test) '
                             'VALUES (%s, %s, %s, %s, %s) '
                             'ON CONFLICT (user_id) '
                             'DO UPDATE SET (user_id, user_name, user_surname, username, '
                             'mode_test) = (EXCLUDED.user_id, '
                             'EXCLUDED.user_name, EXCLUDED.user_surname, EXCLUDED.username, EXCLUDED.mode_test);',
                             (user_id, user_name, user_surname, username, mode_test_fn))
    conn_mode_test.commit()
    # cursor.close()
    # conn.close()


def add_block_fn(user_id: int, user_name: str, user_surname: str, username: str, add_block: str):
    cursor_add_block, conn_add_block = postgres_init()
    cursor_add_block.execute('INSERT INTO add_block_table '
                             '(user_id, user_name, user_surname, username, add_block) '
                             'VALUES (%s, %s, %s, %s, %s) '
                             'ON CONFLICT (user_id) '
                             'DO UPDATE SET (user_id, user_name, user_surname, username, add_block) = '
                             '(EXCLUDED.user_id, '
                             'EXCLUDED.user_name, EXCLUDED.user_surname, EXCLUDED.username, EXCLUDED.add_block);',
                             (user_id, user_name, user_surname, username, add_block))
    conn_add_block.commit()
    # cursor.close()
    # conn.close()


def grade_el_fn(user_id: int, user_name: str, user_surname: str, username: str, grade_el: str):
    cursor_grade, conn_grade = postgres_init()
    cursor_grade.execute('INSERT INTO grade_el_table '
                         '(user_id, user_name, user_surname, username, grade_el) '
                         'VALUES (%s, %s, %s, %s, %s) '
                         'ON CONFLICT (user_id) '
                         'DO UPDATE SET (user_id, user_name, user_surname, username, grade_el) = (EXCLUDED.user_id, '
                         'EXCLUDED.user_name, EXCLUDED.user_surname, EXCLUDED.username, EXCLUDED.grade_el);',
                         (user_id, user_name, user_surname, username, grade_el))
    conn_grade.commit()
    # cursor.close()
    # conn.close()


def calendar_fn(user_id: int, user_name: str, user_surname: str, username: str, calendar_view: str):
    cursor_calendar, conn_calendar = postgres_init()
    cursor_calendar.execute('INSERT INTO calendar_table '
                            '(user_id, user_name, user_surname, username, calendar_view) '
                            'VALUES (%s, %s, %s, %s, %s) '
                            'ON CONFLICT (user_id) '
                            'DO UPDATE SET (user_id, user_name, user_surname, username, calendar_view) = '
                            '(EXCLUDED.user_id, '
                            'EXCLUDED.user_name, EXCLUDED.user_surname, EXCLUDED.username, EXCLUDED.calendar_view);',
                            (user_id, user_name, user_surname, username, calendar_view))
    conn_calendar.commit()
    # cursor.close()
    # conn.close()


def personal_mode_fn(user_id: int, personal_mode: str):
    cursor_personal_mode, conn_personal_mode = postgres_init()
    cursor_personal_mode.execute('INSERT INTO personal_mode_table (user_id, personal_mode) '
                                 'VALUES (%s, %s) ON CONFLICT (user_id) '
                                 'DO UPDATE SET (user_id, personal_mode) = '
                                 '(EXCLUDED.user_id, EXCLUDED.personal_mode);',
                                 (user_id, personal_mode))
    conn_personal_mode.commit()
    # cursor.close()
    # conn.close()


def protect_content_fn(user_id: int, protect_content_check: int):
    cursor_protect_content, conn_protect_content = postgres_init()
    cursor_protect_content.execute('INSERT INTO protect_content_table '
                                   '(user_id, protect_content_chek) '
                                   'VALUES (%s, %s) '
                                   'ON CONFLICT (user_id) '
                                   'DO UPDATE SET (user_id, protect_content_chek) = '
                                   '(EXCLUDED.user_id, EXCLUDED.protect_content_chek);',
                                   (user_id, protect_content_check))
    conn_protect_content.commit()


# def correct_name_fn(user_id: int, correct_name: str):
#     cursor_correct_name, conn_correct_name = postgres_init()
#     cursor_correct_name.execute('INSERT INTO correct_name '
#                                 '(us_id, name) VALUES (%s, %s) '
#                                 'ON CONFLICT (us_id) DO UPDATE SET (us_id, name) = (EXCLUDED.us_id, EXCLUDED.name);',
#                                 (user_id, correct_name))
#     conn_correct_name.commit()


def time_message_block_fn(user_id: int, time_block: int):
    cursor_message_block_name, conn_message_block_name = postgres_init()
    cursor_message_block_name.execute('INSERT INTO message_block_table '
                                      '(user_id, time_block) VALUES (%s, %s) '
                                      'ON CONFLICT (user_id) DO UPDATE SET (user_id, time_block) = '
                                      '(EXCLUDED.user_id, EXCLUDED.time_block);',
                                      (user_id, time_block))
    conn_message_block_name.commit()


def last_message_fn(user_id: int, time: int):
    cursor_last_message, conn_last_message = postgres_init()
    cursor_last_message.execute('INSERT INTO last_message_table '
                                '(user_id, time) VALUES (%s, %s) '
                                'ON CONFLICT (user_id) DO UPDATE SET (user_id, time) = '
                                '(EXCLUDED.user_id, EXCLUDED.time);',
                                (user_id, time))
    conn_last_message.commit()


def error_table_fn(user_id: int, error: str):
    cursor_error_table, conn_error_table = postgres_init()
    cursor_error_table.execute('INSERT INTO error_table '
                               '(user_id, error) VALUES (%s, %s) '
                               'ON CONFLICT (user_id) DO UPDATE SET (user_id, error) = '
                               '(EXCLUDED.user_id, EXCLUDED.error);',
                               (user_id, error))
    conn_error_table.commit()


def connect_bd(message):
    """
    Функция для работы с БД. Принимает блок message и выставляет стандартные настройки системы
    :param message: стандартный блок telegram
    :return: Процедура
    """
    us_id = message.from_user.id
    rfc_number(user_id=us_id, user_name=message.from_user.first_name, user_surname=message.from_user.last_name,
               username=message.from_user.username, search_rfc=0, last_rfc_number="XXXX/2022")
    full_view_rfc(user_id=us_id, user_name=message.from_user.first_name, user_surname=message.from_user.last_name,
                  username=message.from_user.username, view_rfc="not full")
    advice_rfc(user_id=us_id, user_name=message.from_user.first_name, user_surname=message.from_user.last_name,
               username=message.from_user.username, advice="advice on")
    # exp_search3658(user_id=us_id, user_name=message.from_user.first_name, user_surname=message.from_user.last_name,
    #                username=message.from_user.username, activate="False")
    len_200(user_id=us_id, user_name=message.from_user.first_name, user_surname=message.from_user.last_name,
            username=message.from_user.username, stop200="True")
    mode_test(user_id=us_id, user_name=message.from_user.first_name, user_surname=message.from_user.last_name,
              username=message.from_user.username, mode_test_fn="no")
    add_block_fn(user_id=us_id, user_name=message.from_user.first_name, user_surname=message.from_user.last_name,
                 username=message.from_user.username, add_block="False")
    grade_el_fn(user_id=us_id, user_name=message.from_user.first_name, user_surname=message.from_user.last_name,
                username=message.from_user.username, grade_el="True")
    calendar_fn(user_id=us_id, user_name=message.from_user.first_name, user_surname=message.from_user.last_name,
                username=message.from_user.username, calendar_view="Full")
    personal_mode_fn(user_id=us_id, personal_mode='on')
    error_table_fn(user_id=us_id, error='yes')
    # postgres_init.guid_table_fn(user_id=us_id, guid='')
