import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from . import main_router
from states import JobForm

from config import Config, load_config
import logging

config: Config = load_config()

logging.basicConfig(
    level=logging.getLevelName(level=config.log.level),
    format=config.log.format
)

async def main():
    bot = Bot(token=config.bot.token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(main_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.info('Bot started')
    asyncio.run(main())
    
