import postgres_init


def protect_content_check_fn(us_id: int) -> bool:
    """
    Переменная True или 1, говорит что пользователю запрещено копирование и пересылка сообщений
    Переменная False или 0, говорит что пользователю разрешено копирование и пересылка сообщений
    Если в базе нет записи, или ошибка подключения - переменная в состоянии True|1
    :param us_id:
    :return: protect_content в логическом значении
    """
    cursor, conn = postgres_init.postgres_init()
    try:
        cursor.execute(f'SELECT protect_content_chek FROM protect_content_table WHERE user_id = {us_id}')
        answer = cursor.fetchone()[0]
        if answer == 0:
            return False
        elif answer == 1:
            return True
        else:
            return True
    except (Exception,):
        return True
