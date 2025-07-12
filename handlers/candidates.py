from aiogram import Router, types
from aiogram.filters import Command
from database.queries import get_all_candidates

from config import Config, load_config

config: Config = load_config()

router = Router()

@router.message(Command("candidates"))
async def show_candidates(message: types.Message):
    if message.from_user.id not in config.bot.admin_ids:
        await message.answer("У вас нет доступа.")
        return

    candidates = get_all_candidates()
    # ...




