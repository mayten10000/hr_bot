import asyncio
import logging
import sqlite3
import openai
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

#OPENAI_API_KEY = "your_openai_api_key"
# def extract_skills_from_job(job_title):
#     prompt = f"Выдели ключевые навыки из названия вакансии: '{job_title}'. Ответ должен быть в виде списка, например: Python, Django, SQL."
#
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[{"role": "system", "content": prompt}]
#     )
#
#     skills = response["choices"][0]["message"]["content"]
#     return [skill.strip() for skill in skills.split(",") if skill.strip()] ## внедрение нейросети в код

API_TOKEN = '7854583744:AAGtrOwNm-PoIpSYY6g4BjtR53CwovflCdw'
YOUR_ADMIN_ID = 5543459759

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
storage = MemoryStorage()

logging.basicConfig(level=logging.INFO)

# логирование и инициализация бота

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/candidates")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start(message: types.Message):
    if message.from_user.id == YOUR_ADMIN_ID:
    #    await message.answer("Добро пожаловать, админ!", reply_markup=admin_keyboard())
        await message.answer("Тыкай на кнопки или добавляй/удаляй вакансии", reply_markup=admin_keyboard())

    else:
        await message.answer("Выберите вакансию", reply_markup=job_keyboard())

class JobForm(StatesGroup):
    waiting_for_job_title = State()

def init_db():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS candidates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        job_id INTEGER,
                        skills TEXT,
                        match_score INTEGER,
                        FOREIGN KEY (job_id) REFERENCES jobs (id))''')
    conn.commit()
    conn.close()
init_db()


def admin_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить вакансию", callback_data="add_job")],
        [InlineKeyboardButton(text="Удалить вакансию", callback_data="delete_job")]
    ])
    return keyboard


@dp.callback_query(F.data == "delete_job")
async def delete_job(callback: CallbackQuery):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    conn.close()

    if not jobs:
        await callback.message.answer("Нет вакансий для удаления.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=job[1], callback_data=f"del_{job[0]}")] for job in jobs
    ])

    await callback.message.answer("Выберите вакансию для удаления:", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data.startswith("del_"))
async def confirm_delete_job(callback: CallbackQuery):
    job_id = int(callback.data.split("_")[1])

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    conn.commit()
    conn.close()

    await callback.message.edit_text("Вакансия удалена!", reply_markup=admin_keyboard())
    await callback.answer()

def job_keyboard():
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    conn.close()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=job[1], callback_data=f"select_{job[0]}")] for job in jobs
    ])
    return keyboard

def skills_keyboard(remaining_skills):
    buttons = []

    for skill in remaining_skills:
        buttons.append([
            InlineKeyboardButton(text=f"{skill} +", callback_data=f"skill_{skill}_yes"),
            InlineKeyboardButton(text=f"{skill} -", callback_data=f"skill_{skill}_no")
        ])

    if not remaining_skills:
        buttons.append([InlineKeyboardButton(text="Готово", callback_data="submit_skills")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("jobs"))
async def list_jobs(message: types.Message):
    await message.answer("Выберите вакансию", reply_markup=job_keyboard())

@dp.message(Command("candidates"))
async def show_candidates(message: types.Message):
    if message.from_user.id != YOUR_ADMIN_ID:
        await message.answer("У вас нет доступа.")
        return

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, job_id, skills, match_score FROM candidates ORDER BY match_score DESC")
    candidates = cursor.fetchall()
    conn.close()

    if not candidates:
        await message.answer("Кандидатов пока нет.")
        return

    text = "Список кандидатов:\n\n"
    for name, job_id, skills, score in candidates:
        text += f"👤 {name}\n💼 Вакансия ID: {job_id}\n🛠 Навыки: {skills}\n✅ Баллы: {score}\n\n"

    await message.answer(text)


@dp.callback_query(F.data == "add_job")
async def add_job(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название вакансии:")
    await state.set_state(JobForm.waiting_for_job_title)  # Устанавливаем состояние
    await callback.answer()

@dp.message(JobForm.waiting_for_job_title)  # Ждем ввод названия вакансии
async def save_job(message: types.Message, state: FSMContext):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO jobs (title) VALUES (?)", (message.text,))
        conn.commit()
        await message.answer("Вакансия добавлена!", reply_markup=admin_keyboard())
    except sqlite3.IntegrityError:
        await message.answer("Такая вакансия уже существует.")
    finally:
        conn.close()
    await state.clear()  # Очищаем состояние


@dp.callback_query()
async def handle_callback(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("select_"):
        job_id = int(callback.data.split("_")[1])
        await state.update_data(job_id=job_id, skills={})

        # Передаем все доступные навыки
        available_skills = ["Python", "Django", "SQL", "Git"]
        await callback.message.edit_text("Отметьте свои навыки:", reply_markup=skills_keyboard(available_skills))
        await callback.answer()

    elif callback.data.startswith("skill_"):
        _, skill, response = callback.data.split("_")
        user_data = await state.get_data()
        skills = user_data.get("skills", {})

        skills[skill] = 1 if response == "yes" else 0  # Записываем выбранный навык
        await state.update_data(skills=skills)

        # Фильтруем оставшиеся навыки
        all_skills = ["Python", "Django", "SQL", "Git"]
        remaining_skills = [s for s in all_skills if s not in skills]

        if remaining_skills:  # Если остались навыки - обновляем клавиатуру
            await callback.message.edit_text("Отметьте свои навыки:", reply_markup=skills_keyboard(remaining_skills))
        else:  # Если навыков не осталось, показываем кнопку "Готово"
            await callback.message.edit_text("Все навыки отмечены. Нажмите 'Готово'.", reply_markup=skills_keyboard([]))

        await callback.answer()

    elif callback.data == "submit_skills":
        user_data = await state.get_data()
        skills_text = ", ".join(
            [f"{skill}: {'+' if val == 1 else '-'}" for skill, val in user_data.get("skills", {}).items()])
        match_score = sum(user_data.get("skills", {}).values())

        conn = sqlite3.connect("jobs.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO candidates (name, job_id, skills, match_score) VALUES (?, ?, ?, ?)",
                       (callback.from_user.full_name, user_data.get("job_id"), skills_text, match_score))
        conn.commit()
        conn.close()

        await callback.message.edit_text("Спасибо! Мы свяжемся с вами.")  # Убираем кнопки полностью
        await state.clear()
        await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
