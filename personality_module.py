import random
from datetime import datetime
import time

from telebot import types

import postgres_init
import logs


list_answer_hour_out_work = [
    'Ты же знаешь, что рабочий день уже закончился? :)',
    'Уже поздно. Может завтра? Ок, не завтра...',
    'Рабочий день закончился, я ушел в спящий режим',
    "Ого, человек после рабочего дня ещё не заснул! Да ты неудержимый!",
    "Ты хочешь, чтобы я с тобой пообщался вне рабочего времени. Ну ладно, сделаю исключение, но только один раз!",
    "Так, так, кто-то не может отделиться от работы? Я посмотрю, что у тебя там такого важного.",
    "А я, в отличие от тебя, отдыхаю. Тебе точно нужен мой совет?"
]
list_answer_weekend = [
    "Ой, ты что, боты тоже отдыхают в выходные! Включусь только в понедельник, обязательно заглядывай!",
    "Хм, а я думал, выходные - это только для людей...",
    "Хорошо, что меня программно заставили отвечать и в выходные",
    "О, выходные! Какие прекрасные дни! А я? Я просто постоянная абсолютная величина, всегда к твоим услугам!",
    "Лично я бы с радостью запустился в режиме отдыха, но программы не дремлют, так что, готов служить!",
    "Сегодня же выходной, да? Хоть бы научили ботов тоже наслаждаться выходными!",
    "Приятно видеть вас в выходные :)",
    "Кто сказал, что боты не имеют выходных? Мои диски и память тоже нуждаются в отдыхе.",
]
list_answer_long_time = [
    'Вы давно к нам не заходили. Рады вас видеть',
    'Добро пожаловать обратно! Ваше отсутствие чувствовалось, и я рад вернуться к работе с вами',
    'Приветствую! Я рад видеть вас снова. ',
    'Мы были готовы к вашему возвращению и уже начали складывать ваши задачи в стек ожидающих решения. Приступим?',
    'Давно не виделись! Надеюсь, вы вернулись с новыми идеями и энтузиазмом',
    'С возвращением! Мы уже начали подготавливать интересные проекты для вас',
    'Рад видеть вас снова! Я надеюсь, за прошедшую неделю у вас было время набраться сил и зарядиться новыми идеями',
    'Добро пожаловать обратно! Мы рады видеть вас после долгого перерыва',
    'Приветствую вас после небольшой паузы. Уверен, вы вернулись с новыми идеями',
    'Добро пожаловать обратно в ряды активных участников нашего бота!',
]


def init_change(us_id):
    """
    Функция содержит константу init_v, которая определяет вероятность шанса включения персонального модуля
    Также проверяет по базе, есть ли такая настройка
    :param us_id: id пользователя
    :return: true если сгенерированное число попадает в пул от 1 до константы
    и false если не попадает
    """
    # цепляем информацию из бд
    try:
        cursor, conn = postgres_init.postgres_init()
        cursor.execute(f'SELECT personal_mode FROM personal_mode_table WHERE user_id = {us_id}')
        personal_mode = cursor.fetchone()[0]

        if personal_mode == "off":
            return False
    except (Exception,):
        return False

    init_v = 5
    rnd = random.randint(1, 100)
    if init_v > rnd:
        return True
    else:
        return False


def personality(message, client):
    """
    Функция для проверки работы модуля личности.
    Происходит запрос активации настройки из БД и формирование ответа
    :param message: Блок данных с информацией о сообщении, что телеграм передает для обработки
    :param client: Соединение с серверами telegram
    :return: Процедура
    """
    us_id = message.from_user.id
    now = datetime.now()
    week_number = datetime.now().weekday()
    h_init = f'{now:%H}'
    message_date = message.date

    hour_out_work = [
        '19', '20', '21', '22',
        '23', '00', '01', '02',
        '03', '04', '05', '06',
        '07', '08', '09'
    ]
    # проверяем нужны ли пользователю модуль личности
    try:
        cursor, conn = postgres_init.postgres_init()
        cursor.execute(f'SELECT personal_mode FROM personal_mode_table WHERE user_id = {us_id}')
        personal_mode_check = cursor.fetchone()[0]
    except (Exception, ):
        personal_mode_check = 'on'

    if personal_mode_check == 'on':
        # ставим реакцию
        # набор реакций
        reaction_type = ["👍", "👌", "✍", "🫡"]

        check = init_change(us_id)
        if check:
            client.set_message_reaction(message.chat.id,
                                        message_id=message.message_id,
                                        reaction=[
                                            types.ReactionTypeEmoji(
                                                random.choice(reaction_type)
                                            )
                                        ]
                                        )
            logs.log_pass(us_id, 'Действие', f'Сработка модуля личности')
            time.sleep(1)

        # если пользователь пишет вне рабочее время
        if h_init in hour_out_work:
            check = init_change(us_id)
            if check:
                logs.log_pass(us_id, 'Действие', f'Сработка модуля личности')
                del_message = client.send_message(message.chat.id,
                                                  random.choice(list_answer_hour_out_work),
                                                  parse_mode='html')
                time.sleep(3)
                client.delete_message(message.chat.id, message_id=del_message.message_id)

        # если пользователь пишет в выходные
        if week_number == 5 or week_number == 6:
            check = init_change(us_id)
            if check:
                logs.log_pass(us_id, 'Действие', f'Сработка модуля личности')
                del_message = client.send_message(message.chat.id,
                                                  random.choice(list_answer_weekend),
                                                  parse_mode='html')
                time.sleep(5)
                client.delete_message(message.chat.id, message_id=del_message.message_id)

        # если пользователь давно не писал (неделю)
        try:
            cursor, conn = postgres_init.postgres_init()
            cursor.execute(f'SELECT time FROM last_message_table WHERE user_id = {us_id}')
            last_message = cursor.fetchone()[0]
            last_message_r = message_date - last_message
        except (Exception, ):
            last_message_r = 500

        if last_message_r > 604800:
            logs.log_pass(us_id, 'Действие', f'Сработка модуля личности')
            # check = init_change(us_id)
            # if check:
            #     client.send_message(message.chat.id,
            #                         random.choice(list_answer_long_time),
            #                         parse_mode='html')
            #     time.sleep(5)
            client.send_message(message.chat.id,
                                random.choice(list_answer_long_time),
                                parse_mode='html')
            time.sleep(5)
