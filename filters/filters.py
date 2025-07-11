from aiogram.filters import Filter
from aiogram.types import Message
from config import Config, load_config

config: Config = load_config()

# Позже, при разрастании проекта, можно навесить на условный admin_router
class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in config.bot.admin_ids
