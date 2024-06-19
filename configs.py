import os

import configparser


config_file = configparser.ConfigParser()

# Поднимаемся на уровень выше (из папки pilot в папку проект)
os.chdir(os.pardir)

config_file.read(r'config\config.ini')

# test = config_file['sql']['user']

# доступ к оболочке телеграм
telegram = {
    'name': 'RFC Informer Bot',
    'token': config_file['telegram_bot']['dem_token'],  # демьян
    # 'token': config_file['telegram_bot']['token'],  # rfc bot
    'copilot_token': config_file['telegram_bot']['copilot_token']
}

# доступ к веб-сервису 1с
auth_1c = {
    'link': 'https://pb-project.jet.su/Jet_Zakazy_DO',
    'login': config_file['auth_1c']['login'],
    'password': config_file['auth_1c']['password']
}

# дата и версия системы
version = "2.5.1"  # версия бота
data_version_update = "01.07.2024"  # дата последнего обновления

# доступ к веб-сервису naumen
naumen = {
    'link': 'https://sd.pochtabank.ru',
    'accessKey': config_file['naumen']['accessKey'],
    'cookie': 'JSESSIONID=D785F773AD1DEB5C48F9400A6A6BD3CE'
}

# доступ к базе данных
sql_database = {
    'database': 'rfc_postgres_db',
    'user': config_file['sql']['user'],
    'password': config_file['sql']['password'],
    'host': '127.0.0.1',
    'port': '5432',
}

link = {
    'Инструкция бот': "<a href='https://confluence.jet.su/pages/" +
                      "viewpage.action?pageId=162355250'>Инструкция для работы с RFC informer bot</a>",

    'Список версий': "<a href='https://confluence.jet.su/pages/" +
                     "viewpage.action?pageId=162355252'>История обновлений/Список версий</a>",

    'Инструкция 1c': "<a href='https://confluence.jet.su/pages/" +
                     "viewpage.action?pageId=157929193'>Инструкция для работы в ИС '1С'</a>",

    "ИС '1С'": "<a href='https://pb-project.jet.su/Jet_Zakazy_DO/" +
               "ru_RU/'>Ссылка на рабочую базу ИС '1С'</a>",

    'Список SRFC': "<a href='https://confluence.jet.su/display/" +
                   "pochtabank/SRFC'>Список SRFC</a>"
}
# config.link['Инструкция бот']

# почта отдела
email_name = 'rfc_leto@jet.su'

# имя файла для лога
file_log_name = r'logging\logging_rfc_bot.log'

log_analysis_filename = 'log_analysis.docx'
log_error_filename = r'error\Full_error_log.docx'

workers = {
    'rfc_manager1': {
        'Имя': 'Александр',
        'Ссылка': '@tereander'
    },
    'rfc_manager2': {
        'Имя': 'Анисимов Максим',
        'Ссылка': '@milanoov'
    }
}
# config.workers['rfc_manager1']['Ссылка']


# уровни доступа
access_level = {
    'Доступ запрещен': 6,
    'Пользователь': 5,
    'Пользователь +': 4,
    'Пользователь ++': 3,
    'Администратор': 2,
    'Разработчик': 1,
}

list_files_in_dir = [
    {'file_name': 'admins.py',
     'file_hash': '1766ca435447f36fd33c6aaed37702e64fbfbcda15991ba15c9b54f948f17d28'},
    {'file_name': 'blocks.py',
     'file_hash': '901dcd896539620e377741941efa8994ed32312d60fe21df248efea3b8645e01'},
    {'file_name': 'calendars.py',
     'file_hash': 'fbff847d704658663cd68e5d270675598ca52f4edfd072a3719034a6b8f55c44'},
    {'file_name': 'cerberus.py',
     'file_hash': '76822bda58e2f6f09567f37b5ed00da509c01910e470920e2bb531baa4e605ce'},
    {'file_name': 'clues.py',
     'file_hash': '5e1b90a3b9848f6680650d6aa01afbce6f31ff91abc67c7e98d82a154e875ea3'},
    {'file_name': 'color_bars.py',
     'file_hash': 'd8785386093728f968070559c3b5212ea57d09b4e444b6aa5f9656a9e076a058'},
    {'file_name': 'commands.py',
     'file_hash': '2f92a79e6de64900b8ee376767209ee8c797c277e6828b8d10641e8c8676682e'},
    {'file_name': 'configs.py',
     'file_hash': 'd8480004004bb382ea7c529ef5904e218a1b8bbccf0260cb0851c673e643e866'},
    {'file_name': 'errors.py',
     'file_hash': 'd802bbc5b48e05c8cda29ab0105a606f148e1dcaf7ea6f993fbdd1cecea93532'},
    {'file_name': 'file_processing.py',
     'file_hash': '314081a8d104158f106c4d53e93993c298b5ce134336bbc69eb47296b6c42000'},
    {'file_name': 'firewall_mars.py',
     'file_hash': '9b5e9c14973c505e4bd57f21da572cc36af8350fd0858e5b8b1161adf7e93449'},
    {'file_name': 'integrations.py',
     'file_hash': '85fd1cfca9f28f17a5890ed7ecd52d845b006b274d059ff94c1a84feb316850a'},
    {'file_name': 'keyboards.py',
     'file_hash': 'c69a7d1fafb3175edd1c0896c1fc11e9cb2ae9372cdb5ea3afa3982d8bd0e62f'},
    {'file_name': 'logs.py',
     'file_hash': 'bf15d6922ddc25bd9e00c118c3bdba48b2775c75e1d8919a78a22a53abc25886'},
    {'file_name': 'log_analysis.py',
     'file_hash': 'f66689b4de1b16616d5c9323a9ea6f5105486f2ef15646cb930828235ba9c360'},
    {'file_name': 'long_text.py',
     'file_hash': '9c34c541280a592f4d1ebc4d8bb1f1023979ecfd5071b03d58ba7906b065114a'},
    {'file_name': 'mailing_list.py',
     'file_hash': 'bf92fa226358909dc9213ace99f696ec3f4f2c23be05c59f8fa0c1a19e657dc2'},
    {'file_name': 'main.py',
     'file_hash': '0d83bded4916f755276ba8f96d8b8a859e8c1575070b30995214cb0de2b708b5'},
    {'file_name': 'naumen_search.py',
     'file_hash': 'bb597ca7c7997654123ac656a7359cd938b032ad92a6bf8b703bcdd414144031'},
    {'file_name': 'neuron.py',
     'file_hash': '3e53778312ec31df9213d585c0a46aabdfb7554fe02b0f1aca4f3fbeb799223b'},
    {'file_name': 'patterns.py',
     'file_hash': '2aef37b1b0058fdfe5e62e86b6cedfcda6a0f7d37756a2411b2c7d7b208adad1'},
    {'file_name': 'personality_module.py',
     'file_hash': '3cde4c0ca0dad166256303d3ed6515e8a5763686d8505fc5b2b164ac2f15a985'},
    {'file_name': 'personal_users.py',
     'file_hash': '5f1cacb840ea9dad88d974e3988cf9ef0d8a03a53c1518328cd9fe82a03a9e1c'},
    {'file_name': 'postgres_init.py',
     'file_hash': '699cebff07a4fcd0b0736a33c26126024bfd75547f9be8d33ed4082480511f62'},
    {'file_name': 'protect_content.py',
     'file_hash': '13029ce64a719caf2ad7e73aee79946ed5426f3d813d89e780148e4397bdbf65'},
    {'file_name': 'rfc_search.py',
     'file_hash': '6f9b03ee61431f6df670b11c6a93105dda2df3427995b78cbea9cce859897426'},
    {'file_name': 'rfc_statistic.py',
     'file_hash': 'bc179ec7acc0bca7b9a736215689ff3e9a54d70bb58ad1c3f66079873fb4f4aa'},
    {'file_name': 'search_rfc_main_short.py',
     'file_hash': '7455425dc746e19a9f167edcc479c183719de3e3f2e575ee004c1eab5de8690a'},
    {'file_name': 'servers.py',
     'file_hash': 'd6fd3986381898135c5dd4b3ff3e4e8f6a0491c48c72b22f31c117478d6e29d7'},
    {'file_name': 'settings_config.py',
     'file_hash': 'b0823269fc82f6a2dc5ad90859b07b8201c78c901d5d85eb8a8a9ebba7db75c6'}
]
