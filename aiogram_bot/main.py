import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers import router as handlers_router
from app.admin import router as admin_router
from dotenv import load_dotenv
import os
load_dotenv()

API_TOKEN = os.getenv('BOT_API_TOKEN')

if not API_TOKEN:
    raise ValueError("No API token provided")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(handlers_router)
dp.include_router(admin_router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
