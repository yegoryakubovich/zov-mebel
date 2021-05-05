import urllib

import requests

import db
import telebot  # pip3 install pytelegrambotapi
import configparser
import os

config = configparser.ConfigParser()
config.read('config.ini', encoding="utf-8")

# Константы

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
TOKEN = config['settings']['token']
GROUP = config['settings']['group']

texts = {

    'welcome_name': 'Добро пожаловать!\n\nВведите Ваше имя:',
    'welcome_surname': 'Введите Вашу фамилию:',
    'welcome_address': 'Введите Ваш адрес:',
    'suc_application': 'Ваша заявка на регистрацию успешно создана!\n\n'
                       'Имя: {}\n'
                       'Фамилия: {}\n'
                       'Адрес: {}\n\n'
                       'Заявка отправлена администрации на проверку, мы опевестим Вас по ее окончанию!',
    'adm_suc_application': 'Новая заявка!\n\n'
                           'Имя: {}\n'
                           'Фамилия: {}\n'
                           'Адрес: {}\n\n'
                           'Для проверки перейдите в панель администратора.',

    'fail_menu': 'Ваша заявка на проверке!\n\n'
                 'Имя: {}\n'
                 'Фамилия: {}\n'
                 'Адрес: {}\n\n'
                 'Мы опевестим Вас после ее окончанию!',

    'error_cmd': 'Такой команды не существует, повторите попытку.',

    'suc_adm': 'Вы успешно перешли в меню администратора.',
    'new_app': 'Идентификатор: {}\n'
               'Имя: {}\n'
               'Фамилия: {}\n'
               'Адрес: {}\n\n'
               'Примите, или откажите заявку.',
    'fail_new_app': 'Новые заявки отсутствуют!',
    'fail_adm_msg': 'Новые сообщения отсутствуют!',
    'fail_new_app_adm': 'Заявки уже проверяет администратор, его идентификатор: {}.',
    'fail_msg_adm': 'Сообщения уже проверяет администратор, его идентификатор: {}.',
    'fail_new_news_adm': 'Новость уже создает администратор, его идентификатор: {}.',

    'adm_news_date': 'Введите дату новости, к примеру: 04.05.2021',
    'adm_news_img': 'Загрузите изображение.',
    'adm_news_text': 'Введите текст новости.',
    'adm_news_url': 'Введите ссылку новости.',
    'adm_news_status': 'Рассылка пользователям.\n\n'
                       '[{}%] {}',

    'adm_news': 'Добавлена новая новость!\n\n'
                'Дата: {}\n'
                'Текст: {}\n'
                'Ссылка: <a href="{}">тык</a>\n'
                'Картинка прикреплена.',

    'adm_approve_app': 'Заявка одобрена',
    'adm_deny_app': 'Заявка отказана',

    'back_adm': 'Вы возвращены в меню администратора.',
    'back_main': 'Вы возвращены в главное меню.',

    'approve_app': 'Поздравляем, ваша Заявка одобрена!',
    'deny_app': 'Заявка отказана!',

    'news_date': 'Показаны новости за {} г.',


    'catalogs': 'Перейдите по <a href="https://drive.google.com/drive/folders/13jtn6PW-LPrFNP6RSFeUKWaKJnfbpwHw">ссылке</a> для просмотра каталогов',
    'prices': 'Перейдите по <a href="https://drive.google.com/drive/folders/1MSW6JcW1iibgnsMTh2nC2CeEjtuDsgix">ссылке</a> для просмотра прайса.',

    'suc_message': 'Введите текст Вашего сообщения',
    'fail_message': 'У вас уже есть неотвеченные сообщения.',
    'suc_new_massage': 'Ваше сообщение поставлено в очередь, мы уведомим Вас как только модераторы ответят на него!',
    'adm_new_massage': 'Новое сообщение!\n\n'
                       'Пользователь: <a href="t.me/{}">{} {}</a> | id{}\n'
                       'Текст сообщения: {}\n\n'
                       'Для ответа перейдите в панель администратора.',

    'suc_adm_msg': 'Новое сообщение!\n\n'
                   'Пользователь: {} {} | id{}\n'
                   'Текст сообщения: {}\n\n'
                   'Введите ответ.',

    'suc_adm_send': 'Сообщение отправлено!\n\n'
                    'Вы возвращены в панель администратора.',

    'suc_send': 'Получен ответ от администратора!\n\n'
                'Вопрос: {}\n'
                'Ответ: {}',

    'error': 'Произошла ошибка, пожалуйста, повторите попытку.',
}

# Массивы и переменные

reg = []
adm_applications = None
adm_messages = None
adm_news = None
new_news = {
    'date': None,
    'text': None,
    'url': None,
    'img': None,
}
in_news = []

# Клавиатуры

kb_main = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_main.row('📰 Новости')
kb_main.row('📂 Каталоги', '📃 Прайсы')
kb_main.row('✉ Написать нам')

kb_adm = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_adm.row('Заявки', 'Сообщения')
kb_adm.row('Создать новость')
kb_adm.row('Вернуться назад')

kb_adm_app = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_adm_app.row('Принять', 'Отказать')
kb_adm_app.row('Вернуться назад')

kb_back = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_back.row('Вернуться назад')


bot = telebot.TeleBot(TOKEN)


# Обработка - бот


def give_kb(date):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    kb.row('<', date, '>')
    kb.row('Вернуться назад')
    return kb


def give_news(text, url):
    news = '{}\n\n' \
           'Подробности вы можете найти по <a href="{}">ссылке</a>.'.format(text, url)
    return news


def send_news(user_id, news, params=None):
    try:
        img_file = open('photos/' + news['img'], 'rb')
        if not params:
            text = give_news(news['text'], news['url'])
            bot.send_photo(user_id, img_file, text, reply_markup=give_kb(news['date']), parse_mode='HTML')
        else:
            text = texts['adm_news'].format(news['date'], news['text'], news['url'])
            bot.send_photo(user_id, img_file, text, parse_mode='HTML')
    except:
        print('Ошибка новости')

# Обработка сообщений


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user_id = message.from_user.id
    try:
        if db.Account.exits(user_id):  # Проверка на регистрацию
            user = db.Account.select(user_id)
            msg = message.text
            if user['status'] == 1:  # Проверка на доступ

                if msg == '/adm' and db.Admin.exits(user_id):
                    bot.send_message(chat_id=user_id,
                                     text=texts['suc_adm'],
                                     reply_markup=kb_adm
                                     )
                    bot.register_next_step_handler(message, adm)

                elif msg == '📰 Новости':
                    date = db.News.select_dates()[0]
                    news = db.News.select(date)
                    bot.send_message(user_id, texts['news_date'].format(date))
                    for i in news:
                        send_news(user_id, i)


                    in_news.append({
                        'user_id': user_id,
                        'date': date
                    })
                    bot.register_next_step_handler(message, bot_news)

                elif msg == '✉ Написать нам':
                    if not db.Message.exits(user_id):
                        bot.send_message(user_id, texts['suc_message'], reply_markup=kb_back)
                        bot.register_next_step_handler(message, messages)
                    else:
                        bot.send_message(user_id, texts['fail_message'], reply_markup=kb_main)
                elif msg == '📂 Каталоги':
                    bot.send_message(user_id, texts['catalogs'], parse_mode='HTML')

                elif msg == '📃 Прайсы':
                    bot.send_message(user_id, texts['prices'], parse_mode='HTML')

                else:
                    bot.send_message(chat_id=user_id,
                                     text=texts['error_cmd'],
                                     reply_markup=kb_main
                                     )
            elif user['status'] == -1:  # Заявка отказана
                bot.send_message(chat_id=user_id,
                                 text=texts['deny_app'])
            else:
                bot.send_message(chat_id=user_id,
                                 text=texts['fail_menu'].format(
                                     user['name'],
                                     user['surname'],
                                     user['address']
                                 ))
        else:
            reg.append({
                'id': user_id,
                'name': None,
                'surname': None,
                "address": None
            })
            bot.send_message(chat_id=user_id,
                             text=texts['welcome_name'])
            bot.register_next_step_handler(message, reg_name)

    except:
        bot.send_message(chat_id=user_id,
                         text=texts['error'])


def messages(message):
    user_id = message.from_user.id
    try:

        msg = message.text

        if msg == 'Вернуться назад':
            bot.send_message(chat_id=user_id,
                             text=texts['back_main'],
                             reply_markup=kb_main)

        else:
            username = message.from_user.username
            user = db.Account.select(user_id)
            db.Message.insert(user_id, msg)
            bot.send_message(user_id, texts['suc_new_massage'], reply_markup=kb_main)
            bot.send_message(GROUP, texts['adm_new_massage'].format(username, user['name'], user['surname'], user_id, msg), parse_mode='html')


    except:
        bot.send_message(chat_id=user_id,
                         text=texts['error'])
        bot.register_next_step_handler(message, messages)


def bot_news(message):
    user_id = message.from_user.id
    try:

        msg = message.text

        if msg == 'Вернуться назад':
            bot.send_message(chat_id=user_id,
                             text=texts['back_main'],
                             reply_markup=kb_main)
            for user in in_news:
                if user['user_id'] == user_id:
                    in_news.remove(user)

        else:

            dates = db.News.select_dates()

            for user in in_news:
                if user['user_id'] == user_id:
                    с = 0
                    if msg == '<':
                        c = 1
                        index = dates.index(user['date']) - 1
                        date = dates[index]
                        news = db.News.select(date)

                    elif msg == '>':
                        c = 1
                        index = dates.index(user['date']) + 1
                        if len(dates) - 1 < index:
                            index = 0

                        date = dates[index]
                        news = db.News.select(date)

                    if c == 0:
                        bot.send_message(chat_id=user_id,
                                         text=texts['error_cmd'],
                                         reply_markup=kb_adm)
                        bot.register_next_step_handler(message, bot_news)

                    else:
                        user['date'] = date
                        bot.send_message(user_id, texts['news_date'].format(date))
                        for i in news:
                            send_news(user_id, i)
                        bot.register_next_step_handler(message, bot_news)

    except:
        for user in in_news:
            if user['user_id'] == user_id:
                in_news.remove(user)
        bot.send_message(chat_id=user_id,
                         text=texts['error'])


def adm(message):
    user_id = message.from_user.id
    try:

        global adm_applications
        global adm_news
        global adm_messages
        msg = message.text

        if msg == 'Вернуться назад':
            bot.send_message(chat_id=user_id,
                             text=texts['back_main'],
                             reply_markup=kb_main)

        elif msg == 'Заявки':
            app = db.application_select()
            if app:
                if not adm_applications:
                    adm_applications = user_id
                    bot.send_message(chat_id=user_id,
                                     text=texts['new_app'].format(
                                         app['user_id'],
                                         app['name'],
                                         app['surname'],
                                         app['address']
                                     ),
                                     reply_markup=kb_adm_app)
                    bot.register_next_step_handler(message, adm_app)
                else:
                    bot.send_message(chat_id=user_id,
                                     text=texts['fail_new_app_adm'].format(adm_applications),
                                     reply_markup=kb_adm)
                    bot.register_next_step_handler(message, adm)
            else:
                bot.send_message(chat_id=user_id,
                                 text=texts['fail_new_app'].format(adm_applications),
                                 reply_markup=kb_adm)
                bot.register_next_step_handler(message, adm)

        elif msg == 'Сообщения':
            new_msg = db.Message.select()
            if new_msg:
                if not adm_messages:
                    adm_messages = user_id
                    user = db.Account.select(new_msg['user_id'])
                    bot.send_message(chat_id=user_id,
                                     text=texts['suc_adm_msg'].format(
                                         user['name'], user['surname'],
                                         user['user_id'],
                                         new_msg['text']
                                     ),
                                     reply_markup=kb_back)
                    bot.register_next_step_handler(message, adm_msg)
                else:
                    bot.send_message(chat_id=user_id,
                                     text=texts['fail_msg_adm'].format(adm_applications),
                                     reply_markup=kb_adm)
                    bot.register_next_step_handler(message, adm)
            else:
                bot.send_message(chat_id=user_id,
                                 text=texts['fail_adm_msg'].format(adm_applications),
                                 reply_markup=kb_adm)
                bot.register_next_step_handler(message, adm)

        elif msg == 'Создать новость':
            if not adm_news:
                adm_news = user_id
                bot.send_message(chat_id=user_id,
                                 text=texts['adm_news_date'],
                                 reply_markup=kb_back)
                bot.register_next_step_handler(message, adm_news_date)
            else:
                bot.send_message(chat_id=user_id,
                                 text=texts['fail_new_news_adm'].format(adm_applications),
                                 reply_markup=kb_adm)
                bot.register_next_step_handler(message, adm)

        else:
            bot.send_message(chat_id=user_id,
                             text=texts['error_cmd'],
                             reply_markup=kb_adm)
            bot.register_next_step_handler(message, adm)

    except:
        bot.send_message(chat_id=user_id,
                         text=texts['error'])
        bot.register_next_step_handler(message, adm)


def adm_msg(message):
    user_id = message.from_user.id
    try:
        msg = message.text
        new_msg = db.Message.select()
        adm_messages = None

        if msg == 'Вернуться назад':
            bot.send_message(chat_id=user_id,
                             text=texts['back_adm'],
                             reply_markup=kb_adm)
            bot.register_next_step_handler(message, adm)

        else:
            # Отправка пользователю
            bot.send_message(chat_id=user_id,
                             text=texts['suc_send'].format(new_msg['text'], msg),
                             reply_markup=kb_adm)
            db.Message.update_status(new_msg['user_id'])

            # Отправка администратору
            bot.send_message(chat_id=user_id,
                         text=texts['suc_adm_send'],
                         reply_markup=kb_adm)
            bot.register_next_step_handler(message, adm)

    except:
        bot.send_message(chat_id=user_id,
                         text=texts['error'])
        bot.register_next_step_handler(message, adm_msg)


def adm_app(message):
    user_id = message.from_user.id
    try:
        global adm_applications
        msg = message.text
        app = db.application_select()
        adm_applications = None
        if msg == 'Принять':
            db.Account.update_status(app['user_id'], 1)
            bot.send_message(chat_id=user_id,
                             text=texts['adm_approve_app'],
                             reply_markup=kb_adm)
            bot.register_next_step_handler(message, adm)

            bot.send_message(chat_id=app['user_id'],
                             text=texts['approve_app'],
                             reply_markup=kb_main)

        elif msg == 'Отказать':
            db.Account.update_status(app['user_id'], -1)
            bot.send_message(chat_id=user_id,
                             text=texts['adm_deny_app'],
                             reply_markup=kb_adm)
            bot.register_next_step_handler(message, adm)

            bot.send_message(chat_id=app['user_id'],
                             text=texts['deny_app'])

        else:
            bot.send_message(chat_id=user_id,
                             text=texts['back_adm'],
                             reply_markup=kb_adm)
            bot.register_next_step_handler(message, adm)

    except:
        bot.send_message(chat_id=user_id,
                         text=texts['error'])
        bot.register_next_step_handler(message, adm)


def adm_news_date(message):
    user_id = message.from_user.id
    try:
        global adm_news
        msg = message.text
        if msg == 'Вернуться назад':
            adm_news = None
            bot.send_message(chat_id=user_id,
                             text=texts['back_adm'],
                             reply_markup=kb_adm)
            bot.register_next_step_handler(message, adm)

        else:
            new_news['date'] = msg
            bot.send_message(chat_id=user_id,
                             text=texts['adm_news_img'],
                             reply_markup=kb_back)
            bot.register_next_step_handler(message, adm_news_img)

    except:
        bot.send_message(chat_id=user_id,
                         text=texts['error'])
        bot.register_next_step_handler(message, adm_news_date)


def adm_news_img(message):
    user_id = message.from_user.id
    try:
        global adm_news
        msg = message.text
        if msg == 'Вернуться назад':
            adm_news = None
            bot.send_message(chat_id=user_id,
                             text=texts['back_adm'],
                             reply_markup=kb_adm)
            bot.register_next_step_handler(message, adm)

        else:

            file_info = bot.get_file(message.photo[-1].file_id)
            file_name = file_info.file_path.replace("photos/", "")
            file_path = file_info.file_path
            url = 'http://api.telegram.org/file/bot{}/{}'.format(TOKEN, file_path)  # Ссылке
            file_path = os.path.join(THIS_FOLDER, file_info.file_path)
            urllib.request.urlretrieve(url, file_path)

            new_news['img'] = file_name
            bot.send_message(chat_id=user_id,
                             text=texts['adm_news_text'],
                             reply_markup=kb_back)
            bot.register_next_step_handler(message, adm_news_text)

    except:
        bot.send_message(chat_id=user_id,
                         text=texts['error'])
        bot.register_next_step_handler(message, adm_news_img)


def adm_news_text(message):
    user_id = message.from_user.id
    try:
        global adm_news
        msg = message.text
        if msg == 'Вернуться назад':
            adm_news = None
            bot.send_message(chat_id=user_id,
                             text=texts['back_adm'],
                             reply_markup=kb_adm)
            bot.register_next_step_handler(message, adm)

        else:
            new_news['text'] = msg
            bot.send_message(chat_id=user_id,
                             text=texts['adm_news_url'],
                             reply_markup=kb_back)
            bot.register_next_step_handler(message, adm_news_url)

    except:
        bot.send_message(chat_id=user_id,
                         text=texts['error'])
        bot.register_next_step_handler(message, adm_news_text)


def adm_news_url(message):
    user_id = message.from_user.id
    try:
        global adm_news
        msg = message.text
        if msg == 'Вернуться назад':
            adm_news = None
            bot.send_message(chat_id=user_id,
                             text=texts['back_adm'],
                             reply_markup=kb_adm)
            bot.register_next_step_handler(message, adm)

        else:
            # Создание новости
            new_news['url'] = msg
            db.News.insert(new_news['date'], new_news['text'], new_news['url'], new_news['img'])

            # Отправка в группу
            send_news(GROUP, new_news, True)

            # Отправка всем пользователям
            accounts = db.Account.select_all_user_id()
            len_accounts = len(accounts) - 1
            one = 1*100/len_accounts
            one_symb = 1*20/len_accounts
            message_data = bot.send_message(user_id, texts['adm_news_status'].format(0, ''))
            message_id = message_data.message_id

            count = 0
            for i in accounts:
                if i != user_id:
                    send_news(i, new_news)
                    count += 1
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=message_id,
                                          text=texts['adm_news_status'].format(int(one*count), int(one_symb)*'#'))

            bot.edit_message_text(chat_id=user_id,
                                  message_id=message_id,
                                  text=texts['adm_news_status'].format(100, '#'*20))

            # Подтверждение отправки админу
            bot.send_message(chat_id=user_id,
                             text=texts['back_adm'],
                             reply_markup=kb_adm)
            adm_news = None
            bot.register_next_step_handler(message, adm)

    except:
        bot.send_message(chat_id=user_id,
                         text=texts['error'])
        bot.register_next_step_handler(message, adm_news_url)


def reg_name(message):
    user_id = message.from_user.id
    try:
        for user in reg:
            if user['id'] == user_id:
                user['name'] = message.text
                bot.send_message(chat_id=user_id,
                                 text=texts['welcome_surname'])
                bot.register_next_step_handler(message, reg_surname)
    except:
        bot.send_message(chat_id=user_id,
                         text=texts['error'])
        bot.register_next_step_handler(message, reg_name)


def reg_surname(message):
    user_id = message.from_user.id
    try:
        for user in reg:
            if user['id'] == user_id:
                user['surname'] = message.text
                bot.send_message(chat_id=user_id,
                                 text=texts['welcome_address'])
                bot.register_next_step_handler(message, reg_address)
    except:
        bot.send_message(chat_id=user_id,
                         text=texts['error'])
        bot.register_next_step_handler(message, reg_surname)


def reg_address(message):
    user_id = message.from_user.id
    try:
        for user in reg:
            if user['id'] == user_id:
                user['address'] = message.text
                db.Account.insert(user_id,
                                  user['name'],
                                  user['surname'],
                                  user['address'])
                bot.send_message(chat_id=user_id,
                                 text=texts['suc_application'].format(
                                     user['name'],
                                     user['surname'],
                                     user['address']
                                 ))
                bot.send_message(chat_id=GROUP,
                                 text=texts['adm_suc_application'].format(
                                     user['name'],
                                     user['surname'],
                                     user['address']
                                 ))
    except:
        bot.send_message(chat_id=user_id,
                         text=texts['error'])
        bot.register_next_step_handler(message, reg_address)


bot.polling(none_stop=True)
