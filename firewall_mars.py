from urllib3 import disable_warnings, exceptions

import hashlib

# import access_list  # база данных доступов
import configs
import requests
import postgres_init
# import personal_users


def flatten_tuple_list(tuple_list):
    """
    Функция принимает вы себя список, где каждый элемент это кортеж с одним элементом.
    Функция убирает кортежи и превращает их в список
    :param tuple_list: кортеж с данными
    :return: список с данными
    """
    flattened_list = []
    for tuple_item in tuple_list:
        flattened_list.append(tuple_item[0])
    return flattened_list


def level_list_check(level_access):
    """
    Получает уровень доступа и возвращает список id с указанным уровнем для проверок
    Уровень пользователь имеют все пользователи, чем выши, тем список уменьшается.
    Важно! Использовать список только для вхождения данных для проверок
    :param level_access: уровень доступа в текстовом наименовании
    :return: список id с уникальными правами
    """
    cursor, conn = postgres_init.postgres_init()
    access_level_list = []
    if level_access == 'Разработчик':
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Разработчик'")
        access_level_1 = cursor.fetchall()
        access_level_list = list(access_level_1)

    elif level_access == 'Администратор':
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Разработчик'")
        access_level_1 = cursor.fetchall()
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Администратор'")
        access_level_2 = cursor.fetchall()
        access_level_list = list(access_level_1) + list(access_level_2)

    elif level_access == 'Пользователь ++':
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Разработчик'")
        access_level_1 = cursor.fetchall()[0]
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Администратор'")
        access_level_2 = cursor.fetchall()[0]
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Пользователь ++'")
        access_level_3 = cursor.fetchall()[0]
        access_level_list = access_level_1 + access_level_2 + access_level_3

    elif level_access == 'Пользователь +':
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Разработчик'")
        access_level_1 = cursor.fetchall()[0]
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Администратор'")
        access_level_2 = cursor.fetchall()[0]
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Пользователь ++'")
        access_level_3 = cursor.fetchall()[0]
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Пользователь +'")
        access_level_4 = cursor.fetchall()[0]
        access_level_list = access_level_1 + access_level_2 + access_level_3 + access_level_4

    elif level_access == 'Пользователь':
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Разработчик'")
        access_level_1 = cursor.fetchall()[0]
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Администратор'")
        access_level_2 = cursor.fetchall()[0]
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Пользователь ++'")
        access_level_3 = cursor.fetchall()[0]
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Пользователь +'")
        access_level_4 = cursor.fetchall()[0]
        cursor.execute(f"SELECT user_id FROM initialization_user WHERE access = 'Пользователь'")
        access_level_5 = cursor.fetchall()[0]
        access_level_list = access_level_1 + access_level_2 + access_level_3 + access_level_4 + access_level_5
    access_level_list = flatten_tuple_list(list(access_level_list))
    return access_level_list


# ФУНКЦИЯ ПОЛУЧЕНИЯ ИМЕНИ
def id_in_name(search_id):
    """
    :param search_id: id пользователя для проверки
    :return: Имя пользователя из бд
    Функция принимает id пользователя, подключается к БД и производит поиск имени.
    Если имя не найдено, функция вернет 'Имя не определенно'
    """
    try:
        cursor, conn = postgres_init.postgres_init()
        cursor.execute(f'SELECT user_name FROM initialization_user WHERE user_id = {search_id}')
        correct_name = cursor.fetchone()[0]
        return correct_name
    except (Exception,):
        return 'Имя не определенно'


# ФУНКЦИЯ ПОЛУЧЕНИЯ ИМЕНИ 2
def guid_in_name(search_guid):
    """
    Функция принимает на вход guid для поиска, производит проверку по БД,
    и возвращает полное имя пользователя
    :param search_guid: guid пользователя для проверки
    :return: Имя пользователя
    """
    try:
        cursor, conn = postgres_init.postgres_init()
        cursor.execute(f'SELECT user_name FROM initialization_user WHERE guid = {search_guid}')
        correct_name = cursor.fetchone()[0]
        return correct_name
    except (Exception,):
        return None


# ФУНКЦИЯ ПОЛУЧЕНИЯ СЕРИИ guid_1c
def guid_in_guid(guid1c: str, access: int, department: str):
    """
    :param guid1c: guid пользователя в 1с
    :param access: уровень доступа
    :param department:
    :return:
    """
    check_l_name = False
    # guid1c = str(guid1c)
    # if guid1c == "None":
    guid1c_for5 = guid1c
    guid1c = ""

    # если уровень пять получаем только свои работы
    if access == 5:
        return guid1c_for5, check_l_name

    # если уровень четыре получаем только работы своего отдела
    elif access == 4:
        cursor, conn = postgres_init.postgres_init()
        cursor.execute(f'SELECT * FROM initialization_user WHERE department = {department}')
        initialization_list = cursor.fetchall()

        for el_department in initialization_list:
            if el_department[4] != "":
                guid1c = guid1c + "," + str(el_department[4])
                check_l_name = True
        # print(guid_1c)
        if guid1c[0] == ",":
            guid1c = guid1c[1:]
        return guid1c, check_l_name

    # если уровень три и более получаем все работы
    elif access <= 3:
        cursor, conn = postgres_init.postgres_init()
        cursor.execute(f'SELECT * FROM initialization_user')
        initialization_list = cursor.fetchall()

        for el_department in initialization_list:
            if el_department[4] != "":
                guid1c = guid1c + "," + str(el_department[4])
                check_l_name = True
        # print(guid_1c)
        if guid1c[0] == ",":
            guid1c = guid1c[1:]
        return guid1c, check_l_name


# ФУНКЦИЯ ПОЛУЧЕНИЯ guid_1c
def id_in_guid(search_id):
    """
    :param search_id: id пользователя для проверки
    :return: общий (длинный) guid
    Функция принимает id пользователя, производит поиск, получает отдел и уровень доступа.
    Используя эти данные создается весь дополнительный список guid для ответа.
    """
    cursor, conn = postgres_init.postgres_init()
    try:
        # получаем список данных
        cursor.execute(f'SELECT * FROM initialization_user WHERE user_id = {search_id}')
        initialization_list = cursor.fetchall()[0]

        guid_1c = initialization_list[4]
        access = initialization_list[5]
        department = initialization_list[3]
        # превращаем текст в число
        access = configs.access_level[str(access)]

        guid_1c, check_l_name = guid_in_guid(guid_1c, access, department)
        return guid_1c, check_l_name
    except (Exception,):
        return None


def access_check(user_id):
    """
    :param user_id: id пользователя в telegram
    :returns True|False, обозначающее наличие доступа
    Основная функция проверки общего доступа к боту.
    ФФункция получает на вход id пользователя, проверяет детальный доступ пользователя к базе
    и возвращает True|False, которые обозначает разрешен ли пользователя доступ к боту
    """
    cursor, conn = postgres_init.postgres_init()
    try:
        cursor.execute(f'SELECT access FROM initialization_user WHERE user_id = {user_id}')
        access_name = cursor.fetchone()[0]
    except (Exception, ):
        access_name = 'Доступ запрещен'
    # print(access_name)
    access_level = configs.access_level[f'{access_name}']
    if access_level <= 5:
        return True
    else:
        return False


def id_in_level(user_id):
    """
    :param user_id: id пользователя в telegram
    :returns access_level, уровень доступа к пользователю.
    ФФункция получает на вход id пользователя, проверяет детальный доступ пользователя к базе
    и возвращает уровень доступа пользователя
    """
    cursor, conn = postgres_init.postgres_init()
    try:
        cursor.execute(f'SELECT access FROM initialization_user WHERE user_id = {user_id}')
        access_name = cursor.fetchone()[0]
    except (Exception, ):
        access_name = 'Доступ запрещен'

    access_level = configs.access_level[f'{access_name}']
    return access_level


def aut_1c(login, password):
    """
    :param login: логин пользователя в ИС 1С (Имя ёёёпользователя в формате: фамилия + имя)
    :param password: Пароль пользователя до преобразования в hash
    :return: boolean о наличии доступа, логин пользователя, хеш пароля
    Функция принимает на вход имя пользователя и пароль. Создает hash данных и передает на веб сервис ИС 1С
    для проверки. Проверка производится на корректность предоставленных данных и наличие/отсутствие
    блокировки уз. Если данные корректные и блокировка отсутствует, веб сервис вернет True
    """
    # print(login)
    # print(password)
    hash_object = hashlib.sha1(password.encode('utf-8'))
    hash_password = hash_object.hexdigest()
    aut_check = {"login": login,
                 "password": hash_password}
    # print(hash_password)

    endpoint = f"{configs.auth_1c['link']}/ws/RFC_UserCheck/UserCheck.1cws"

    body = '<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope' \
           f'/" xmlns:jet="{configs.auth_1c["link"]}">' \
           '<x:Header/><x:Body><jet:CheckUser><jet:InputString>' + str(aut_check) + \
           '</jet:InputString></jet:CheckUser></x:Body></x:Envelope>'
    headers = {"Content-Type": "application/json ; charset=utf-8"}
    headers.update({"Content-Length": str(len(body))})
    disable_warnings(exceptions.InsecureRequestWarning)
    answer_auth = requests.request("POST", url=endpoint, headers=headers,
                                   data=body.encode('utf-8'),
                                   auth=(configs.auth_1c['login'],
                                         configs.auth_1c['password']
                                         ),
                                   verify=False)
    answer_auth = answer_auth.text
    answer_auth = answer_auth.replace('<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">', '')
    answer_auth = answer_auth.replace('<soap:Body>', '')
    answer_auth = answer_auth.replace(f'<m:CheckUserResponse xmlns:m="{configs.auth_1c["link"]}">', '')
    answer_auth = answer_auth.replace('<m:return xmlns:xs="http://www.w3.org/2001/XMLSchema"', '')
    answer_auth = answer_auth.replace('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">', '')
    answer_auth = answer_auth.replace('</m:return>', '')
    answer_auth = answer_auth.replace('</m:CheckUserResponse>', '')
    answer_auth = answer_auth.replace('</soap:Body>', '')
    answer_auth = answer_auth.replace('</soap:Envelope>', '')
    answer_auth = answer_auth.replace('\r\n\t\t\t\t\t', '')
    answer_auth = answer_auth.replace('\r\n\t\t\t\t', '')
    answer_auth = answer_auth.replace('\r\n\t\t\t', '')
    answer_auth = answer_auth.replace('\r\n\t\t', '')
    answer_auth = answer_auth.replace('\r\n\t', '')
    answer_auth = answer_auth.replace('\r', '')
    answer_auth = answer_auth.replace('\n', '')
    answer_auth = answer_auth.replace('\t', '')
    # print(answer_auth)
    return answer_auth, login, hash_password
