import aiogram
import requests
import asyncio
import urllib.parse
import logging
from aiogram import Router, types, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton



logging.basicConfig(filename='c137bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
bot = aiogram.Bot(token='6767096954:AAEc0HuoQA5e9nrLf9f9NBW5LvY-gM1EO5o')
dp = aiogram.Dispatcher(bot=bot)
router = Router()
dp.include_router(router)
print('\n\nbot online! prog test')


@router.message(Command('start'))
async def start_command(message: Message, command: Command):
    token = command.args[0] if command.args else None
    chat_id = message.chat.id
    user_name = message.from_user.full_name
    logging.info(f"{user_name} ({chat_id}) start bot. Personal token: {token}")
    if token:
        success = await attach_token(chat_id, token, message)
        if success:
            await message.answer("Успешная авторизация!")
            logging.info(f"{user_name} ({chat_id}) success auth. Personal token: {token}")
        else:
            await message.answer("Повторите попытку")
    else:
        await message.answer("Не удалось получить токен")
        logging.info(f"{user_name} ({chat_id}) error auth.")

async def attach_token(chat_id, token, message: Message):
    SERVER_URL = "https://hack137.ru:3001"

    try:
        response2 = requests.post(urllib.parse.urljoin(SERVER_URL, "/v1/internal/telegram/upsert"), json={
            "user": message.from_user.model_dump()
        })

        response1 = requests.post(urllib.parse.urljoin(SERVER_URL, "/v1/me/telegram/account/attach"), json={
            "telegram_account_id": chat_id,
            "person_secret": token
        })

        print(response2.text)
        return response1.status_code == 200 or 201 and response2.status_code == 200 or 201
    except Exception as e:
        print(f"\nError attaching token: {e}")
        logging.error(f" {chat_id}Error attaching token: {e}")
        return False

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
