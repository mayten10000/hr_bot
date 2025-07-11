from aiogram import Router, types
from aiogram.filters import Command
from database.queries import get_all_jobs

from keyboards.inline import admin_keyboard, job_keyboard
from utils.commands import set_default_commands

from config import Config, load_config

router = Router()

config: Config = load_config()

@router.message(Command("start"))
async def start_cmd(message: types.Message):
    await set_default_commands(message.bot, message.from_user.id)

    if message.from_user.id in config.bot.admin_ids:
        await message.answer("Тыкай на кнопки или добавляй/удаляй вакансии", reply_markup=admin_keyboard())
    else:
        jobs = get_all_jobs()
        await message.answer("Выберите вакансию:", reply_markup=job_keyboard(jobs))

