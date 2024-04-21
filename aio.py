import aiogram
import requests
import urllib.parse
from aiogram import Router, types, dispatcher
from aiogram.filters import CommandStart, CallbackQuery
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

bot = aiogram.Bot(token='6767096954:AAEUGBFSTDqQHW476WrBiMTwRBJ3PM8UJ14')
dp = aiogram.Dispatcher(bot=bot)
router = Router()
dp.include_router(router)
print('bot online! prog main')

@router.message(CommandStart())
async def start_command(message: Message, check_token=None):
    token = message.text.split()[1] if len(message.text.split()) > 1 else None
    chat_id = message.chat.id
    success = check_token(token, chat_id)

    if success:
        keyboard = InlineKeyboardMarkup(row_width=2)
        button1 = InlineKeyboardButton("Отправить отзыв", callback_data="send_review")
        button2 = InlineKeyboardButton("Привязать календарь", callback_data="attach_calendar")
        keyboard.add(button1, button2)
        await message.answer("Ваш аккаунт успешно авторизован! Добро пожаловать, {user_name}!❤️\n Выберите, что вы хотите сделать👇")
    else:
        await message.answer("Неудачная авторизация. Пожалуйста, введите токен вручную:")
        token_message = await message.answer("Введите токен:")
        token = (await bot.wait_for_message(chat_id=chat_id, timeout=60)).text
        success = check_token(token, chat_id)

        if success:
            await message.answer("Успешная авторизация")
        else:
            await message.answer("Неудачная авторизация. Попробуйте еще раз.")
async def process_callback(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup(row_width=2)
    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=callback_query.message.message_id, reply_markup=keyboard)
    if callback_query.data == "send_review":
        await bot.send_message(chat_id, "Когда проходила встреча?")
        date = (await bot.wait_for_message(chat_id=chat_id, timeout=60)).text
        await bot.send_message(chat_id, "С кем проходила встреча?")
        person = (await bot.wait_for_message(chat_id=chat_id, timeout=60)).text
        await bot.send_message(chat_id, "Расскажите нам о встрече")
        description = (await bot.wait_for_message(chat_id=chat_id, timeout=60)).text
        send_review(chat_id, date, person, description)
        keyboard = InlineKeyboardMarkup(row_width=2)
        button1 = InlineKeyboardButton("Отправить отзыв", callback_data="send_review")
        button2 = InlineKeyboardButton("Привязать календарь", callback_data="attach_calendar")
        keyboard.add(button1, button2)
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=callback_query.message.message_id, reply_markup=keyboard)



    elif callback_query.data == "attach_calendar":
        await bot.send_message(chat_id, "pass")

def check_token(token, chat_id, message=None):
    SERVER_URL = "https://hack137.ru"

    response2 = requests.post(urllib.parse.urljoin(SERVER_URL, "/v1/internal/telegram/upsert"), json={
        "user": message.from_user.to_dict(),
    })

    response = requests.post(urllib.parse.urljoin(SERVER_URL, "/v1/me/telegram/account/attach"), json={
        "telegram_account_id": chat_id,
        "person_secret": token
    })

    if response.status_code == 200 and response2.status_code == 200:
        return True
    else:
        return False

def send_review(chat_id, date, person, description):
    SERVER_URL = "https://hack137.ru/"
    response = requests.post(urllib.parse.urljoin(SERVER_URL, "/v1/me/telegram/account/attach"), json={
        "telegram_account_id": chat_id,
        "date": date,
        "person": person,
        "description": description
    })
    if response.status_code == 200:
        bot.send_message(chat_id, "Отзыв успешно отправлен!")
    else:
        bot.send_message(chat_id, "Не удалось отправить отзыв. Попробуйте еще раз.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())