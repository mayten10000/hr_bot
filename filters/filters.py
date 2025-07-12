from aiogram.filters import Filter, BaseFilter
from config import Config, load_config
from aiogram.types import Message
from enums.roles import UserRole
from handlers import start
from database.queries import get_user_role
config: Config = load_config()

# Позже, при разрастании проекта, можно навесить на условный admin_router
class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in config.bot.admin_ids


class UserRoleFilter(BaseFilter):
    def __init__(self, *roles: UserRole):
        if not roles:
            raise ValueError("At least one role must be specified")
        self.roles = roles

    async def __call__(self, message: Message) -> bool:
        telegram_id = message.from_user.id
        role_str = get_user_role(telegram_id)
        if not role_str:
            return False
        try:
            role = UserRole(role_str)
        except ValueError:
            return False
        return role in self.roles