from aiogram import Router, types
from aiogram.filters import Command
from config import YOUR_ADMIN_ID
from database.queries import get_all_candidates

router = Router()

@router.message(Command("candidates"))
async def show_candidates(message: types.Message):
    if message.from_user.id not in YOUR_ADMIN_ID:
        await message.answer("У вас нет доступа.")
        return

    candidates = get_all_candidates()
    ...
