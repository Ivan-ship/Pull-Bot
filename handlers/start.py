import asyncio
import os
from aiogram.filters import CommandStart
from aiogram.types import Message
import aiohttp
from aiogram import Router
from dotenv import load_dotenv
from buttons import main_kb
from aiogram.fsm.context import FSMContext
from states import TestState
from aiohttp import ClientSession
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

load_dotenv()

router = Router()
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
API_BASE = os.getenv("API_BASE")

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


#Список тестов
@router.message(lambda m: m.text == "Пройти опрос")
async def show_tests(message: Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE}/tests") as resp:
            tests = await resp.json()
        
        kb = []
        for test in tests:
            kb.append([KeyboardButton(text=f"{test['test_id']}:{test['title']}")])
        markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

        await state.set_state(TestState.choosing_test)
        await message.answer("Выберите опрос: ", reply_markup=markup)

#Выбор теста
@router.message(TestState.choosing_test)
async def select_test(message: Message, state: FSMContext):
    try:
        test_id = int(message.text.split(":")[0])
    except:
        await message.answer("выберите тест!")
        return
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE}/tests/{test_id}") as resp:
            test = await resp.json()
    
    await state.update_data(
        test_id=test_id,
        questions=test["questions"],
        current_q = 0,
        answers=[]
    )

    await state.set_state(TestState.passing_test)
    await send_question(message, state)

#отправка вопросов
async def send_question(message: Message, state: FSMContext):
    data = await state.get_data()

    if data["current_q"] >= len(data["questions"]):
        await message.answer("Тест завершён!")
        return

    q = data["questions"][data["current_q"]]

    kb = InlineKeyboardMarkup(
        inline_keyboard = [
            [
                InlineKeyboardButton(
                    text = ans["text"],
                    callback_data=f"ans:{q['question_id']}:{ans['answer_id']}"
                )
            ]
            for ans in q['answers']
        ]
    )
    await message.answer(q["text"], reply_markup=kb)


#Обработчик кнопки
@router.callback_query(lambda c: c.data.startswith("ans:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    _, question_id, answer_id = callback.data.split(":")

    data = await state.get_data()

    answers = data["answers"]
    answers.append({
        "question_id": int(question_id),
        "answer_id": int(answer_id)
    })

    await state.update_data(
        answers = answers,
        current_q = data["current_q"] + 1
    )

    await callback.answer("Ответ принят!")
    await send_question(callback.message, state)