from copy import copy
from telebot import TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.types import Message
from telebot.handler_backends import State, StatesGroup

from app.config import settings
from app.utils import get_city_cent_meters, get_price_sqm_model_diff_rate, geocoder
from app.liquidity_model import report
import app.keyboards as keyboard


state_storage = StateMemoryStorage()
bot = TeleBot(settings.telegram_token, state_storage=state_storage)

class FeatureStates(StatesGroup):
    city = State()
    address = State()
    realty_id = State()
    isapartments = State()
    isjk = State()
    price = State()
    area = State()
    roomscount = State()
    floor = State()
    repairtype = State()

@bot.message_handler(commands=["start"])
def start(message: Message):
    bot.set_state(message.from_user.id, FeatureStates.city, message.chat.id)
    
    bot.send_message(
        chat_id=message.chat.id, 
        text=f"Привет, {message.from_user.first_name}, я помощник по оценке ликвидности недвижимости в Москве и Санкт-Петербурге!",
        reply_markup=keyboard.start(),
    )

@bot.message_handler(state="*", commands=['cancel', 'predict'])
def cancel(message):
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, FeatureStates.city, message.chat.id)
    bot.send_message(
        chat_id=message.chat.id,
        text="Нажмите Начать! для оценки нового объекта",
        reply_markup=keyboard.start()
    )

@bot.message_handler(state="*", commands=["help"])
def help(message: Message):
    bot.set_state(message.from_user.id, FeatureStates.city, message.chat.id)
    bot.send_message(
        chat_id=message.chat.id, 
        text="Я помощник по оценке ликвидности недвижимости в Москве и Санкт-Петербурге!",
        reply_markup=keyboard.start(),
    )

@bot.message_handler(state=FeatureStates.city, text=['Начать!'])
def choose_city(message: Message):
    bot.send_message(
        chat_id=message.chat.id,
        text='Выберете, пожалуйста, город, в котором собираетесь продавать недвижимость',
        reply_markup=keyboard.city()
    )
    bot.set_state(message.from_user.id, FeatureStates.address, message.chat.id)


@bot.message_handler(state=FeatureStates.address)
def get_address(message: Message):
    if message.text in keyboard.get_labels(keyboard.city()):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city_name'] = message.text
            data['is_msk'] = 1 if message.text == 'Москва' else 0
        text = f"Укажите точный адрес в городе {message.text} - " \
                "улица, номер дома, корпус, строение.\nНапример: Ясеневая улица, 27/25с2."
        bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=keyboard.hide()
        )
        bot.set_state(message.from_user.id, FeatureStates.realty_id, message.chat.id)
    else:
        bot.reply_to(message, "Используй предложенную клавиатуру. Для описания работы бота -- команда /help")

@bot.message_handler(state=FeatureStates.realty_id)
def get_realty_id(message: Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        city_name = data['city_name']
    address = f"г. {city_name}, {message.text}"
    realty_id = geocoder(address)
    if realty_id is not None:
        text = f"ID дома, который соответствует введенному адресу ({address}) - {realty_id}."
        bot.send_message(message.chat.id, text)
        text = "Производится предрасчет некоторых параметров..."
        bot.send_message(message.chat.id, text)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['address'] = address
            data['realty_id'] = realty_id
            data['city_cent_meters'] = get_city_cent_meters(realty_id)
        bot.send_message(
            chat_id=message.chat.id,
            text='Объект является апартаментами?',
            reply_markup=keyboard.yes_no()
        )
        bot.set_state(message.from_user.id, FeatureStates.isapartments, message.chat.id)
    else:
        text = f"Дом не найден.\nНа это может быть две причины:\n1. Введенный адресс некорректен (Найдите дом на карте Yandex и и введите адрес в том формате, в котором он указывается на картах).\n2. Дома нет в базе Циан."
        bot.send_message(message.chat.id, text)

@bot.message_handler(state=FeatureStates.isapartments)
def get_isapartments(message: Message):
    if message.text in keyboard.get_labels(keyboard.yes_no()):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['isapartments'] = 1 if message.text == 'Да' else 0
        bot.send_message(
            chat_id=message.chat.id,
            text='Объект находится в составе ЖК?',
            reply_markup=keyboard.yes_no()
        )
        bot.set_state(message.from_user.id, FeatureStates.isjk, message.chat.id)
    else:
        bot.reply_to(message, "Используй предложенную клавиатуру. Для описания работы бота -- команда /help")

@bot.message_handler(state=FeatureStates.isjk)
def get_isjk(message: Message):
    if message.text in keyboard.get_labels(keyboard.yes_no()):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['isjk'] = 1 if message.text == 'Да' else 0
        bot.send_message(
            chat_id=message.chat.id,
            text='Укажите предполагаемую цену продажи объекта',
            reply_markup=keyboard.hide()
        )
        bot.set_state(message.from_user.id, FeatureStates.price, message.chat.id)
    else:
        bot.reply_to(message, "Используй предложенную клавиатуру. Для описания работы бота -- команда /help")

@bot.message_handler(state=FeatureStates.price)
def get_price(message: Message):
    try:
        price = int(message.text)
        if price > 1_000_000 and price < 100_000_000:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['price'] = price
            bot.send_message(
                chat_id=message.chat.id,
                text='Укажите площадь объекта',
            )
            bot.set_state(message.from_user.id, FeatureStates.area, message.chat.id)
        else:
            bot.reply_to(
                message=message,
                text='Стоимость не попадает в интервал оценки (1млн-100млн), проверьте правильность введенного значения. '
                     'Для описания работы бота -- команда /help'
            )
    except ValueError:
        bot.reply_to(message, 'Введите целое число (полная стоимость в рублях). Для описания работы бота -- команда /help')

@bot.message_handler(state=FeatureStates.area)
def get_totalarea_and_val(message: Message):
    try:
        totalarea = float(message.text)
        if totalarea > 9 and totalarea < 250:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['totalarea'] = totalarea
                data['price_sqm'] = data['price'] / totalarea
            bot.send_message(
                chat_id=message.chat.id,
                text='Укажите комнатность',
                reply_markup=keyboard.room(),
            )
            bot.set_state(message.from_user.id, FeatureStates.roomscount, message.chat.id)
        else:
            bot.reply_to(
                message=message,
                text='Площадь не попадает в интервал оценки (9м-250м), проверьте правильность введенного значения. '
                     'Для описания работы бота -- команда /help'
            )
    except ValueError:
        bot.reply_to(message, 'Введите действительное число (например, 32.5 или 25). Для описания работы бота -- команда /help')

@bot.message_handler(state=FeatureStates.roomscount)
def get_roomscount(message: Message):
    if message.text in keyboard.get_labels(keyboard.room()):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['room'] = message.text
            if message.text == "Студия":
                data['roomscount'] = 0
            else:
                data['roomscount'] = int(message.text)
        bot.send_message(
            chat_id=message.chat.id,
            text='Укажите этаж, на котором расположен объект',
            reply_markup=keyboard.floor()
        )
        bot.set_state(message.from_user.id, FeatureStates.floor, message.chat.id)
    else:
        bot.reply_to(message, "Используй предложенную клавиатуру. Для описания работы бота -- команда /help")

@bot.message_handler(state=FeatureStates.floor)
def get_floor(message: Message):
    if message.text in keyboard.get_labels(keyboard.floor()):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['floor'] = message.text
        bot.send_message(
            chat_id=message.chat.id,
            text='Выберете тип ремонта',
            reply_markup=keyboard.repairtype()
        )
        bot.set_state(message.from_user.id, FeatureStates.repairtype, message.chat.id)
    else:
        bot.reply_to(message, "Используй предложенную клавиатуру. Для описания работы бота -- команда /help")

@bot.message_handler(state=FeatureStates.repairtype)
def get_val_and_predict(message: Message):
    if message.text in keyboard.get_labels(keyboard.repairtype()):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['repairtype'] = message.text
            data['price_sqm_model_diff_rate'] = get_price_sqm_model_diff_rate(data)
            features = data
        
        rep = report(copy(features))
        caption = f"С вероятностью {round((1 - rep['good']['pred']) * 100, 1)}%" \
               f" объект будет реализован за 90 дней." \
               f" Это примерно в {round((1 - rep['good']['pred']) / (1 - rep['bad']['pred']), 1)} раз вероятнее," \
               f" чем если бы продажа происходила без сервиса 'Обмен квартиры'." \
               f" Цена объекта по версии модели ликвидности - {rep['good']['bin']}."
        # if rep['best']['cost_diff'] > 0:
        caption += f"\nПри этом, если допустить дисконт в размере {rep['best']['price_ch']}%," \
                f" то вероятность продажи увеличится в {round((1 - rep['best']['pred']) / (1 - rep['good']['pred']), 1)} раз." \
                f" А экономия затрат за весь срок экспозиции составит примерно {round(rep['best']['cost_diff'] * 100, 1)}%."
        text = "__Введенные параметры:__"
        for feature in ['address', 'isapartments', 'isjk', 'price', 'totalarea', 'room', 'floor']:
            text += f'\n*{feature}*: {features[feature]}'
        bot.send_message(
            chat_id=message.chat.id,
            text=text,
        )
        bot.send_photo(
            chat_id=message.chat.id,
            photo=rep['plot'],
            caption=caption,
            reply_markup=keyboard.start()
        )
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.set_state(message.from_user.id, FeatureStates.city, message.chat.id)
    else:
        bot.reply_to(message, "Используй предложенную клавиатуру. Для описания работы бота -- команда /help")

@bot.message_handler(func=lambda message: True)
def incorrect_message(message):
    bot.reply_to(message, "Кажется, я тебя не понимаю. Для описания работы бота используй команду /help")

if __name__ == "__main__":
    bot.add_custom_filter(custom_filters.TextMatchFilter())
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling(skip_pending=True)