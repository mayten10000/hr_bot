import asyncio
import logging
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN
from aiogram import Bot, Dispatcher
from handlers import start, jobs, candidates, apply

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start.router)
    dp.include_router(jobs.router)
    dp.include_router(apply.router)
    dp.include_router(candidates.router)

    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
