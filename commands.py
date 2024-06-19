def command_list(access_f_command):
    check_status_command_list_replace = False
    cm03 = "/command03 - Предоставлении доступа пользователю\n"
    cm04 = "/command04 - Тестовая функция\n"
    cm05 = "/command05 - Получение журнала логов\n"
    cm06 = "/command06 - Запуск бота\n"
    cm07 = "/command07 - Перезапуск бота\n"
    cm08 = "/command08 - Просмотр главного меню\n"
    cm09 = "/command09 - Просмотр меню настроек\n"
    cm10 = "/command10 - Просмотр меню информации\n"
    cm11 = "/command11 - Вызов меню подсказок\n"
    cm12 = "/command12 - Поиск RFC\n"
    cm13 = "/command13 - Активация 'Режима разработчика'\n"
    cm14 = "/command14 - Деактивация 'Режима разработчика'\n"
    cm16 = "/command16 - Анализ 'Журнала логов'\n"
    cm18 = "/command18 - Получение календаря работ\n"
    cm19 = "/command19 - Отправка рассылки\n"
    cm20 = "/command20 - Получение списка работ на 14 дней\n"
    cm23 = "/command23 - Roadmap\n"
    cm26 = "/command26 - Применение конфиг настроек\n"
    cm27 = "/command27 - Получение данных по id\n"
    if access_f_command == "Администратор":
        check_status_command_list_replace = True
        cm03 = cm04 = cm13 = cm14 = cm19 = cm20 = cm27 = ""
    elif access_f_command == "Пользователь" or access_f_command == "Пользователь +" or \
            access_f_command == "Пользователь ++":
        check_status_command_list_replace = True
        cm03 = cm04 = cm05 = cm13 = cm14 = cm16 = cm19 = cm27 = ""

    command_list_nb = (cm03 + cm04 + cm05 + cm06 + cm07 +
                       cm08 + cm09 + cm10 + cm11 + cm12 +
                       cm13 + cm14 + cm16 + cm18 + cm19 +
                       cm20 + cm23 + cm26 + cm27
                       )
    return command_list_nb, check_status_command_list_replace
