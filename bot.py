import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from handlers.apply import router as router_apply
from handlers.candidates import router as router_candidates
from handlers.jobs import router as router_jobs
from handlers.start import router as router_start
from handlers.job_form import router as router_job_form

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

    dp.include_router(router_apply)
    dp.include_router(router_candidates)
    dp.include_router(router_jobs)
    dp.include_router(router_start)
    dp.include_router(router_job_form)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.info('Bot started')
    asyncio.run(main())
    
