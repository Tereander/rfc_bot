import postgres_init
import protect_content
import personal_users
import logs
import admins
import keyboards


def time_block_check(us_id, time_block):
    """
    Функция проверяет время последней блокировки и запрашивает
    предпоследний инцидент для определения подозрения на ddos
    :param us_id: id пользователя в telegram
    :param time_block: время последней блокировки
    :return: true - подозрение на ddos, false - обоснование не найдено
    """
    cursor, conn = postgres_init.postgres_init()
    try:
        """
        пытаемся получить последнее время блок сообщения
        """
        cursor.execute(f'SELECT time_block FROM message_block_table WHERE user_id = {us_id}')
        time_block_old = cursor.fetchone()[0]
        """
        Высчитываем разницу между текущим запросом, и последней записи в базе.
        Делим результат на 60, чтобы получить секунды
        """
        time_check = int(time_block) - int(time_block_old)
        # time_check = time_check / 60
        # если разница больше 30 секунд, пропускаем, иначе не пропускаем
        if time_check > 5:
            # обновляем запись
            postgres_init.time_message_block_fn(us_id, time_block)
            return False
        else:
            # обновляем запись
            postgres_init.time_message_block_fn(us_id, time_block)
            logs.log_pass(us_id, 'DDOS', f'Подозрение на DDOS атаку')
            return True
    except (Exception,):
        # в случае ошибки тоже пропускаем
        postgres_init.time_message_block_fn(us_id, time_block)
        return False


def access_blocked(message, us_id, user_full_name, username, client):
    """
    Функция, которая отвечает за блокировку пользователя и заданный алгоритм действий при этом.
    Бот уведомляет пользователя и администраторов, указывая необходимую информацию
    :param message: модуль сообщение для работы с данными телеги
    :param us_id: id пользователя
    :param user_full_name: полное имя пользователя
    :param username: никнейм пользователя
    :param client: соединение с telegram
    :return: Процедура
    """
    protect_content_check = protect_content.protect_content_check_fn(us_id)
    # получаем время блокировки сообщения
    time_block = message.date
    message_block_check = time_block_check(us_id, time_block)
    # если блока уведомлений нет, уведомляем всех
    if not message_block_check:
        # добавляем собаку, или пишем что он отсутствует
        username = personal_users.user_nickname(username)

        client.send_chat_action(message.chat.id, action="typing")
        client.send_message(message.chat.id,
                            "⚠️ Доступ к чат-боту RFC заблокирован!\n"
                            f"📑 ID пользователя: <code><b>{us_id}</b></code> \n"
                            "📲 Обратитесь к системному администратору ресурса "
                            "или попробуйте осуществить самостоятельную регистрацию через УЗ ИС 1С",
                            parse_mode="html",
                            protect_content=protect_content_check,
                            reply_markup=keyboards.web_auth_1c_keyboard())

        text_notification_user_block = f"⚠️<b>Обнаружена попытка входа!</b>\n" \
                                       f" \n" \
                                       f"Имя: <b>{user_full_name}</b> \n" \
                                       f"Никнейм: <b>{username}</b> \n" \
                                       f"ID пользователя: <b>{us_id}</b> \n" \
                                       f" \n" \
                                       f"💾 Последнее сообщение пользователя до блокировки: " \
                                       f"<i><b>{message.text}</b></i>\n" \
                                       f" \n" \
                                       f"❌ На данный момент, доступ этому пользователю заблокирован."

        admins.admin_notification_message(client, text_notification_user_block)
    else:
        client.send_chat_action(message.chat.id, action="typing")
        client.send_message(message.chat.id,
                            '⚠️ Фиксирую попытку DDOS атаки. Повторите попытку через 30 секунд\n'
                            'Администраторы системы уведомлены\n',
                            parse_mode="html", protect_content=protect_content_check)
        text_notification_user_ddos = f"⚠️<b>Обнаружена попытка DDOS атаки!</b>\n" \
                                      f" \n" \
                                      f"Имя: <b>{user_full_name}</b> \n" \
                                      f"Никнейм: <b>{username}</b> \n" \
                                      f"ID пользователя: <b>{us_id}</b> \n"
        admins.admin_notification_message(client, text_notification_user_ddos)

    logs.log_pass(us_id, 'Блокировка', f'доступ заблокирован')
    return
