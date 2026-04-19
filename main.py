from aiogram import Bot, Dispatcher
import asyncio
import os
from dotenv import load_dotenv
from aiogram.filters import CommandStart
from aiogram.types import Message

load_dotenv()

token = os.getenv("API_TOKEN")

bot = Bot(token)
dp = Dispatcher()

#Приветствие бота
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(f"Привет!")

async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass