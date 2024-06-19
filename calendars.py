import requests
import json
import datetime
from datetime import datetime, timedelta
from collections import Counter
################################################################################
import re
from urllib3 import disable_warnings, exceptions
# import psycopg2
# from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
################################################################################
import configs
import firewall_mars
import neuron


def calendar_rfc(guid_1c):
    uuid_1c = guid_1c

    # код поиска и вывода - Создаем клиент
    endpoint = f"{configs.auth_1c['link']}/ws/RFC_Calendar/ws1.1cws"
    body = ('<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope'
            f'/" xmlns:jet="{configs.auth_1c["link"]}">'
            '<x:Header/><x:Body><jet:Calendar><jet:UUID>' + str(uuid_1c) +
            '</jet:UUID></jet:Calendar></x:Body></x:Envelope>')

    headers = {"Content-Type": "application/json ; charset=utf-8"}
    headers.update({"Content-Length": str(len(body))})
    disable_warnings(exceptions.InsecureRequestWarning)

    response = requests.request("POST", url=endpoint, headers=headers,
                                data=body,
                                auth=(configs.auth_1c['login'],
                                      configs.auth_1c['password']),
                                verify=False
                                )
    answer = response.text
    answer = re.sub(r'<[^>]*>', '', answer)
    answer = re.sub(r'\r', '', answer)
    answer = re.sub(r'\n', '', answer)
    answer = re.sub(r'\t', '', answer)
    # answer = re.sub(r'\"', '', answer)
    answer = re.sub(r'\[', '', answer)
    answer = re.sub(r']', '', answer)
    answer = answer.split("}")
    return answer


# ##########СОРТИРУЕМ ПО ДАТЕ####################################################
def answer_calendar_rfc(result_data, calendar_build, check_l_name, grade_el_table_zn, calendar_view):
    result_data = datetime.strptime(str(result_data), '%Y-%m-%d')
    result_data = result_data.strftime("%d.%m.%Y")
    answer_list = []
    for a in calendar_build:
        if a != "":
            a = str(a) + "}"
            a = json.loads(a)

            if str(a["start_date"]) == str(result_data):
                answer_list.append(a)

    # ##########МЕНЯЕМ ГУИД НА ИМЯ###############################################

    for irf in answer_list:
        irf["uuid"] = firewall_mars.guid_in_name(irf["uuid"])
    # ##########МЕНЯЕМ ГУИД НА ИМЯ###############################################
    # делаем список рфс только с номерами
    number_answer_list = []
    for tre in answer_list:
        number_answer_list.append(tre["numberRFC"])
    # получаем словарь с указанием повторяющихся номеров
    a_dict = Counter(number_answer_list)
    for key in a_dict:
        if a_dict[key] > 1:

            # если два и более одинаковых рфс, но с разными исполнителями
            asd = []
            for g in answer_list:
                if key == g["numberRFC"]:
                    if g["uuid"] is not None:
                        asd.append(g["uuid"])
            many_name = " + ".join(asd)
            # меняем все uuid на одинаковое
            for h in answer_list:
                if h["numberRFC"] == key:
                    h["uuid"] = many_name
    temp = []
    for answer_list_el in answer_list:
        if answer_list_el not in temp:
            temp.append(answer_list_el)
    answer_list = temp

    # ФОРМИРУЕМ ОТВЕТ
    if answer_list is []:
        answer = "На текущую дату ("+str(result_data)+") работы отсутствуют"
        repeat_calendar = False
    else:
        repeat_calendar = True
        answer = "Список RFC на <b>" + str(result_data)+"</b>: \n \n"
        for_del = []
        for answer_list_el in answer_list:
            if grade_el_table_zn == "True":
                ch_proc = neuron.estimate(answer_list_el["status"], result_data, answer_list_el["uuid_bank"])
                ch_proc = " ● <b>(~ "+str(ch_proc)+"%)</b>"
            else:
                ch_proc = ""

            if check_l_name is True:
                if answer_list_el["uuid"] is None:
                    name = ""
                else:
                    name = "<b>(" + str(answer_list_el["uuid"]) + ")</b>"

            else:
                name = ""

            # думаем над тем какие работы отображать
            checks = [
                      answer_list_el["status"] == "Создание",
                      answer_list_el["status"] == "Не согласовано",
                      answer_list_el["status"] == "Отменено",
                      answer_list_el["status"] == "Выполнено успешно",
                      answer_list_el["status"] == "Завершены откатом",
                      answer_list_el["status"] == "Закрыто",
                      ]
            if calendar_view == "Not Full":
                checks = [
                          answer_list_el["status"] == "Создание",
                          answer_list_el["status"] == "Не согласовано",
                          answer_list_el["status"] == "Отменено",
                          answer_list_el["status"] == "Выполнено успешно",
                          answer_list_el["status"] == "Завершены откатом",
                          answer_list_el["status"] == "Закрыто",
                          answer_list_el["status"] == "Разработка",
                          answer_list_el["status"] == "Технологическое согласование",
                          answer_list_el["status"] == "Оформление",
                          answer_list_el["status"] == "Доработка",
                          answer_list_el["status"] == "Планирование",
                          answer_list_el["status"] == "На паузе",
                          ]

            # заканчиваем думать
            if any(checks):
                for_del.append(answer_list_el)
            else:
                answer = answer + "<b>" + str(answer_list_el["start_time"]) +\
                         "</b> ● " + str(answer_list_el["numberRFC"]) +\
                         " - " + str(answer_list_el["nameRFC"]) +\
                         " " + name + ch_proc + "\n \n"

        for i in for_del:
            answer_list.remove(i)
    return answer, repeat_calendar, answer_list


# ###########################Получаем календарь списком##########################
def list_week(calendar_build, grade_el_table_zn, calendar_view):
    data_list = []
    today = datetime.now()
    new_today = str(today)
    new_today = new_today[:10]
    new_today = datetime.strptime(new_today, '%Y-%m-%d')
    new_today = new_today.strftime("%d.%m.%Y")
    data_list.append(new_today)

    day1 = today + timedelta(days=1)
    day1 = str(day1)
    day1 = day1[:10]
    day1 = datetime.strptime(str(day1), '%Y-%m-%d')
    day1 = day1.strftime("%d.%m.%Y")
    data_list.append(day1)
    day2 = today + timedelta(days=2)
    day2 = str(day2)
    day2 = day2[:10]
    day2 = datetime.strptime(str(day2), '%Y-%m-%d')
    day2 = day2.strftime("%d.%m.%Y")
    data_list.append(day2)
    day3 = today + timedelta(days=3)
    day3 = str(day3)
    day3 = day3[:10]
    day3 = datetime.strptime(str(day3), '%Y-%m-%d')
    day3 = day3.strftime("%d.%m.%Y")
    data_list.append(day3)
    day4 = today + timedelta(days=4)
    day4 = str(day4)
    day4 = day4[:10]
    day4 = datetime.strptime(str(day4), '%Y-%m-%d')
    day4 = day4.strftime("%d.%m.%Y")
    data_list.append(day4)
    day5 = today + timedelta(days=5)
    day5 = str(day5)
    day5 = day5[:10]
    day5 = datetime.strptime(str(day5), '%Y-%m-%d')
    day5 = day5.strftime("%d.%m.%Y")
    data_list.append(day5)
    day6 = today + timedelta(days=6)
    day6 = str(day6)
    day6 = day6[:10]
    day6 = datetime.strptime(str(day6), '%Y-%m-%d')
    day6 = day6.strftime("%d.%m.%Y")
    data_list.append(day6)
    day7 = today + timedelta(days=7)
    day7 = str(day7)
    day7 = day7[:10]
    day7 = datetime.strptime(str(day7), '%Y-%m-%d')
    day7 = day7.strftime("%d.%m.%Y")
    data_list.append(day7)
    day8 = today + timedelta(days=8)
    day8 = str(day8)
    day8 = day8[:10]
    day8 = datetime.strptime(str(day8), '%Y-%m-%d')
    day8 = day8.strftime("%d.%m.%Y")
    data_list.append(day8)
    day9 = today + timedelta(days=9)
    day9 = str(day9)
    day9 = day9[:10]
    day9 = datetime.strptime(str(day9), '%Y-%m-%d')
    day9 = day9.strftime("%d.%m.%Y")
    data_list.append(day9)
    day10 = today + timedelta(days=10)
    day10 = str(day10)
    day10 = day10[:10]
    day10 = datetime.strptime(str(day10), '%Y-%m-%d')
    day10 = day10.strftime("%d.%m.%Y")
    data_list.append(day10)
    day11 = today + timedelta(days=11)
    day11 = str(day11)
    day11 = day11[:10]
    day11 = datetime.strptime(str(day11), '%Y-%m-%d')
    day11 = day11.strftime("%d.%m.%Y")
    data_list.append(day11)
    day12 = today + timedelta(days=12)
    day12 = str(day12)
    day12 = day12[:10]
    day12 = datetime.strptime(str(day12), '%Y-%m-%d')
    day12 = day12.strftime("%d.%m.%Y")
    data_list.append(day12)
    day13 = today + timedelta(days=13)
    day13 = str(day13)
    day13 = day13[:10]
    day13 = datetime.strptime(str(day13), '%Y-%m-%d')
    day13 = day13.strftime("%d.%m.%Y")
    data_list.append(day13)
    day14 = today + timedelta(days=14)
    day14 = str(day14)
    day14 = day14[:10]
    day14 = datetime.strptime(str(day14), '%Y-%m-%d')
    day14 = day14.strftime("%d.%m.%Y")
    data_list.append(day14)

    today = str(today)
    today = today[:10]
    today = datetime.strptime(str(today), '%Y-%m-%d')
    today = today.strftime("%d.%m.%Y")

    answer_list = []
    for a in calendar_build:
        if a != "":
            a = str(a) + "}"
            a = json.loads(a)
            for yu in data_list:
                if str(a["start_date"]) == str(yu):
                    answer_list.append(a)
    #################################################
    work_not_check = False
    if not answer_list:
        answer = "<i>Добрый день, уважаемый пользователь! \n" +\
                 "К сожалению, в текущий период для Вас работы отсутствуют. \n" +\
                 "RFC менеджеры прикладывают все усилия для исправления этой ситуации.</i>"
        work_not_check = True
    else:
        answer = "Список RFC c <b>"+str(today)+" по "+str(day14)+"</b>: \n \n"
        for_del = []
        for answer_list_el in answer_list:
            if grade_el_table_zn == "True":
                ch_proc = neuron.estimate(answer_list_el["status"], today, answer_list_el["uuid_bank"])
                ch_proc = " ● <b>(~ "+str(ch_proc)+"%)</b>"
            else:
                ch_proc = ""
            # думаем над тем какие работы отображать
            checks = [
                      answer_list_el["status"] == "Создание",
                      answer_list_el["status"] == "Не согласовано",
                      answer_list_el["status"] == "Отменено",
                      answer_list_el["status"] == "Выполнено успешно",
                      answer_list_el["status"] == "Завершены откатом",
                      answer_list_el["status"] == "Закрыто",
                      ]
            if calendar_view == "Not Full":
                checks = [
                          answer_list_el["status"] == "Создание",
                          answer_list_el["status"] == "Не согласовано",
                          answer_list_el["status"] == "Отменено",
                          answer_list_el["status"] == "Выполнено успешно",
                          answer_list_el["status"] == "Завершены откатом",
                          answer_list_el["status"] == "Закрыто",
                          answer_list_el["status"] == "Разработка",
                          answer_list_el["status"] == "Технологическое согласование",
                          answer_list_el["status"] == "Оформление",
                          answer_list_el["status"] == "Доработка",
                          answer_list_el["status"] == "Планирование",
                          answer_list_el["status"] == "На паузе",
                          ]

            # заканчиваем думать

            if any(checks):
                for_del.append(answer_list_el)
            else:
                answer = answer + str(answer_list_el["start_date"]) + " с " +\
                         "<b>" + str(answer_list_el["start_time"]) +\
                         "</b> ● " + str(answer_list_el["numberRFC"]) +\
                         " - " + str(answer_list_el["nameRFC"]) +\
                         str(ch_proc) + "\n \n"
        for i in for_del:
            answer_list.remove(i)
    return answer, answer_list, work_not_check
