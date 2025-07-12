from aiogram import Router, types, F
from aiogram.filters import Command
from database.queries import get_all_jobs, user_exists
from keyboards.inline import admin_keyboard, job_keyboard
from utils.commands import set_default_commands
from config import Config, load_config
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database.queries import set_user_role, get_user_role
from enums.roles import UserRole

router = Router()

role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="HR")],
        [KeyboardButton(text="Кандидат")],
    ],
    resize_keyboard=True
)

config: Config = load_config()

@router.message(Command("start"))
async def start_handler(message: Message):
    await set_default_commands(message.bot, message.from_user.id)
    telegram_id = message.from_user.id
    role = get_user_role(telegram_id)
    username = message.from_user.username
    full_name = message.from_user.full_name

    if telegram_id in config.bot.admin_ids:
        set_user_role(telegram_id, UserRole.ADMIN.value, username, full_name)
        await message.answer("Ты админ!", reply_markup=admin_keyboard())
        return

    if not role:
        await message.answer("Кто ты?", reply_markup=role_keyboard)
        return

    role_str = UserRole(role)
    jobs = get_all_jobs()
    if role_str == UserRole.HR:
        await message.answer("Привет, HR. Возможности пока ограничены")
    elif role_str == UserRole.CANDIDATE:
        await message.answer("Привет, кандидат. Тыкай, что интересно", reply_markup=job_keyboard(jobs))


@router.message(F.text.in_(["HR", "Кандидат"]))
async def role_choose_handler(message: Message):

    telegram_id = message.from_user.id
    if user_exists(telegram_id):
        await message.answer("Ты уже зарегистрирован. Нажми /start.", reply_markup=ReplyKeyboardRemove())
        return

    role = UserRole.HR.value if message.text == "HR" else UserRole.CANDIDATE.value
    set_user_role(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        role=role
    )
    await message.answer(f"ты зарегистрирован как {role}, нажми на /start", reply_markup=ReplyKeyboardRemove(role_keyboard))