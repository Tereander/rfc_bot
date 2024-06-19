from datetime import datetime

import keyboards
import postgres_init
import integrations
import admins


def cerberus_check(client, us_id):
    """
    Модуль для проверки доступов в систему.
    Ежедневно, при первом запросе подключается к базе и проверяет пользователя на наличия доступа к базе
    :param client: соединение с серверами telegram
    :param us_id: id пользователя в telegram
    :return: Процедура
    """
    try:
        cursor, conn = postgres_init.postgres_init()

        cursor.execute('SELECT * FROM authentication_1c WHERE user_id = ' + str(us_id))
        authentication_1c_list = cursor.fetchall()[0]

        last_data = authentication_1c_list[4]
        today_data = str(datetime.now().date())
        # если даты не совпадают, делаем проверку
        if last_data != today_data:
            # проверяем логин и пароль из базы
            auth_1c_check = integrations.auth_1c_check(str(authentication_1c_list[1]), str(authentication_1c_list[2]))
            # если блок уз......
            if auth_1c_check == 'False':
                # достаем данные о пользователе
                cursor.execute(f'SELECT * FROM initialization_user WHERE user_id = {us_id}')
                initialization_user_list = cursor.fetchall()[0]
                user_name = initialization_user_list[1]
                username = initialization_user_list[2]
                department = initialization_user_list[3]
                # проводим блокировку пользователя
                postgres_init.initialization(user_id=us_id, user_name=user_name, username=username,
                                             department=department, guid='', access="Доступ запрещен")
                # уведомляем пользователя
                time = str(datetime.now().time())
                time = time[:8]
                client.send_message(us_id,
                                    f'<b>Уважаемый {user_name}!</b>\n'
                                    '\n'
                                    f'Сегодня, в <b>{time}</b>, при анализе безопасности доступа к нашему боту, '
                                    'мы не смогли подтвердить легитимность Вашей учетной записи.\n'
                                    '\n'
                                    'В целях обеспечения безопасности, /Cerberus временно заблокировал '
                                    'ваш доступ к боту и уже уведомили администраторов.\n',
                                    reply_markup=keyboards.cerberus_keyboard(),
                                    parse_mode="html")
                # уведомляем администраторов
                text_notification = '<b>Уважаемые администраторы,</b>\n' \
                                    '\n' \
                                    'Я хотел бы сообщить вам о последнем инциденте, ' \
                                    'связанном с проверкой доступа пользователей к нашему ресурсу.\n' \
                                    "\n" \
                                    f'Сегодня, в <b>{time}</b>, ' \
                                    f'при анализе безопасности доступа к нашему боту, /Cerberus не смог подтвердить ' \
                                    f'легитимность учетной записи <b>{user_name}</b>\n' \
                                    '/Cerberus заблокировал доступ данному пользователю'
                admins.admin_notification_message(client, text_notification)
                # прекращаем работу
                return
            # обновляем дату и последний чек по дате
            postgres_init.authentication_1c(authentication_1c_list[0], authentication_1c_list[1],
                                            authentication_1c_list[2], authentication_1c_list[3], today_data)
    except(Exception,):
        time = str(datetime.now().time())
        time = time[:8]
        # уведомляем администраторов
        text_notification = '<b>Уважаемые администраторы,</b>\n' \
                            '\n' \
                            'Я хотел бы сообщить вам о последнем инциденте, ' \
                            'связанном с проверкой доступа пользователей к нашему ресурсу.\n' \
                            ' \n' \
                            f'Сегодня, в <b>{time}</b>, ' \
                            f'при анализе безопасности доступа к нашему боту, /Cerberus не смог подключиться ' \
                            r'к БД и\или подтвердить легитимность учетной записи ' \
                            f'<code>{us_id}</code>\n' \
                            'Необходима ручная проверка пользователя.\n ' \
                            '<b>Доступ пользователю не заблокирован</b>'

        admins.admin_notification_message(client, text_notification)
