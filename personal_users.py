import postgres_init


# Получаем полное имя пользователя
def user_name(id_for_cr_name, message):
    try:
        cursor, conn = postgres_init.postgres_init()
        cursor.execute(f'SELECT user_name FROM initialization_user WHERE user_id = {id_for_cr_name}')
        correct_name = cursor.fetchone()[0]
        return correct_name
    except (Exception,):
        correct_name = message.from_user.full_name
        return correct_name


# Проверяем на наличие nickname и делаем из него внутр ссылку
def user_nickname(username):
    if username is not None:
        username = '@' + username
    else:
        username = 'Отсутствует'
    return username


def search_user_data(input_search: str):
    """
    :param input_search: Данные для поиска, имя или id
    :return: json файл с данными
    Функция принимает на вход текстовую строку, проверяет ее в поле имя или id.
    Проводим поиск и выдаем данные пользователю
    """
    cursor, conn = postgres_init.postgres_init()
    cursor.execute(
        f'SELECT * FROM initialization_user WHERE user_id = {input_search} or {input_search} in user_name'
    )
    correct_name = cursor.fetchone()[0]
    # print(correct_name)
    return
