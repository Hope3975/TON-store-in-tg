import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from db_queries import insert_photo, fetch_photos_by_user_id

from db_queries import get_photo_and_caption  

API_TOKEN = ''
ALLOWED_USERS = []

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
#АДМИН
@dp.message_handler(commands=['startAD'])
async def cmd_start(message: types.Message, state=None):
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply("У вас нет доступа к этой команде.")
        return

    txt = (
        "Добро пожаловать в новую эру торговли! \n"
        "/help для просмотра функций бота."
    )
    await message.reply(txt)

@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply("У вас нет доступа к этой команде.")
        return
    help_text = (
        "Список доступных команд:\n"
        "/add - добавить товар\n"
        "/check - проверить товары\n"
    )
    await message.reply(help_text)

PHOTO_DIR = 'photos'
os.makedirs(PHOTO_DIR, exist_ok=True)

@dp.message_handler(commands=['add'])
async def cmd_add(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply("У вас нет доступа к этой команде.")
        return
    await message.reply("Пожалуйста, отправьте фото!")

temp_storage = {}

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def process_photo(message: types.Message):
    try:
        photo = message.photo[-1]
        user_id = message.from_user.id
        user_folder = os.path.join(PHOTO_DIR, str(user_id))

        os.makedirs(user_folder, exist_ok=True)

        file_path = os.path.join(user_folder, f"{photo.file_id}.jpg")
        await photo.download(file_path)

        temp_storage[user_id] = {'file_path': file_path}

        await message.reply("Пожалуйста, напишите описание для фото.")

    except Exception as e:
        await message.reply(f"Ошибка при загрузке фотографии: {str(e)}")

@dp.message_handler(lambda message: message.from_user.id in temp_storage)
async def process_caption(message: types.Message):
    user_id = message.from_user.id
    caption = message.text

    file_path = temp_storage[user_id]['file_path']

    insert_photo(user_id, file_path, caption)

    del temp_storage[user_id]

    await message.reply(f"Фото сохранено в папке с вашим ID. Путь до файла: {file_path}")
    phototxt = (
        "Успешно! используйте /help для работы с ботом"
    )
    await bot.send_message(message.chat.id, phototxt)


@dp.message_handler(commands=['check'])
async def cmd_check(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await message.reply("У вас нет доступа к этой команде.")
        return
    user_id = message.from_user.id

    results = fetch_photos_by_user_id(user_id)

    if not results:
        await message.reply("Вы ничего не выкладывали!")
    else:
        for file_path, caption in results:
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as photo:
                    await bot.send_photo(message.chat.id, photo, caption=caption)
                    phototxt = (
                        "Успешно! используйте /help для работы с ботом"
                    )
                    await bot.send_message(message.chat.id, phototxt)
            else:
                await message.reply(f"Файл не найден: {file_path}")


#КЛИЕНТ
@dp.message_handler(commands=['start'], chat_type=types.ChatType.PRIVATE)
async def cmd_start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Показать товар"))
    await message.reply("Привет! Нажми на кнопку, чтобы увидеть шлюх.", reply_markup=markup)

@dp.message_handler(lambda message: message.text == "Показать товар", chat_type=types.ChatType.PRIVATE)
async def process_show_photo(message: types.Message):
    file_path, caption = await get_photo_and_caption()  # Call the function from db_queries.py
    if file_path and caption:
        url_markup = InlineKeyboardMarkup()
        url_markup.add(InlineKeyboardButton(text="Купить", url="https://t.me/Krauf_7802"))
        await bot.send_photo(chat_id=message.from_user.id, photo=open(file_path, 'rb'), caption=caption, parse_mode=ParseMode.HTML, reply_markup=url_markup)
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Нет доступных фотографий.")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)