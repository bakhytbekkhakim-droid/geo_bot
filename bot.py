import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# БҰЛ ЖЕРГЕ ӨЗ ТОКЕНІҢІЗДІ ҚОЙЫҢЫЗ
API_TOKEN = 'СІЗДІҢ_ТОКЕНІҢІЗ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Сұрақтар базасы (Сіз берген 30 сұрақтың үлгісі)
QUIZ_DATA = [
    {"id": 1, "q": "«География» терминін алғаш рет енгізген кім?", "options": ["Аристотель", "Эратосфен", "Птолемей", "Страбон"], "correct": 1, "page": "6-бет"},
    {"id": 2, "q": "«Географияның екінші тілі» деп нені атайды?", "options": ["Глоссарий", "Карта", "Оқулық", "Саяхатшылар"], "correct": 1, "page": "7-бет"},
    # Басқа сұрақтарды осы жерге қосыңыз...
]

# Пайдаланушылардың сессиясын сақтау (мектеп деңгейі үшін маңызды)
user_sessions = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Сәлем, {message.from_user.first_name}! 🌍\nГеография тестін бастау үшін /test командасын жібер.")

@dp.message(Command("test"))
async def start_quiz(message: types.Message):
    # Кездейсоқ 10 сұрақ таңдау
    random_questions = random.sample(QUIZ_DATA, min(len(QUIZ_DATA), 10))
    user_sessions[message.from_user.id] = {"questions": random_questions, "score": 0, "current": 0}
    await send_next_question(message)

async def send_next_question(message):
    user_id = message.from_user.id
    data = user_sessions[user_id]
    
    if data["current"] < len(data["questions"]):
        q = data["questions"][data["current"]]
        buttons = [[types.InlineKeyboardButton(text=opt, callback_data=f"ans_{i}")] for i, opt in enumerate(q["options"])]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(f"❓ {data['current']+1}-сұрақ:\n{q['q']}", reply_markup=keyboard)
    else:
        await message.answer(f"🏁 Тест аяқталды! Сенің нәтижең: {data['score']}/10")

@dp.callback_query(F.data.startswith("ans_"))
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    ans_idx = int(callback.data.split("_")[1])
    data = user_sessions[user_id]
    q = data["questions"][data["current"]]
    
    if ans_idx == q["correct"]:
        data["score"] += 1
        await callback.message.answer("✅ Дұрыс!")
    else:
        await callback.message.answer(f"❌ Қате. Дұрыс жауабы: {q['options'][q['correct']]}\n📖 {q['page']} қараңыз.")
    
    data["current"] += 1
    await send_next_question(callback.message)
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())