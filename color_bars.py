def color_bar(proc):
    # округляем число
    if proc < 100:
        proc = str(proc)
        if len(proc) == 1:
            proc = "0" + proc
        x1 = proc[0]
        x2 = proc[1]
        if int(x2) >= 5:
            x1 = int(x1) + 1
            proc = str(x1) + "0"
            proc = int(proc)
        else:
            proc = str(x1) + "0"
            proc = int(proc)
    # подбираем цвет
    color_bar_el = None
    if proc == 0:
        color_bar_el = "⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"
        # color_bar_el = '▹ [][][][][][][][][][]'
    elif proc == 10:
        color_bar_el = "🟪⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"
        # color_bar_el = '▹ █[][][][][][][][][]'
    elif proc == 20:
        color_bar_el = "🟦🟦⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"
        # color_bar_el = '▹ ██[][][][][][][][]'
    elif proc == 30:
        color_bar_el = "🟩🟩🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️"
        # color_bar_el = '▹ ███[][][][][][][]'
    elif proc == 40:
        color_bar_el = "🟩🟩🟩🟩⬜️⬜️⬜️⬜️⬜️⬜️"
        # color_bar_el = '▹ ████[][][][][][]'
    elif proc == 50:
        color_bar_el = "🟨🟨🟨🟨🟨⬜️⬜️⬜️⬜️⬜️"
        # color_bar_el = '▹ █████[][][][][]'
    elif proc == 60:
        color_bar_el = "🟨🟨🟨🟨🟨🟨⬜️⬜️⬜️⬜️"
        # color_bar_el = '▹ ██████[][][][]'
    elif proc == 70:
        color_bar_el = "🟧🟧🟧🟧🟧🟧🟧⬜️⬜️⬜️"
        # color_bar_el = '▹ ███████[][][]'
    elif proc == 80:
        color_bar_el = "🟧🟧🟧🟧🟧🟧🟧🟧⬜️⬜️"
        # color_bar_el = '▹ ████████[][]'
    elif proc == 90:
        color_bar_el = "🟫🟫🟫🟫🟫🟫🟫🟫🟫️⬜️"
        # color_bar_el = '▹ █████████[]'
    elif proc == 100:
        color_bar_el = "🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥"
        # color_bar_el = '▹ ███████████'
    elif proc > 100:
        color_bar_el = "⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️⬛️"
        # color_bar_el = '▹ ███████████'
    return color_bar_el


# добавляем цветов к статусам
def status_color(st_s):
    status_cl = None
    status_cl_sm = None
    if str(st_s) == "Создание":
        status_cl = "⚪️ Создание"
        status_cl_sm = "⚪️"
    if str(st_s) == "Оформление":
        status_cl = "🟢 Оформление"
        status_cl_sm = "🟢"
    if str(st_s) == "Разработка":
        status_cl = "🟡 Разработка"
        status_cl_sm = "🟡"
    if str(st_s) == "Технологическое согласование":
        status_cl = "🟡 Технологическое согласование"
        status_cl_sm = "🟡"
    if str(st_s) == "Доработка":
        status_cl = "🟢 Доработка"
        status_cl_sm = "🟢"
    if str(st_s) == "Планирование":
        status_cl = "🟢 Планирование"
        status_cl_sm = "🟢"
    if str(st_s) == "Финальное согласование":
        status_cl = "🟡 Финальное согласование"
        status_cl_sm = "🟡"
    if str(st_s) == "Согласовано":
        status_cl = "🟢 Согласовано"
        status_cl_sm = "🟢"
    if str(st_s) == "Не согласовано":
        status_cl = "⚪️ Не согласовано"
        status_cl_sm = "⚪️"
    if str(st_s) == "На паузе":
        status_cl = "⚪️ На паузе"
        status_cl_sm = "⚪️"
    if str(st_s) == "Отменено":
        status_cl = "⚪️ Отменено"
        status_cl_sm = "⚪️"
    if str(st_s) == "Выполнено успешно":
        status_cl = "⚪️ Выполнено успешно"
        status_cl_sm = "⚪️"
    if str(st_s) == "Завершены откатом":
        status_cl = "⚪️ Завершены откатом"
        status_cl_sm = "⚪️"
    if str(st_s) == "Закрыто":
        status_cl = "⚪️ Закрыто"
        status_cl_sm = "⚪️"
    if str(st_s) == "Согласованно (SRFC)":
        status_cl = "🟢 Согласованно (SRFC)"
        status_cl_sm = "🟢"
    return status_cl, status_cl_sm
