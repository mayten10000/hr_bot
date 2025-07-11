import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from handlers import start, jobs, candidates, apply

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
    dp.include_router(start.router)
    dp.include_router(jobs.router)
    dp.include_router(apply.router)
    dp.include_router(candidates.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.info('Bot started')
    asyncio.run(main())
    
