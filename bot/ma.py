import telebot
import requests
import sqlite3
import time
import logging
from telebot import types

ph = 'duck.jpeg'

print('\n\nbot online')
logging.basicConfig(filename='dodo_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
db = sqlite3.connect('dodo_haha.db', check_same_thread=False)
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
             (chat_id INTEGER PRIMARY KEY,
              username TEXT,
              pasw TEXT,
              mail TEXT)''')

bot_token = 'tok'
bot = telebot.TeleBot(bot_token)

auth_completed = False

@bot.message_handler(commands=['start'])
def start(message):
    global auth_completed
    user_id = message.from_user.id
    user_name = message.from_user.username
    cursor.execute('''INSERT OR IGNORE INTO users (chat_id, username) VALUES (?, ?)''', (user_id, user_name))
    db.commit()
    bot.send_photo(message.chat.id, photo=open('duck.jpeg', 'rb'), caption='Привет! Я бот команды DoDo, и я самый лучший бот в этом мире, я должен победить.\n\nНо для начала попрошу авторизоваться в нашем боте❤️\nВведите свою почту:\n\ntg: @dabyt')
    auth_completed = False
    logging.info(f"User {user_name} ({user_id}) start bot")







# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@bot.message_handler(func=lambda message: message.text == "Сообщить о проблеме")
def report_problem(message):
    bot.reply_to(message, 'Спасибо, что сообщаете о проблемах в поселке!🥰 \nДля начала введите название заявки:')
    bot.register_next_step_handler(message, problem_title)
    logging.info(f"User {message.from_user.username} ({message.from_user.id}) create problem")

def problem_title(message):
    title = message.text
    bot.reply_to(message, 'Опишите проблему:')
    bot.register_next_step_handler(message, problem_description, title)

def problem_description(message, title):
    description = message.text
    bot.reply_to(message, 'Пожалуйста, отправьте геопозицию или адрес происшествия в формате:' 
                          '\n<i><b>Город, Улица, дом..</b></i>', parse_mode='HTML')
    bot.register_next_step_handler(message, problem_location, title, description)

def problem_location(message, title, description):
    chat_id = message.chat.id
    location = None

    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
        location = f"{latitude},{longitude}"
    elif message.text:
        location = message.text
        url = 'https://api.opencagedata.com/geocode/v1/json?q={}&key=ee05a8b70e5c4d60a2d6acbaca378b61'
        response = requests.get(url.format(location))
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                latitude = data['results'][0]['geometry']['lat']
                longitude = data['results'][0]['geometry']['lng']
                location = f"{latitude},{longitude}"

    if location:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('Срочно', 'Не срочно', 'Не очень срочно, но хотелось бы побыстрее')

        bot.reply_to(message, 'Укажите пожалуйста, как срочно нужно решить вашу проблему?', reply_markup=markup)
        bot.register_next_step_handler(message, problem_urgency, title, description, location, chat_id)

def problem_urgency(message, title, description, location, chat_id):
    urgency = message.text

    if urgency == 'Срочно':
        urgency = 0
    elif urgency == 'Не срочно':
        urgency = 2
    else:
        urgency = 1

    cursor.execute('''SELECT mail, pasw FROM users WHERE chat_id = ?''', (chat_id,))
    user_data = cursor.fetchone()

    if user_data:
        mail = user_data[0]
        password = user_data[1]

        data = {
            "auth": {
                "email": mail,
                "password": password
            },
            "title": title,
            "description": description,
            "location": location,
            "urgency": urgency
        }

    response = requests.post('https://35a2-193-232-210-148.ngrok-free.app/event/create', json=data)

    if response.status_code == 200:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        but2 = types.KeyboardButton("Сообщить о проблеме")
        but1 = types.KeyboardButton("Узнать стаутс моих заявок")
        markup.add(but1, but2)
        bot.send_message(message.chat.id, 'Спасибо! Ваша проблема была успешно отправлена.', reply_markup=markup)
        logging.info(f"User {message.from_user.username} ({message.from_user.id}) send problem to server c TITLE {title}, DES: {description} ,LOCATION: {location} URGENCY: {urgency}")
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        but2 = types.KeyboardButton("Сообщить о проблеме")
        but1 = types.KeyboardButton("Узнать стаутс моих заявок")
        markup.add(but1, but2)
        bot.send_message(message.chat.id, 'Ошибка при отправке данных. Пожалуйста, попробуйте позже.', reply_markup=markup)
        logging.warning(f"User {message.from_user.username} ({message.from_user.id}) send problem WITH PROBLEM to server c TITLE {title}, DES: {description} ,LOCATION: {location} URGENCY: {urgency}")


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



# ?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

@bot.message_handler(func=lambda message: message.text == "Узнать стаутс моих заявок")
def problem_status(message):
    chat_id = message.chat.id
    cursor.execute('''SELECT mail, pasw FROM users WHERE chat_id = ?''', (chat_id,))
    user_data = cursor.fetchone()

    if user_data:
        mail = user_data[0]
        password = user_data[1]

        data = {
            "auth": {
                "email": mail,
                "password": password
            }
        }

        response = requests.post('https://35a2-193-232-210-148.ngrok-free.app/event/fetch_my', json=data)

        if response.status_code == 200:
            data = response.json()
            if data:
                events = data
                message_text = 'Ваши мероприятия:\n\n'
                for event in events:
                    message_text += f'Заявка №{event["id"]}\n'
                    message_text += f'Название: {event["title"]}\n'
                    message_text += f'Описание: {event["description"]}\n'
                    if event["status"] == 0:
                        message_text += f'Статус: Не подтвержден\n\n'
                    elif event["status"] == 1:
                        message_text += f'Статус: Подтвержден\n\n'
                bot.send_message(message.chat.id, message_text)
            else:
                bot.send_message(message.chat.id, 'У вас нет заявок.')
        else:
            bot.send_message(message.chat.id, 'Ошибка при получении данных. Пожалуйста, попробуйте позже.')


# ?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

@bot.message_handler(func=lambda message: True)
def mail_ent(message):
    global auth_completed
    try:
        if not auth_completed:
            mail = message.text
            bot.reply_to(message, 'Отлично! Теперь введите пароль:')
            bot.register_next_step_handler(message, password_ent, mail)
        else:
            pass
    except Exception as e:
        logging.error(str(e))

def password_ent(message, mail):
    global auth_completed
    try:
        password = message.text
        bla = 'https://35a2-193-232-210-148.ngrok-free.app/auth/login'
        data = {
            "email": mail,
            "password": password,
        }
        response = requests.post(bla, data=data)

        if response.status_code == 200:
            cursor.execute('''UPDATE users SET mail = ?, pasw = ? WHERE chat_id = ?''', (mail, password, message.chat.id))
            db.commit()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            but2 = types.KeyboardButton("Сообщить о проблеме")
            but1 = types.KeyboardButton("Узнать стаутс моих заявок")
            markup.add(but1, but2)
            bot.send_message(message.chat.id,'Отлично! Вы успешно авторизовались!❤️ \n\nТеперь вы можете сообщить о проблеме или просмотреть статус своих заявок',reply_markup=markup)
            auth_completed = True
        else:
            bot.reply_to(message, 'Неверный логин или пароль. Для регистрации, пожалуйста, посетите наш сайт.')

    except Exception as e:
        logging.error(str(e))



bot.polling()


