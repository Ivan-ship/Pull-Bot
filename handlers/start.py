import asyncio
import os
from aiogram.filters import CommandStart
from aiogram.types import Message
import aiohttp
from aiogram import Router
from dotenv import load_dotenv
from buttons import main_kb

load_dotenv()

router = Router()
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

#Приветствие бота
@router.message(CommandStart())
async def command_start_handler(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    headers = {
        "x-api-key": API_KEY
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json = {
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name
            },
                headers = headers,
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
        await message.answer("Приветствуем в приложении Test+", reply_markup=main_kb)
    
    except asyncio.TimeoutError:
        await message.answer("Сервер не отвечает")
    except aiohttp.ClientError as e:
        await message.answer("Нет соединения с сервером!")
        print(f"ClientError {e}")
    except Exception as e:
        await message.answer("Неизвестная ошибка!")
        print(f"Неизвестная ошибка! {e}")

