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
from aiogram.types import BotCommandScopeChat

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
YOUR_ADMIN_ID = {5543459759}
ADMIN = 5543459759
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
storage = MemoryStorage()

logging.basicConfig(level=logging.INFO)

# логирование и инициализация бота


from aiogram import Bot
from aiogram.types import BotCommand


async def set_default_commands(bot: Bot, user_id: int):

    user_commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="jobs", description="Список вакансий"),
        BotCommand(command="apply", description="Откликнуться на вакансию"),
        BotCommand(command="help", description="Помощь")
    ]

    admin_commands = [
        BotCommand(command="candidates", description="Список кандидатов"),
        BotCommand(command="add_job", description="Добавить вакансию"),
        BotCommand(command="delete_job", description="Удалить вакансию"),
        BotCommand(command="edit_job", description="Изменить вакансию"),
        BotCommand(command="match", description="Оценить кандидатов"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="stats", description="Статистика"),
        BotCommand(command="refresh", description="Обновить данные"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="edit_stack", description="Редактировать стек технологий")
    ]


    if user_id == ADMIN:
        commands = admin_commands
    else:
        commands = user_commands
#    commands = admin_commands if user_id == ADMIN else user_commands
    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=user_id))
def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/candidates")]
        ],
        resize_keyboard=True
    )
class UpdateStackForm(StatesGroup):
    waiting_for_stack = State()
@dp.message(Command("start"))
async def start(message: types.Message):

    user_id = message.from_user.id
    await set_default_commands(bot, user_id)

    if message.from_user.id == ADMIN:
    #    await message.answer("Добро пожаловать, админ!", reply_markup=admin_keyboard())
        await message.answer("Тыкай на кнопки или добавляй/удаляй вакансии", reply_markup=admin_keyboard())

    else:
        await message.answer("Выберите вакансию", reply_markup=job_keyboard())

class JobForm(StatesGroup):
    waiting_for_job_title = State()
    waiting_for_job_description = State()
    waiting_for_job_salary = State()
    waiting_for_job_requirements = State()


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

@dp.callback_query(F.data == "edit_technologies")
async def edit_technologies(callback: CallbackQuery):
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM jobs")
    jobs = cursor.fetchall()
    conn.close()

    if not jobs:
        await callback.message.answer("Нет вакансий для редактирования.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=job[1], callback_data=f"edit_stack_{job[0]}")] for job in jobs
    ])
    await callback.message.answer("Выберите вакансию для редактирования стека:", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_stack_"))
async def edit_stack_for_job(callback: CallbackQuery):
    job_id = int(callback.data.split("_")[2])

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, requirements FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    conn.close()

    if job:
        title, requirements = job
        text = f"📌 *{title}*\n\n📝 *Текущий стек технологий:* {requirements if requirements else 'Не указан'}"
        await callback.message.edit_text(text, parse_mode="Markdown",
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                             [InlineKeyboardButton(text="Изменить стек", callback_data=f"update_stack_{job_id}")]
                                         ]))
    else:
        await callback.message.edit_text("Вакансия не найдена.")

    await callback.answer()

@dp.callback_query(F.data.startswith("update_stack_"))
async def update_stack(callback: CallbackQuery, state: FSMContext):
    job_id = int(callback.data.split("_")[2])

    await state.update_data(job_id=job_id)
    await callback.message.answer("Введите новый стек технологий для вакансии (например, Python, Django, SQL):")
    await state.set_state(UpdateStackForm.waiting_for_stack)
    await callback.answer()

@dp.message(UpdateStackForm.waiting_for_stack)
async def update_stack_in_db(message: types.Message, state: FSMContext):
    data = await state.get_data()
    job_id = data.get("job_id")

    new_stack = message.text.strip()

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET requirements=? WHERE id=?", (new_stack, job_id))
    conn.commit()
    conn.close()

    await message.answer("Стек технологий обновлен!")
    await state.clear()
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
    cursor.execute("SELECT id, title FROM jobs")
    jobs = cursor.fetchall()
    conn.close()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=job[1], callback_data=f"select_{job[0]}")] for job in jobs
    ])
    return keyboard



@dp.message(Command("jobs"))
async def list_jobs(message: types.Message):
    await message.answer("Выберите вакансию", reply_markup=job_keyboard())

@dp.message(Command("candidates"))
async def show_candidates(message: types.Message):
    if message.from_user.id not in YOUR_ADMIN_ID:
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

@dp.message(JobForm.waiting_for_job_title)
async def save_job_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание вакансии: ")
    await state.set_state(JobForm.waiting_for_job_description)

@dp.message(JobForm.waiting_for_job_description)
async def save_job_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите зарплату (например, 100 000 руб.):")
    await state.set_state(JobForm.waiting_for_job_salary)

@dp.message(JobForm.waiting_for_job_salary)
async def save_job_salary(message: types.Message, state: FSMContext):
    await state.update_data(salary=message.text)
    await message.answer("Введите требования (например, Python, SQL, Django):")
    await state.set_state(JobForm.waiting_for_job_requirements)

@dp.message(JobForm.waiting_for_job_requirements)
async def save_job_requrements(message: types.Message, state: FSMContext):
    data = await state.get_data()

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO jobs (title, description, salary, requirements) VALUES (?, ?, ?, ?)",
                       (data["title"], data["description"], data["salary"], message.text))
        conn.commit()
        await message.answer("Вакансия добавлена!", reply_markup=admin_keyboard())
    except sqlite3.IntegrityError:
        await message.answer("Такая вакансия уже существует.")
    finally:
        conn.close()
    await state.clear()


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

@dp.callback_query(F.data.startswith("select_"))
async def show_job_details(callback: CallbackQuery):
    job_id = int(callback.data.split("_")[1])

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, salary, requirements FROM jobs WHERE id=?", (job_id,))
    job = cursor.fetchone()
    conn.close()

    if job:
        title, description, salary, requirements = job
        text = f"📌 *{title}*\n\n📝 *Описание:* {description}\n💰 *Зарплата:* {salary}\n📋 *Требования:* {requirements}"
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Откликнуться", callback_data=f"apply_{job_id}")]
        ]))
    else:
        await callback.message.edit_text("Вакансия не найдена.")

    await callback.answer()


@dp.callback_query(F.data.startswith("apply_"))
async def apply_for_job(callback: CallbackQuery, state: FSMContext):
    job_id = int(callback.data.split("_")[1])

    # Получаем стек технологий вакансии
    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, requirements FROM jobs WHERE id=?", (job_id,))
    job = cursor.fetchone()
    conn.close()

    if not job:
        await callback.message.answer("Вакансия не найдена.")
        return

    title, requirements = job
    skills_list = requirements.split(", ") if requirements else []  # Парсим стек

    if not skills_list:
        await callback.message.answer("Для этой вакансии нет требований.")
        return

    await state.update_data(job_id=job_id, skills={}, remaining_skills=skills_list)
    await callback.message.answer(f"Вы откликаетесь на вакансию *{title}*.\n\n"
                                  "Отметьте свои навыки:", parse_mode="Markdown",
                                  reply_markup=skills_keyboard(skills_list))
    await callback.answer()


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

@dp.callback_query(F.data.startswith("skill_"))
async def handle_callback(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    user_data = await state.get_data()

    if data.startswith("skill_"):
        _, skill, response = data.split("_")
        skills = user_data.get("skills", {})
        remaining_skills = user_data.get("remaining_skills", [])

        # Удаляем навык из списка оставшихся
        if skill in remaining_skills:
            remaining_skills.remove(skill)

        skills[skill] = 1 if response == "yes" else 0

        await state.update_data(skills=skills, remaining_skills=remaining_skills)

        if remaining_skills:
            await callback.message.edit_text("Отметьте свои навыки:", reply_markup=skills_keyboard(remaining_skills))
        else:
            await callback.message.edit_text("Все навыки отмечены. Нажмите 'Готово'.",
                                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                 [InlineKeyboardButton(text="Готово", callback_data="submit_skills")]
                                             ]))

    elif data == "submit_skills":
        if "job_id" not in user_data or "skills" not in user_data:
            await callback.message.answer("Произошла ошибка. Попробуйте снова.")
            return

        skills_text = ", ".join([f"{skill}: {'+' if val == 1 else '-'}" for skill, val in user_data["skills"].items()])
        match_score = sum(user_data["skills"].values())

        conn = sqlite3.connect("jobs.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO candidates (name, job_id, skills, match_score) VALUES (?, ?, ?, ?)",
                       (callback.from_user.full_name, user_data["job_id"], skills_text, match_score))
        conn.commit()
        conn.close()

        await callback.message.edit_text("Спасибо! Мы свяжемся с вами.")
        await state.clear()

    await callback.answer()


def register_handlers(dp: Dispatcher):
    dp.callback_query.register(handle_callback, F.data.startswith("skill_"))
    dp.callback_query.register(handle_callback, F.data == "submit_skills")


async def main():
    register_handlers(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
