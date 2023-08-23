import asyncio
import requests
from config import API_TOKEN, API_OWM_TOKEN
import psycopg2
import random

from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import logging

from aiogram import Dispatcher, Bot, executor, types
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from db_model import Base, MediaIds

HELP_TEXT = '''
/give - рандомная пичка из базы данных
/start - иди нахуй
/count - посмотреть сколько запросов ты выполнил
- отправка стикера, фото, видео или голосового сообщения добавляет файл в базу данных
'''

START_TEXT = '''
У меня есть только /help и
/start
'''

count = 0

bot = Bot(token=API_TOKEN)

dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

DATABASE_URL = 'postgresql://postgres:123@localhost:5432/TG_DB'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


class States(StatesGroup):
    START = State()
    GIVING_ITEM = State()
    LOAD_ITEM = State()


def start_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("/give")
    button2 = KeyboardButton("/help")
    keyboard.add(button1, button2)
    return keyboard


def give_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("/back")
    button2 = KeyboardButton("/give")
    keyboard.add(button1, button2)
    return keyboard


def get_random_record_from_postgres():
    connection = psycopg2.connect(
        database="TG_DB",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM public.\"MediaIds\" ORDER BY RANDOM() LIMIT 1")
    random_record = cursor.fetchone()

    connection.close()
    return random_record


@dp.message_handler(commands=['weather'])
async def weather_state(message: types.Message):
    await message.reply('Введите название городе, погоду которого хотите посмотреть')
    await States.START.set()


@dp.message_handler()
async def weather_print(message: types.Message):
    city_name = message.text

    # Отправляем запрос к OpenWeatherMap API
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_OWM_TOKEN}")
        weather_data = response.json()
        if response.status_code == 200:
            weather_description = weather_data["weather"][0]["description"]
            temperature = weather_data["main"]["temp"] - 273.15  # Конвертируем из Кельвинов в градусы Цельсия
            await message.reply(f"Погода в городе {city_name}: {weather_description}, температура: {temperature:.2f}°C")
        else:
            await message.reply("Не удалось получить данные о погоде.")
    except Exception as e:
        await message.reply("Произошла ошибка при запросе погодных данных.")


@dp.message_handler(commands=['give'])
async def give_random(message: types.Message):
    global count
    count += 1
    random_material = get_random_record_from_postgres()
    if random_material[1] == 'sticker':
        await bot.send_sticker(chat_id=message.chat.id, sticker=random_material[2])
    elif random_material[1] == 'voice':
        await bot.send_voice(chat_id=message.chat.id, voice=random_material[2])
    await States.GIVING_ITEM.set()
    await message.answer('Выберите действие', reply_markup=give_keyboard())


@dp.message_handler(content_types=[types.ContentType.STICKER, types.ContentType.PHOTO, types.ContentType.VIDEO,
                                   types.ContentType.VOICE])
async def handle_all_messages(message: types.Message):
    session = Session()
    global count
    count += 1
    # Сохранение медиафайлов в базу данных
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.sticker:
        file_id = message.sticker.file_id
        file_type = "sticker"
    elif message.voice:
        file_id = message.voice.file_id
        file_type = "voice"
    else:
        return

    # Сохранение информации в базе данных
    media_file = MediaIds(file_id=file_id, file_type=file_type)
    session.add(media_file)
    session.commit()
    session.close()
    print('Работает')


@dp.message_handler(commands='back')
async def help_print(message: types.Message):
    global count
    count += 1
    await message.answer('Возвращение в начальное состояние')
    await message.answer('Выберите действие', reply_markup=start_keyboard())
    await States.START.set()


@dp.message_handler(commands=['help'])
async def help_print(message: types.Message):
    global count
    count += 1
    await message.reply(text=HELP_TEXT)


@dp.message_handler(commands=['count'])
async def count_print(message: types.Message):
    global count
    await message.answer(text=str(count))
    count += 1


@dp.message_handler(commands=['start'])
async def start_print(message: types.Message):
    global count
    count += 1
    await message.answer('Выберите действие', reply_markup=start_keyboard())


@dp.message_handler()
async def echo(message: types.Message):
    global count
    count += 1
    if len(message.text.split()) > 2:
        print(len(message.text.split()) > 2)
        if str(message.text).upper() == str(message.text):
            await message.answer('Ты нахуй орёшь')
            await asyncio.sleep(2)
            await message.answer('МУДАК СУКА')
        else:
            await message.answer(text=str(message.text).upper())


'''@dp.message_handler(content_types=types.ContentType.STICKER)
async def send_sticker_back(message: types.Message):
    await message.reply_sticker(message.sticker.file_id)'''

if __name__ == '__main__':
    executor.start_polling(dp)
