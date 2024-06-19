
def sanitize_filename(filename):
    """
    Принимает имя файла и убирает из названия все спец. символы
    :param filename: Имя файла
    :return: Корректное имя файла
    """
    forbidden_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '+', '[', ']']

    sanitized_filename = filename
    for char in forbidden_chars:
        sanitized_filename = sanitized_filename.replace(char, '')
    return sanitized_filename
