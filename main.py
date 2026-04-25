from aiogram import Bot, Dispatcher
import asyncio
import os
from dotenv import load_dotenv
from aiogram.filters import CommandStart
from aiogram.types import Message
import aiohttp
from aiogram import Router

load_dotenv()

token = os.getenv("API_TOKEN")

bot = Bot(token)
dp = Dispatcher()

router = Router()
API_URL = os.getenv("API_URL")

#Приветствие бота
@router.message(CommandStart())
async def command_start_handler(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json = {
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name
            },
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:

                #Проверка статуса
                if resp.status != 200:
                    text = await resp.text()
                    await message.answer("Ошибка на сервере при регистрации!")
                    print(f"API error {resp.status}: {text}")
                    return
                
                try:
                    result = await resp.json()
                except Exception:
                    await message.answer("Ошибка ответа сервера!")
                    return
        await message.answer("Приветствуем в приложении Test+")
    
    except asyncio.TimeoutError:
        await message.answer("Сервер не отвечает")
    except aiohttp.ClientError as e:
        await message.answer("Нет соединения с сервером!")
        print(f"ClientError {e}")
    except Exception as e:
        await message.answer("Неизвестная ошибка!")
        print(f"Неизвестная ошибка! {e}")

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass