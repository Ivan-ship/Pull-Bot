from aiogram import Bot, Dispatcher
import asyncio
import os
from dotenv import load_dotenv
from handlers.start import router


load_dotenv()

token = os.getenv("API_TOKEN")

bot = Bot(token)
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass