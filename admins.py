import postgres_init
import protect_content

cursor, conn = postgres_init.postgres_init()


def admin_notification_message(client, text):
    """
    :param client: модуль подключения к телеграм боту
    :param text: текст сообщения для рассылки администраторов
    :return: функция принимает текст, получает из базы список администраторов,
    и через цикл делает рассылку сообщений
    """
    cursor.execute(f"SELECT * FROM initialization_user WHERE access = 'Разработчик'")
    admin_list = cursor.fetchall()

    """
    Не забывай форму ответа!
    admin_list = [[727403326, ], ]
    """

    for el_id in admin_list:
        protect_content_check = protect_content.protect_content_check_fn(el_id[0])

        client.send_message(el_id[0], text,
                            parse_mode="html",
                            protect_content=protect_content_check
                            )
