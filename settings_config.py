# import psycopg2

# import config
import postgres_init

cursor, conn = postgres_init.postgres_init()


def input_config_line(config_line: str, us_id: int, us_name: str, us_surname: str, username: str) -> True:
    """
    Функция принимает конфиг настроек пользователя в виде строки
    делит конфиг на отдельные настройки и выставляет значения в БД, в зависимости от указанных данных
    :param config_line: текстовая строка конфига пользователя
    :param us_id: id пользователя в telegram
    :param us_name: имя пользователя
    :param us_surname: фамилия пользователя
    :param username: никнейм пользователя
    :return: True
    """
    config_list = config_line.split()
    config_list.pop(0)
    config_line_check = None
    # print(config_list)
    for config_list_el in config_list:

        config_line_check = True
        # настройка длины рфс
        if "view_rfc-n" == config_list_el:
            postgres_init.full_view_rfc(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                        username=username, view_rfc="not full")
        if "view_rfc-f" == config_list_el:
            postgres_init.full_view_rfc(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                        username=username, view_rfc="full")

        # настройка подсказок рфс
        if "advice-f" == config_list_el:
            postgres_init.advice_rfc(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                     username=username, advice="advice off")
        if "advice-n" == config_list_el:
            postgres_init.advice_rfc(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                     username=username, advice="advice on")

        # настройка длины ответа
        if "len200-y" == config_list_el:
            postgres_init.len_200(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                  username=username, stop200="False")
        if "len200-n" == config_list_el:
            postgres_init.len_200(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                  username=username, stop200="True")

        # настройка оценки алгоритма
        if "grade-n" == config_list_el:
            postgres_init.grade_el_fn(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                      username=username, grade_el="False")
        if "grade-y" == config_list_el:
            postgres_init.grade_el_fn(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                      username=username, grade_el="True")

        # настройка статуса рассылок
        if "mailing_l-y" == config_list_el:
            postgres_init.add_block_fn(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                       username=username, add_block="False")
        if "mailing_l-n" == config_list_el:
            postgres_init.add_block_fn(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                       username=username, add_block="True")

        # настройка календаря
        if "calendar-f" == config_list_el:
            postgres_init.calendar_fn(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                      username=username, calendar_view="Full")
        if "calendar-n" == config_list_el:
            postgres_init.calendar_fn(user_id=us_id, user_name=us_name, user_surname=us_surname,
                                      username=username, calendar_view="Not Full")

        # настройка модуля личности
        if "personal_m-n" == config_list_el:
            postgres_init.personal_mode_fn(user_id=us_id, personal_mode='on')
        if "personal_m-f" == config_list_el:
            postgres_init.personal_mode_fn(user_id=us_id, personal_mode='off')
    return config_line_check


def output_config_line(us_id: int) -> str:
    """
    Функция запрашивает актуальные настройки системы из БД и формирует
    текстовую конфиг строку с краткой кодировкой состояния каждой настройки
    :param us_id: id пользователя в телеграм
    :return: текстовая строка содержащая сформированным конфигом системы
    """
    # config_line = None
    try:
        config_line = "/command26 "

        # настройка длины рфс
        cursor.execute('SELECT view_rfc FROM full_view_rfc WHERE user_id = ' + str(us_id))
        view_rfc = cursor.fetchone()[0]
        if view_rfc == "not full":
            config_line += "view_rfc-n "
        elif view_rfc == "full":
            config_line += "view_rfc-f "

        # настройка подсказок рфс
        cursor.execute('SELECT advice FROM advice_rfc WHERE user_id = ' + str(us_id))
        advice = cursor.fetchone()[0]
        if advice == "advice off":
            config_line += "advice-f "
        elif advice == "advice on":
            config_line += "advice-n "

        # настройка длины ответа
        cursor.execute('SELECT stop200 FROM len_200 WHERE user_id = ' + str(us_id))
        stop200 = cursor.fetchone()[0]
        if stop200 == "False":
            config_line += "len200-y "
        elif stop200 == "True":
            config_line += "len200-n "

        # настройка оценки алгоритма
        cursor.execute('SELECT grade_el FROM grade_el_table WHERE user_id = ' + str(us_id))
        grade_el = cursor.fetchone()[0]
        if grade_el == "False":
            config_line += "grade-n "
        elif grade_el == "True":
            config_line += "grade-y "

        # настройка статуса рассылок
        cursor.execute('SELECT add_block FROM add_block_table WHERE user_id = ' + str(us_id))
        add_block = cursor.fetchone()[0]
        if add_block == "False":
            config_line += "mailing_l-y "
        elif add_block == "True":
            config_line += "mailing_l-n "

        # настройка календаря
        cursor.execute('SELECT calendar_view FROM calendar_table WHERE user_id = ' + str(us_id))
        calendar_view = cursor.fetchone()[0]
        if calendar_view == "Full":
            config_line += "calendar-f "
        elif calendar_view == "Not Full":
            config_line += "calendar-n "

        # настройка модуля личности
        cursor.execute(f'SELECT personal_mode FROM personal_mode_table WHERE user_id = {us_id}')
        personal_mode = cursor.fetchone()[0]
        if personal_mode == "on":
            config_line += "personal_m-n "
        elif personal_mode == "off":
            config_line += "personal_m-f "

    except (Exception,):
        config_line = "Ошибка формирования конфига системы. \n" + \
                      "Попробуйте позднее, или обратитесь к Администратору ресурса."
    return config_line
