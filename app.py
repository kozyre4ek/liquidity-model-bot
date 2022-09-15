from typing import Any, Dict

import telebot

from app.config import settings
from app.utils import *
from app.liquidity_model import predict, _feature_names


bot = telebot.TeleBot(settings.telegram_token)

@bot.message_handler(commands=["help", "start"])
def start(message: telebot.types.Message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}, я помощник по оценке ликвидности недвижимости в Москве и Санкт-Петербурге!")
    choose_city(message)

def choose_city(message: telebot.types.Message):
    text = "Выберете, пожалуйста, город, в котором собираетесь продавать недвижимость."
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row(
        telebot.types.KeyboardButton("Москва"),
        telebot.types.KeyboardButton("Санкт-Петербург"),
    )
    ans = bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=keyboard
    )
    bot.register_next_step_handler(ans, enter_address)

def enter_address(message: telebot.types.Message):
    features = {}
    features['city_name'] = message.text
    text = f"Укажите точный адрес в городе {features['city_name']} - улица, номер дома, корпус, строение.\nНапример: Ясеневая улица, 27/25с2."
    ans = bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(ans, get_realty_id, features)

def get_realty_id(message: telebot.types.Message, features: Dict[str, Any]):
    features['address'] = f"г. {features['city_name']}, {message.text}"
    features['realty_id'] = geocoder(features['address'])
    if features['realty_id'] is not None:
        text = f"ID дома, который соответствует введенному адресу ({features['address']}) - {features['realty_id']}."
        bot.send_message(message.chat.id, text)
        get_model_features(message, features)
    else:
        text = f"Дом не найден.\nНа это может быть две причины:\n1. Введенный адресс некорректен (Найдите дом на карте Yandex и и введите адрес в том формате, в котором он указывается на картах).\n2. Дома нет в базе Циан."
        bot.send_message(message.chat.id, text)
        choose_city(message)

def get_model_features(message: telebot.types.Message, features: Dict[str, Any]):
    features['call_cnt_per_day'] = 0.5
    text = "Производится предрасчет некоторых параметров..."
    bot.send_message(message.chat.id, text)
    features['city_cent_meters'] = get_city_cent_meters(features['realty_id'])
    features['is_msk'] = 1 if features['city_name'] == 'Москва' else 0
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row(
        telebot.types.KeyboardButton("Да"),
        telebot.types.KeyboardButton("Нет"),
    )
    ans = bot.send_message(
        chat_id=message.chat.id,
        text='Объект имеет статус жилого помещения (квартира/апартаменты)?',
        reply_markup=keyboard
    )
    bot.register_next_step_handler(ans, get_is_apartments, features, keyboard)

def get_is_apartments(message: telebot.types.Message, features: Dict[str, Any], keyboard: telebot.types.ReplyKeyboardMarkup):
    features['isapartments'] = 1 if message.text == 'Да' else 0
    ans = bot.send_message(
        chat_id=message.chat.id,
        text='Объект находится в составе ЖК?',
        reply_markup=keyboard
    )
    bot.register_next_step_handler(ans, get_is_jk, features)

def get_is_jk(message: telebot.types.Message, features: Dict[str, Any]):
    features['isjk'] = 1 if message.text == 'Да' else 0
    ans = bot.send_message(
        chat_id=message.chat.id,
        text='Укажите предполагаему цену продажи объекта',
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(ans, get_price, features)

def get_price(message: telebot.types.Message, features: Dict[str, Any]):
    features['price'] = int(message.text)
    ans = bot.send_message(
        chat_id=message.chat.id,
        text='Укажите площадь объекта'
    )
    bot.register_next_step_handler(ans, get_totalarea_and_val, features)

def get_totalarea_and_val(message: telebot.types.Message, features: Dict[str, Any]):
    features['totalarea'] = float(message.text)
    features['price_sqm'] = features['price'] / features['totalarea']
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row(telebot.types.KeyboardButton("Студия"))
    keyboard.row(
        telebot.types.KeyboardButton("1"),
        telebot.types.KeyboardButton("2"),
        telebot.types.KeyboardButton("3"),
        telebot.types.KeyboardButton("4"),
    )
    ans = bot.send_message(
        chat_id=message.chat.id,
        text='Укажите комнатность',
        reply_markup=keyboard
    )
    bot.register_next_step_handler(ans, get_roomscount, features)

def get_roomscount(message: telebot.types.Message, features: Dict[str, Any]):
    features['roomscount'] = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row(
        telebot.types.KeyboardButton("1"),
        telebot.types.KeyboardButton("2"),
    )
    keyboard.row(telebot.types.KeyboardButton("Последний"))
    keyboard.row(telebot.types.KeyboardButton("Другой"))
    ans = bot.send_message(
        chat_id=message.chat.id,
        text='Укажите этаж, на котором расположен объект',
        reply_markup=keyboard
    )
    bot.register_next_step_handler(ans, get_floor, features)

def get_floor(message: telebot.types.Message, features: Dict[str, Any]):
    features['floor'] = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row(
        telebot.types.KeyboardButton("Без ремонта"),
        telebot.types.KeyboardButton("Косметический"),
    )
    keyboard.row(
        telebot.types.KeyboardButton("Евро"),
        telebot.types.KeyboardButton("Дизайнерский"),
    )
    ans = bot.send_message(
        chat_id=message.chat.id,
        text='Укажите ремонт',
        reply_markup=keyboard
    )
    bot.register_next_step_handler(ans, get_val_and_predict, features)

def get_val_and_predict(message: telebot.types.Message, features: Dict[str, Any]):
    features['repairtype'] = message.text
    features['price_sqm_model_diff_rate'] = get_price_sqm_model_diff_rate(features)
    features['isalternative'] = 0
    features['vas_rate'] = 1
    X = [[normalize_feature(feat, features[feat]) for feat in _feature_names]]
    features['pred'] = predict(X)
    bot.send_message(
        chat_id=message.chat.id,
        text='Введенные параметры: ' + "\n".join(list(map(str, features.items()))),
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )
    bot.send_message(
        chat_id=message.chat.id,
        text='Параметры для модели: ' + "\n".join(list(map(str, zip(_feature_names, X[0])))),
    )
    choose_city(message)

if __name__ == "__main__":
    bot.infinity_polling()