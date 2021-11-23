import sqlite3
import telebot
import pyowm
from datetime import datetime

bot = telebot.TeleBot("TOKEN")
owm=pyowm.OWM('7511e2e4086c7ea3203db8008673826a', language = 'ru')

try:
    sqlite_connection = sqlite3.connect('sqlite_python.db', check_same_thread=False)
    sqlite_create_table_query = '''CREATE TABLE registration (
                                user_name TEXT,
                                user_surname TEXT,
                                user_parent TEXT,
                                user_birthday TEXT,
                                user_email TEXT,
                                user_number INTEGER,
                                user_city TEXT);'''

    cursor = sqlite_connection.cursor()
    print("База данных подключена к SQLite")
    cursor.execute(sqlite_create_table_query)
    sqlite_connection.commit()
    print("Таблица SQLite с регистарцией создана")

except sqlite3.Error as error:
    print("Ошибка при подключении к SQLite с регистрацией", error)
    pass


try:
    sqlite_connection = sqlite3.connect('sqlite_python.db', check_same_thread=False)
    sqlite_create_table_query = '''CREATE TABLE history (
                                user_message TEXT,
                                user_date TEXT,
                                user_time TEXT);'''

    cursor = sqlite_connection.cursor()
    print("База данных подключена к SQLite")
    cursor.execute(sqlite_create_table_query)
    sqlite_connection.commit()
    print("Таблица SQLite с историей создана")

except sqlite3.Error as error:
    print("Ошибка при подключении к SQLite с историей", error)
    pass


def db_table_val(user_name: str, user_surname: str, user_parent: str, user_birthday: str, user_email: str, user_number: int, user_city: str):
	cursor.execute('INSERT INTO registration (user_name, user_surname, user_parent, user_birthday, user_email, user_number, user_city) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_name, user_surname, user_parent, user_birthday, user_email, user_number, user_city))
	sqlite_connection.commit()


def db_table_val_history(user_message: str, user_date: str, user_time: str):
	cursor.execute('INSERT INTO history (user_message, user_date, user_time) VALUES (?, ?, ?)', (user_message, user_date, user_time))
	sqlite_connection.commit()


@bot.message_handler(commands=['start'])
def start_message(message):
	msg = bot.send_message(message.chat.id, 'Привет! Я Бот Олег :)')
	msg = bot.send_message(message.chat.id, 'Напиши "Команды", чтобы узнать, какие команды я воспринимаю...')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):

	us_message = message.text.lower()
	us_date = str(datetime.now().date())
	us_time = str(datetime.now().time())
	db_table_val_history(user_message=us_message, user_date=us_date, user_time=us_time)

	if message.text.lower() == 'привет':
		msg = bot.send_message(message.chat.id, 'Привет! Я Бот Олег :)')
		msg = bot.send_message(message.chat.id, 'Напиши "Команды", чтобы узнать, какие команды я воспринимаю...')

	elif message.text.lower() == 'команды':
		bot.send_message(message.chat.id, '''Команды, которые можно мне писать:\n
• Регистрация  -  ты будешь зарегистрирован
• Проверка *любой текст*  -  я проверю, отправлял ли ты мне сообщение с таким текстом
• Погода  -  я скажу погоду на сегодня в твоем городе''')

	elif message.text.lower() == 'регистрация':
		send = bot.send_message(message.chat.id, '''Отлично, давай зарегистрируемся!
Если ошибешься или передумаешь регистрироваться, просто напиши "Отмена", и регистрация будет остановлена

А теперь напиши, пожалуйста, свое имя!''')	
		bot.register_next_step_handler(send, reg_name)

	elif message.text.lower() == 'проверка':
		send = bot.send_message(message.chat.id, 'Напиши, пожалуйста, сообщение, которое хочешь проверить!')
		bot.register_next_step_handler(send, check)

	elif message.text.lower() == "погода":
		send = bot.send_message(message.chat.id, 'Напиши, пожалуйста, погода в каком городе тебя интересует!')
		bot.register_next_step_handler(send, wether)

	else:
		send = bot.send_message(message.chat.id, '''Дружище, такой команды я, к сожалению, не знаю :(\n
Чтобы посмотреть, какие команды я знаю, просто напиши "Команды" !''')


def reg_name(message):
	if message.text.lower() == "отмена":
		send = bot.send_message(message.chat.id, 'Регистрация остановлена!')
		return
	global us_name
	us_name = message.text
	send = bot.send_message(message.chat.id, 'Фамилию')
	bot.register_next_step_handler(send, reg_surname)

	
def reg_surname(message):
	if message.text.lower() == "отмена":
		send = bot.send_message(message.chat.id, 'Регистрация остановлена!')
		return
	global us_surname
	us_surname = message.text
	send = bot.send_message(message.chat.id, 'Отчество')
	bot.register_next_step_handler(send, reg_parant)


def reg_parant(message):
	if message.text.lower() == "отмена":
		send = bot.send_message(message.chat.id, 'Регистрация остановлена!')
		return
	global us_parent
	us_parent = message.text
	send = bot.send_message(message.chat.id, 'Дату рождения')
	bot.register_next_step_handler(send, reg_birthday)
		

def reg_birthday(message):
	if message.text.lower() == "отмена":
		send = bot.send_message(message.chat.id, 'Регистрация остановлена!')
		return
	global us_birthday
	us_birthday = message.text
	send = bot.send_message(message.chat.id, 'Свой email')
	bot.register_next_step_handler(send, reg_email)


def reg_email(message):
	if message.text.lower() == "отмена":
		send = bot.send_message(message.chat.id, 'Регистрация остановлена!')
		return
	global us_email
	us_email = message.text
	cursor.execute('SELECT * from registration')
	data = cursor.fetchall()
	for i in data:
		if i[4] == us_email:
			send = bot.send_message(message.chat.id, 'Аккаунт с таким email уже существует!')
			return
	send = bot.send_message(message.chat.id, 'Свой номер телефона')
	bot.register_next_step_handler(send, reg_number)


def reg_number(message):
	if message.text.lower() == "отмена":
		send = bot.send_message(message.chat.id, 'Регистрация остановлена!')
		return
	global us_number
	us_number = message.text
	cursor.execute('SELECT * from registration')
	data = cursor.fetchall()
	for i in data:
		if i[5] == us_number:
			send = bot.send_message(message.chat.id, 'Аккаунт с таким номером телефона уже существует!')
			return
	send = bot.send_message(message.chat.id, 'Город, в котором проживаешь')
	bot.register_next_step_handler(send, reg_city)


def reg_city(message):
	if message.text.lower() == "отмена":
		send = bot.send_message(message.chat.id, 'Регистрация остановлена!')
		return
	global us_city
	us_city = message.text
	send = bot.send_message(message.chat.id, 'Отлично, ты зарегистрирован!')
	db_table_val(user_name=us_name, user_surname=us_surname, user_parent=us_parent, user_birthday=us_birthday, user_email=us_email, user_number=us_number, user_city=us_city)


def check(message):
	message_in_history = message.text.lower()
	cursor.execute('SELECT * from history')
	data = cursor.fetchall()
	flag = 0
	for i in data:
		if i[0] == message_in_history:
			flag += 1
			last_date = i[1]
			last_time = i[2]
	if flag != 0:
		flag = str(flag)
		send = bot.send_message(message.chat.id, 'Да, это сообщение ты присылал ' + flag + ' раз. Последний раз ты присылал его ' + i[1] + ' в ' + i[2] + ' !')
	else:
		send = bot.send_message(message.chat.id, 'Нет, такого сообщения ты не присылал...')


def wether(message):
	try:
		observation = owm.weather_at_place(message.text)
		w = observation.get_weather()
		temp=w.get_temperature('celsius')['temp']

		answer = f"В городе {message.text} сейчас {w.get_detailed_status()} \n"
		answer += f"Температура в районе {round(temp)} градусов\n\n"

		if temp<10:
			answer += 'Очень холодно, оденься потеплее...'
		elif temp<17:
			answer += 'Прохладно, лучше оденься...'
		else:
			answer += 'Почти жара! Можно и в шортах прогуляться...'

		send = bot.send_message(message.chat.id, answer)
	except pyowm.exceptions.api_response_error.NotFoundError:
		bot.send_message(message.chat.id, 'Город не найден :(\nПопробуй другой!')

	
bot.polling(none_stop=True)
