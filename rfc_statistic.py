import requests
import json

from urllib3 import disable_warnings, exceptions

import configs


# код поиска и вывода - Создаем клиент
def simple_rfc_statistic() -> str:
    """
    Функция подключается к базе 1С и собирает список работ во всех статусах
    :return: Текстовое сообщение с информацией о статусах rfc
    """

    # ОБЪЯВЛЯЕМ ПЕРЕМЕННЫЕ СТАТУСОВ
    status01 = "⚪️ Закрыто:"+" <b>0</b> RFC\n"
    status02 = "⚪️ Завершены откатом:"+"<b> 0</b> RFC\n"
    status03 = "⚪️ Выполнено успешно:"+"<b> 0</b> RFC\n"
    status04 = "⚪️ Отменено:"+"<b> 0</b> RFC\n"
    status05 = "⚪️ На паузе:"+"<b> 0</b> RFC\n"
    status06 = "⚪️ Не согласовано:"+"<b> 0</b> RFC\n"
    status07 = "🟢 Планирование:"+"<b> 0</b> RFC\n"
    status08 = "🟢 Доработка:"+"<b> 0</b> RFC\n"
    status09 = "🟡 Технологическое согласование:"+"<b> 0</b> RFC\n"
    status10 = "🟢 Оформление:"+"<b> 0</b> RFC\n"
    status11 = "🟡 Разработка:"+"<b> 0</b> RFC\n"
    status12 = "🟡 Финальное Согласование:"+"<b> 0</b> RFC\n"

    endpoint = f"{configs.auth_1c['link']}/ws/RFC_StatusStatistics"

    body = '<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope' +\
           f'/" xmlns:jet="{configs.auth_1c["link"]}">' +\
           '<x:Header/><x:Body><jet:GetStatistics><jet:Status>' +\
           '</jet:Status></jet:GetStatistics></x:Body></x:Envelope>'

    headers = {"Content-Type": "application/json; charset=utf-8"}
    headers.update(
        {
            "Content-Length": str(
                len(body)
            )
        }
    )
    disable_warnings(exceptions.InsecureRequestWarning)
    response = requests.request("POST", url=endpoint, headers=headers,
                                data=body,
                                auth=(configs.auth_1c['login'],
                                      configs.auth_1c['password']
                                      ),
                                verify=False)
    # global rfc_info
    rfc_info6 = response.text
    # print(response.json)
    rfc_info6 = rfc_info6.replace('<soap:Envelope xmlns:soap'
                                  '="http://schemas.xmlsoap.'
                                  'org/soap/envelope/">', '')
    rfc_info6 = rfc_info6.replace('<soap:Body>', '')
    rfc_info6 = rfc_info6.replace(f'<m:GetStatisticsResponse xmlns:m="{configs.auth_1c["link"]}">', '')
    rfc_info6 = rfc_info6.replace('<m:return xmlns:xs="http://www.w3.org'
                                  '/2001/XMLSchema"', '')
    rfc_info6 = rfc_info6.replace('xmlns:xsi="http://www.w3.org/2001/'
                                  'XMLSchema-instance">', '')
    rfc_info6 = rfc_info6.replace('</m:return>', '')
    rfc_info6 = rfc_info6.replace('</m:GetStatisticsResponse>', '')
    rfc_info6 = rfc_info6.replace('</soap:Body>', '')
    rfc_info6 = rfc_info6.replace('</soap:Envelope>', '')
    rfc_info6 = rfc_info6.replace('\r\n\t\t\t\t\t', '')
    rfc_info6 = rfc_info6.replace('\r\n\t\t\t\t', '')
    rfc_info6 = rfc_info6.replace('\r\n\t\t\t', '')
    rfc_info6 = rfc_info6.replace('\r\n\t\t', '')
    rfc_info6 = rfc_info6.replace('\r\n\t', '')
    # print(rfc_info6)
    rfc_split = rfc_info6.split("}")

    answer_rfc_statistic = "<b>Список RFC с разделением по статусам:</b>\n \n"
    # print(rfc_split)
    # print("")
    # print("")
    qty_all_status = 0
    not_successfully_completed = 0
    successfully_completed = 0

    qty_status12 = qty_status11 = qty_status10 = qty_status09 = 0
    qty_status08 = qty_status07 = qty_status06 = qty_status05 = 0
    qty_status04 = qty_status03 = qty_status02 = qty_status01 = 0

    for i in rfc_split:
        # print(i)
        try:
            i = i + "}"
            rfc_info8 = json.loads(i)
            # print(rfc_info8)
        except (Exception,):
            rfc_info8 = ""

        ########################################################################
        if "Закрыто" in rfc_info8:
            work_list = rfc_info8["Закрыто"]
            work_list = str(work_list).split(",")
            status01 = "⚪️ Закрыто: <b>" + str(len(work_list))+"</b> RFC\n"
            qty_status01 = int(len(work_list))
            qty_all_status += len(work_list)
        ########################################################################
        if "ЗавершеныОткатом" in rfc_info8:
            work_list = rfc_info8["ЗавершеныОткатом"]
            work_list = work_list.split(",")
            status02 = "⚪️ Завершены откатом: <b>" + str(len(work_list))+"</b> RFC\n"
            qty_status02 = int(len(work_list))
            qty_all_status += len(work_list)
            not_successfully_completed = len(work_list)
        ########################################################################
        if "ВыполненоУспешно" in rfc_info8:
            work_list = rfc_info8["ВыполненоУспешно"].split(",")
            status03 = "⚪️ Выполнено успешно: <b>" + str(len(work_list))+"</b> RFC\n"
            qty_status03 = int(len(work_list))
            qty_all_status += len(work_list)
            successfully_completed = len(work_list)
        ########################################################################
        if "Отменено" in rfc_info8:
            work_list = rfc_info8["Отменено"].split(",")
            status04 = "⚪️ Отменено: <b>" + str(len(work_list))+"</b> RFC\n"
            qty_status04 = int(len(work_list))
            qty_all_status += len(work_list)
        ########################################################################
        if "НаПаузе" in rfc_info8:
            work_list = rfc_info8["НаПаузе"].split(",")
            status05 = "⚪️ На паузе: <b>" + str(len(work_list))+"</b> RFC\n"
            qty_status05 = int(len(work_list))
            qty_all_status += len(work_list)
        ########################################################################
        if "НеСогласовано" in rfc_info8:
            work_list = rfc_info8["НеСогласовано"].split(",")
            status06 = "⚪️ Не согласовано: <b>" + str(len(work_list))+"</b> RFC\n"
            qty_status06 = int(len(work_list))
            qty_all_status += len(work_list)
        ########################################################################
        if "Планирование" in rfc_info8:
            work_list = rfc_info8["Планирование"].split(",")
            status07 = "🟢 Планирование: <b>" + str(len(work_list))+"</b> RFC\n"
            qty_status07 = int(len(work_list))
            qty_all_status += len(work_list)
        ########################################################################
        if "Доработка" in rfc_info8:
            work_list = rfc_info8["Доработка"].split(",")
            status08 = "🟢 Доработка: <b>" + str(len(work_list))+"</b> RFC\n"
            qty_status08 = int(len(work_list))
            qty_all_status += len(work_list)
        ########################################################################
        if "ТехнологическоеСогласование" in rfc_info8:
            work_list = rfc_info8["ТехнологическоеСогласование"].split(",")
            status09 = "🟡 Технологическое согласование: <b>" + str(len(work_list))+"</b> RFC\n"
            qty_status09 = int(len(work_list))
            qty_all_status += len(work_list)
        ########################################################################
        if "Оформление" in rfc_info8:
            work_list = rfc_info8["Оформление"].split(",")
            status10 = "🟢 Оформление: <b>" + str(len(work_list))+"</b> RFC\n"
            qty_status10 = int(len(work_list))
            qty_all_status += len(work_list)
        ########################################################################
        if "Разработка" in rfc_info8:
            work_list = rfc_info8["Разработка"].split(",")
            status11 = "🟡 Разработка: <b>" + str(len(work_list))+"</b> RFC\n"
            qty_status11 = int(len(work_list))
            qty_all_status += len(work_list)
        ########################################################################
        if "ФинальноеСогласование" in rfc_info8:
            work_list = rfc_info8["ФинальноеСогласование"].split(",")
            status12 = "🟡 Финальное Согласование: <b>" + str(len(work_list))+"</b> RFC\n"
            qty_status12 = int(len(work_list))
            qty_all_status += len(work_list)
        ########################################################################

    # работаем с процентом закрытых статусов
    all_successfully_completed = not_successfully_completed + successfully_completed
    pr_successfully_completed = 100*not_successfully_completed/all_successfully_completed
    pr_successfully_completed = round(pr_successfully_completed, 1)

    answer_rfc_statistic = (str(answer_rfc_statistic) +
                            "● Статусы согласования:\n" +
                            '● Всего: <b>' + str(qty_status12+qty_status11+qty_status09) + "</b> RFC\n" +
                            str(status11) +
                            str(status12) +
                            str(status09) +
                            " \n" +
                            "● Статусы контроля:\n" +
                            '● Всего: <b>' + str(qty_status07 + qty_status08 + qty_status10) + "</b> RFC\n" +
                            str(status07) +
                            str(status08) +
                            str(status10) +
                            " \n" +
                            "● Закрытые статусы:\n" +
                            '● Всего: <b>' + str(qty_status01 + qty_status02 + qty_status03 +
                                                 qty_status04 + qty_status05 + qty_status06) + "</b> RFC\n" +
                            str(status01) +
                            str(status02) +
                            str(status03) +
                            str(status04) +
                            str(status05) +
                            str(status06) +
                            ' \n' +
                            '● Всего RFC в базе: <b>' + str(qty_all_status) + '</b>\n' +
                            '● Работы завершаются откатом в <b>' + str(pr_successfully_completed) + ' %</b> случаев')

    return answer_rfc_statistic
