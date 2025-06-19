from aiogram.types import BotCommand, BotCommandScopeChat
from config import ADMIN_ID

async def set_default_commands(bot, user_id: int):
    user_commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="jobs", description="Список вакансий"),
        BotCommand(command="apply", description="Откликнуться на вакансию"),
        BotCommand(command="help", description="Помощь")
    ]

    admin_commands = [
        BotCommand(command="candidates", description="Список кандидатов"),
        BotCommand(command="delete_job", description="Удалить вакансию"),
        BotCommand(command="delete_candidate_", description="Удалить кандидата")
    ]

    commands = admin_commands if user_id == ADMIN_ID else user_commands
    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=user_id))
