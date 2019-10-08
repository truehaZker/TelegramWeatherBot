# coding=utf-8
import pyowm
import telebot as tb
from googletrans import Translator
from telebot import types

TOKEN = 'TOKEN'
bot = tb.TeleBot(TOKEN)

# Подключаем переводчик
# ---------------------
# ПЕРЕВОДЧИК ИСПОЛЬЗУЕТСЯ,
# ТАК КАК OWM ЛУЧШЕ ПОНИМАЕТ
# НАЗВАНИЯ ГОРОДОВ ПО АНГЛИЙСКИ
# ---------------------
translator = Translator()

# Подключаем OWM API
forecast = pyowm.OWM('TOKEN', language='ru')

# Это ветер
wreq = ''

# Это температура
req = ''

# Создаем клавиатуру для стандартных городов
# ---------------------
# ОТПРАВИТЬ ПОЛЬЗОВАТЕЛЮ
# НУЖНУЮ КЛАВИАТУРУ МОЖНО
# В ОТВЕТНОМ СООБЩЕНИИ (СМ. СТРЕЛОЧКИ):
# bot.send_message(КОМУ, "СООБЩЕНИЕ", --> reply_markup=keyboard) <--
# ---------------------

moscow = types.KeyboardButton(text="Москва")
saintp = types.KeyboardButton(text="Санкт Петербург")
kazan = types.KeyboardButton(text="Казань")
sam = types.KeyboardButton(text="Самара")
diff = types.KeyboardButton(text="Другой город...")

keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
keyboard.add(moscow, saintp, kazan, sam, diff)

markup = types.ReplyKeyboardRemove(selective=True)


# Создаем условия, зависящие от скорости ветра

def locwind(x):
    global wreq

    if 3 <= x <= 5:
        wreq = 'Кажется, в городе ветрено.'
    elif 5 < x <= 10:
        wreq = 'Кажется, в городе очень сильный ветер, будьте бдительны.'
    elif 10 < x:
        wreq = 'Кажется, в городе ураган! По возможности остантесь дома.'
    else:
        wreq = 'Ветра нет или он не значительный'


# Создаем условия, зависящие от температуры

def loctips(y):
    global req

    if y <= -30:
        req = 'там мороз. Советуем надеть все самое теплое, что есть в доме'
    elif -30 < y <= -20:
        req = 'рекомендуем одеться потеплее, на улице холодно'
    elif -20 < y <= -10:
        req = 'рекомендуем надеть пуховик и подштанники'
    elif -10 < y <= -5:
        req = 'рекомендуем надеть теплую куртку и теплые штаны'
    elif -5 < y <= 9:
        req = 'рекомендуем надеть теплую куртку'
    elif 9 < y <= 13:
        req = 'рекомендуем надеть теплую ветровку и джинсы'
    elif 13 < y <= 18:
        req = 'рекомендуем надеть теплую кофту'
    elif 18 < y <= 20:
        req = 'рекомендуем взять с собой легкую кофточку'
    elif 20 < y < 30:
        req = 'рекомендуем надеть легкую майку и шорты'
    elif y >= 30:
        req = 'рекомендуем надеть головной убор. На улице очень жарко'


# Отправляем приветственное сообщение

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     "Благодаря этому Боту Вы сможете узнать погоду в своем городе!\n\nПросто нажмите нужную кнопку:",
                     reply_markup=keyboard)


# Если получаем любое сообщение от пользователя, проверяем, соответствует ли следующим условиям

@bot.message_handler(content_types=['text'])
def check_city(message):
    # Если получили сообщение с текстом 'Другой город...', то отправляем вопрос
    if message.text == 'Другой город...':
        bot.send_message(message.chat.id, "В каком городе узнать погоду?", reply_markup=markup)

    # Пользователь ввел/выбрал нужный город
    # Проверяем город на существование в системе OWM
    else:
        try:
            # Тут мы переводим наименование города (багует, т.к. есть названия городов типа "Кривой Рог", "Орел" и т.д.)
            translated = translator.translate(message.text, dest='en', src='ru')

            # Получаем нужные данные
            w = forecast.weather_at_place(translated.text)

            # Возвращает JSON со всеми данными
            local = w.get_weather()
            temp = local.get_temperature('celsius')['temp'] // 1
            windSpeed = int(local.get_wind()['speed'] // 1)

            # Запускаем функции, дающие подходящие рекомендации относительно ветра и температуры
            locwind(windSpeed)
            loctips(temp)

            # Сообщаем пользователю в ответном сообщение нужные данные и реплики
            bot.send_message(message.chat.id,
                             f"Сейчас в городе {message.text.title()} температура около {temp}\u2103. Ветер движется со скоростью {windSpeed} м/с.\n\nЕсли вы собираетесь выйти на улицу, то {req}.\n\n{wreq}",
                             reply_markup=keyboard)

        # Ловим ошибку, если запрашиваемого города не существует
        except:
            bot.send_message(message.chat.id,
                             f"Нам очень жаль, мы не знаем где находится '{message.text}'.\n\nПопробуйте выбрать другой город",
                             reply_markup=keyboard)


# Отвечает за работу бота без остановок
bot.polling(none_stop=True)
