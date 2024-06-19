import time

import postgres_init
import firewall_mars
import logs


def mailing_message(client, message, protect_content_check):

    mailing_text = message.text

    signature = f'\n ' \
                f' \n ' \
                f'Вы можете отключить рассылки в /settings'

    mailing_text = mailing_text + signature  # финальный текст для отправки

    us_id = message.from_user.id
    us_name = message.from_user.first_name
    user_surname = message.from_user.last_name
    username = message.from_user.username

    postgres_init.rfc_number(user_id=us_id, user_name=us_name, user_surname=user_surname,
                             username=username, search_rfc=0, last_rfc_number="XXXX/202X")

    if '/cancellation' in mailing_text:
        client.send_message(message.chat.id, 'Рассылка отменена')
        return

    cursor, conn = postgres_init.postgres_init()

    full_name = firewall_mars.id_in_name(us_id)
    report = "Отчет о направленной рассылке " + \
             "от пользователя <b>" + str(full_name) + "</b>: \n \n"
    y = 0
    y_gr = 0
    y_rd = 0
    y_el = 0

    # получаем список id для работы
    access_list_r = []

    cursor.execute("SELECT * FROM initialization_user WHERE access = 'Разработчик'")
    access = cursor.fetchall()
    access_list_r += access

    cursor.execute("SELECT * FROM initialization_user WHERE access = 'Администратор'")
    access = cursor.fetchall()
    access_list_r += access

    cursor.execute("SELECT * FROM initialization_user WHERE access = 'Пользователь ++'")
    access = cursor.fetchall()
    access_list_r += access

    cursor.execute("SELECT * FROM initialization_user WHERE access = 'Пользователь +'")
    access = cursor.fetchall()
    access_list_r += access

    cursor.execute("SELECT * FROM initialization_user WHERE access = 'Пользователь'")
    access = cursor.fetchall()
    access_list_r += access

    for j in access_list_r:
        us_id = int(j[0])
        name = str(j[1])
        # пытаемся вытащить переменную проверку блока
        try:
            cursor.execute(f'SELECT add_block FROM add_block_table WHERE user_id = {us_id}')
            add_block = cursor.fetchone()[0]
        except (Exception,):
            add_block = "False"
        # пытаемся отправить
        try:
            if add_block == "True":
                y = y + 1
                y_el = y_el + 1
                tr = str(y) + ") 🟡 - " + str(name) + "\n"
                report = report + tr
                pass
            else:
                client.send_message(int(us_id),
                                    mailing_text,
                                    parse_mode="html", protect_content=protect_content_check)
                time.sleep(0.3)
                y = y + 1
                y_gr = y_gr + 1
                tr = str(y) + ") 🟢 - " + str(name) + "\n"
                report = report + tr
                pass
        except (Exception,):
            y = y + 1
            y_rd = y_rd + 1
            tr = str(y) + ") 🔴 - " + str(name) + "\n"
            report = report + tr
            pass

    report += " \n" + \
              "Рассылку получило: " + str(y_gr) + " человек\n" + \
              "Ошибка: " + str(y_rd) + " человек \n" + \
              "Заблокировали: " + str(y_el) + " человек\n"

    for admin_prime_id in firewall_mars.level_list_check('Разработчик'):
        if len(report) > 4096:
            for x in range(0, len(report), 4096):
                client.send_chat_action(admin_prime_id, action="typing")
                client.send_message(admin_prime_id,
                                    str(report[x:x + 4096]),
                                    parse_mode="html", protect_content=protect_content_check)
        else:
            client.send_chat_action(admin_prime_id, action="typing")
            client.send_message(admin_prime_id, str(report),
                                parse_mode="html", protect_content=protect_content_check)

    # full_user_name = firewall_mars.id_in_name(us_id)
    logs.log_pass(us_id, 'Действие', f'Рассылка направлена')
    return
