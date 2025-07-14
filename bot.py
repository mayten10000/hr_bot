import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from handlers.apply import router as router_apply
from handlers.candidates import router as router_candidates
from handlers.jobs import router as router_jobs
from handlers.start import router as router_start
from handlers.job_form import router as router_job_form
from handlers.key_word_query_form import router as router_search
from keyboards.inline import router as router_keyboard

from config import Config, load_config
import logging

config: Config = load_config()

logging.basicConfig(
    level=logging.getLevelName(level=config.log.level),
    format=config.log.format
)

async def main():
    bot = Bot(token=config.bot.token)
    dp = Dispatcher(storage=MemoryStorage()) # Заменить позже на RedisStorage

    dp.include_router(router_apply)
    dp.include_router(router_candidates)
    dp.include_router(router_jobs)
    dp.include_router(router_start)
    dp.include_router(router_job_form)
    dp.include_router(router_search)
    dp.include_router(router_keyboard)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.info('Bot started')
    asyncio.run(main())
    
