import random
import datetime
import requests
from datetime import datetime

import configs

################################################################################
# ОЦЕНКА ВЕРОЯТНОСТИ ЗАПРОС НАУМЕН
################################################################################


def detail_naumen_search(status_naumen_first: str) -> int:
    """
    Функция принимает статус naumen и конвертирует его в число оценки.
    :param status_naumen_first: Статус работ в ИС naumen
    :return: число с вероятностью проведения работ
    """
    answer_ch = None
    if str(status_naumen_first) == "registered":
        answer_ch = random.randint(50, 53)
    elif str(status_naumen_first) == "resolved":
        answer_ch = 2
    elif str(status_naumen_first) == "closed":
        answer_ch = 2
    elif str(status_naumen_first) == "checking":
        answer_ch = random.randint(50, 53)
    elif str(status_naumen_first) == "waiting":
        answer_ch = random.randint(50, 53)
    elif str(status_naumen_first) == "test":
        answer_ch = random.randint(50, 53)
    elif str(status_naumen_first) == "purpose":
        answer_ch = random.randint(60, 65)
    elif str(status_naumen_first) == "intCAB":
        answer_ch = random.randint(50, 53)
    elif str(status_naumen_first) == "implementation":
        answer_ch = random.randint(96, 99)
    elif str(status_naumen_first) == "analysis":
        answer_ch = random.randint(50, 55)
    elif str(status_naumen_first) == "negotiating":
        answer_ch = random.randint(70, 80)
    elif str(status_naumen_first) == "opinion":
        answer_ch = random.randint(60, 70)
    elif str(status_naumen_first) == "plan":
        answer_ch = random.randint(70, 75)
    return answer_ch


def naumen_search(uuid_naumen):
    if str(uuid_naumen) == "Отсутствует" or str(uuid_naumen) == "None" or str(uuid_naumen) == "":
        answer_ch = random.randint(50, 65)
        return answer_ch

    url = f"{configs.naumen['link']}/sd/services/rest/get/"+str(uuid_naumen) +\
          "?accessKey="+str(configs.naumen['accessKey'])
    payload = {}
    headers = {'Cookie': configs.naumen['cookie'],
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
               }
    response_naumen = requests.request("GET", url=url, headers=headers,
                                       data=payload)
    naumen_load7 = response_naumen.json()

    status_naumen_first = naumen_load7["state"]
    answer_ch = detail_naumen_search(status_naumen_first)
    return answer_ch
################################################################################
# ОЦЕНКА ВЕРОЯТНОСТИ
################################################################################


def time_revers(result_data, probability_rfc):
    """
    Функция принимает дату выполнения работ и процент вероятности и калибруем данное значение.
    Если дата проведения работ на будущее время, система понижает шанс, если на прошлую дату - понижает
    :param result_data: дата проведения работ
    :param probability_rfc: Вероятность реализации RFC
    :return: число измененное коэффициентом
    """
    try:
        now_date = datetime.now()
        result_data = datetime.strptime(result_data, "%H:%M %d.%m.%Y")
        data_difference = result_data - now_date
        data_difference_short = data_difference.days
        if data_difference_short <= -2:
            probability_rfc_revers = 1
        elif data_difference_short == -1:
            probability_rfc_revers = round(probability_rfc * 0.2)
        elif data_difference_short == 0:
            probability_rfc_revers = round(probability_rfc * 1)
        elif data_difference_short == 1:
            probability_rfc_revers = round(probability_rfc * 1.1)
        elif data_difference_short == 2:
            probability_rfc_revers = round(probability_rfc * 1.2)
        elif data_difference_short >= 3:
            probability_rfc_revers = round(probability_rfc * 1.3)

        return probability_rfc_revers
    except (Exception, ):
        return probability_rfc


# функция оценки
def estimate(state_rfc, result_data, uuid_naumen):
    probability_rfc = 0
    if state_rfc == "Оформление":
        probability_rfc = random.randint(5, 10)
        probability_rfc_revers = time_revers(result_data, probability_rfc)
    elif state_rfc == "Разработка":
        probability_rfc = random.randint(10, 20)
        probability_rfc_revers = time_revers(result_data, probability_rfc)
    elif state_rfc == "Создание":
        probability_rfc = random.randint(1, 5)
        probability_rfc_revers = time_revers(result_data, probability_rfc)
    elif state_rfc == "Технологическое согласование":
        probability_rfc = random.randint(20, 35)
        probability_rfc_revers = time_revers(result_data, probability_rfc)
    elif state_rfc == "Планирование":
        probability_rfc = random.randint(40, 45)
        probability_rfc_revers = time_revers(result_data, probability_rfc)
    elif state_rfc == "Доработка":
        probability_rfc = random.randint(2, 5)
        probability_rfc_revers = time_revers(result_data, probability_rfc)
    elif state_rfc == "На паузе":
        probability_rfc = random.randint(5, 10)
    elif state_rfc == "Финальное согласование":
        probability_rfc = naumen_search(uuid_naumen)
        probability_rfc_revers = time_revers(result_data, probability_rfc)
    # если на ноль
    if probability_rfc <= 0:
        probability_rfc_revers = 1
    return probability_rfc_revers


# список паттернов
pattern_1 = r'\d{4}\\202\d|\d{4}-202\d|\d{4}_202\d|\d{4}\|202\d'
pattern_2 = r'\d{8}|\d{4}|\d{3}'
pattern_3 = r'\d{4}/202\d|srfc\d{3}|task\d{8}'
pattern_4 = r'\d{4}/02\d|\d{3}/202\d|\d\d/202\d|\d/202\d'
pattern_5_callback = r'\d\d\d\d/202\d|task\d\d\d\d\d\d\d\d|SRFC\d\d\d'
pattern_5_var1 = r'\d{5}|ЗНИ\d{5}|зни\d{5}|ЗНИ \d{5}|ЗНИ: \d{5}|зни: \d{5}'
pattern_5_var2 = r'\d{4}\\202\d|\d{4}-202\d|\d{4}_202\d|\d{4}\|202\d|\d{4}/202\d'


# answer = estimate("Планирование", "20:59 03.06.2024", 0)
# print(answer)
