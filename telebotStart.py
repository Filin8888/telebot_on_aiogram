from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import asyncio
from aiogram.types import FSInputFile
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import random
import os
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv 
load_dotenv()


TOKEN = os.getenv("TOKEN")#"8250251901:AAGlvgMXLOya2m_RUAHdUtMjVeXky0CI9v0"
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")


bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())



#Клас зі станами
class OrderState(StatesGroup):
    waiting_for_order = State()

# /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привіт!", reply_markup=reply_km)
    await message.answer("Ось мої кнопки", reply_markup=inline_km)

# /help
@dp.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer("Список команд:\n/start — почати роботу з ботом\n/help — допомога")


# Сайт
@dp.message(F.text == "Сайт")
async def site_hendler(message: types.Message):
    inline_btn = InlineKeyboardButton(text="Відкрити сайт", url="https://github.com/Filin8888")
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[[inline_btn]])
    await message.answer("Ось мій сайт", reply_markup=inline_kb)


# Профіль користувача
@dp.message(F.text == "Мій профіль")
async def profile_handler(message: types.Message):
    user_id = message.from_user.id
    user_firstname = message.from_user.first_name
    user_nikname = message.from_user.username
    await message.answer(
        f"Ваш ID: {user_id} \nВаше ім'я: {user_firstname} \nВаш нік: @{user_nikname if user_nikname else '404 Not Found'}"
    )



# Рандомна фотка
@dp.message(F.text == "Хочу чогось веселого")
async def Veselo_handler(message: types.Message):
    photo = random.choice(all_photos)

    #internet photo
    if photo.startswith("http"):
        await message.answer_photo(photo, caption="PАНДОМНА ФОТКА!!!")
    #local photo
    else:
        file = FSInputFile(photo)
        await message.answer_photo(file, caption="PАНДОМНА ФОТКА!!!")



#Zamowlenia 
@dp.message(F.text == "Зробити замовлення")
async def order_handler(message: types.Message, state: FSMContext):
    # await message.answer("handler")
    await message.answer("Напишіть своє замовлення текстом")
    await state.set_state(OrderState.waiting_for_order)



@dp.message(OrderState.waiting_for_order, F.text)
async def save_order_handler(message: types.Message, state: FSMContext):
    with open("orders.txt", "a", encoding="utf-8") as f:
        f.write(f"{message.from_user.id}: {message.text}\n")
    
    await message.answer("Ваше замовлення прийнято ✅")
    await state.clear()


#Gra z userom
@dp.message(F.text == "Гра")
async def gra_handler(message: types.Message):
    r_key = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Почали!")], 
        [KeyboardButton(text="Назад")]
    ])
    await message.answer("Давай пограємо! \nПравила гри: \n1.Я загадав число від 1 до 10 \n2. Ти відгадуєш", reply_markup=r_key)

@dp.message(F.text == "Назад")
async def back_handler(message: types.Message):
    await message.answer("Ти повернувся у головне меню", reply_markup=reply_km)



game_data = {}

@dp.message(F.text == "Почали!")
async def play_handler(message: types.Message):
    x = random.randint(1, 10)
    user_id = message.from_user.id
    game_data[user_id] = x
    await message.answer("Я загадав число! Спробуй вгадати ;)")

@dp.message(lambda m: m.text.isdigit())
async def start_game(message: types.Message):
    user_id = message.from_user.id
    if user_id not in game_data:
        return
    
    try:
        guess = int(message.text)
    except ValueError:
        await message.answer("Введи ціле число від 1 до 10!")
        return
    
    x = game_data[user_id]
    if guess == x:
        await message.answer("Правильно! Ти вгадав!")
        del game_data[user_id]
    else:
        await message.answer(f"НІ! Я загадав {x}. Спробуємо ще раз?")
        del game_data[user_id]

    
# Reply button
reply_km = ReplyKeyboardMarkup(
    keyboard=[
    [KeyboardButton(text="Про мене"), KeyboardButton(text="Сайт")], 
    [KeyboardButton(text="Мій профіль"), KeyboardButton(text="Гра")], 
    [KeyboardButton(text="Хочу чогось веселого")], [KeyboardButton(text="Зробити замовлення")]
    ], 
    resize_keyboard=True
)


#inline button
inline_km = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Привіт", callback_data="Hello")], 
        [InlineKeyboardButton(text="Поки", callback_data="Bye")]
    ]
)


#photo filtr
def get_valid_photo(folder, max_size=10*1024*1024):
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if os.path.getsize(os.path.join(folder, f)) <= max_size
    ]


#Here photos is
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
photos_dir = os.path.join(BASE_DIR, "photos")
local_photos = get_valid_photo(photos_dir)

internet_photos = [
    "https://images.unsplash.com/photo-1507149833265-60c372daea22", 
    "https://images.unsplash.com/photo-1521747116042-5a810fda9664", 
    "https://images.unsplash.com/photo-1501594907352-04cda38ebc29", 
    "https://images.unsplash.com/photo-1505678261036-a3fcc5e884ee", 
    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee", 
    "https://images.unsplash.com/photo-1495567720989-cebdbdd97913", 
]


all_photos = internet_photos + local_photos

























async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


