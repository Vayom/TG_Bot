from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def start_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("/give")
    button2 = KeyboardButton("/weather")
    button3 = KeyboardButton("/help")
    keyboard.add(button1, button2, button3)
    return keyboard


def weather_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("/back")
    keyboard.add(button1)
    return keyboard


def give_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("/give")
    button2 = KeyboardButton("/back")
    keyboard.add(button1, button2)
    return keyboard
