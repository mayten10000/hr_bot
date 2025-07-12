from pyexpat.errors import messages

from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from config import Config, load_config

config: Config = load_config()

# Позже, при разрастании проекта, можно навесить на условный admin_router
class IsAdmin(Filter):
    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        return obj.from_user.id in config.bot.admin_ids

