from typing import List
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def city() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup()
    keyboard.row(
        KeyboardButton("Москва"),
        KeyboardButton("Санкт-Петербург"),
    )
    return keyboard

def yes_no() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup()
    keyboard.row(
        KeyboardButton("Да"),
        KeyboardButton("Нет"),
    )
    return keyboard

def room() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup()
    keyboard.row(KeyboardButton("Студия"))
    keyboard.row(
        KeyboardButton("1"),
        KeyboardButton("2"),
        KeyboardButton("3"),
        KeyboardButton("4"),
    )
    return keyboard

def floor() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup()
    keyboard.row(
        KeyboardButton("1"),
        KeyboardButton("2"),
    )
    keyboard.row(KeyboardButton("Последний"))
    keyboard.row(KeyboardButton("Другой"))
    return keyboard

def repairtype() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup()
    keyboard.row(
        KeyboardButton("Без ремонта"),
        KeyboardButton("Косметический"),
    )
    keyboard.row(
        KeyboardButton("Евроремонт"),
        KeyboardButton("Дизайнерский"),
    )
    return keyboard

def hide() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()

def get_labels(keyboard: ReplyKeyboardMarkup) -> List[str]:
    keys = []
    for line in keyboard.keyboard:
        for key in line:
            keys.append(list(key.values())[0])
    return keys

