import os
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = '7037566831:AAHsoFZo0sEAaEnUWcWL8CZkMWZQCPnuEVo'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# Создаем папку "story" если она не существует
if not os.path.exists('story'):
    os.makedirs('story')

@router.message(Command(commands=['start']))
async def send_start(message: types.Message):
    help_text = (
        "Я могу помочь вам с следующими командами:\n"
        "/start - Начать общение со мной\n"
        "/help - Получить список доступных команд\n"
        "Отправьте мне .txt файл, и я сохраню его."
    )
    await message.answer(help_text)

@router.message(F.document)
async def handle_docs(message: types.Message):
    document = message.document
    if document.mime_type == 'text/plain':
        file_id = document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path
        downloaded_file = await bot.download_file(file_path)

        file_name = document.file_name
        save_path = os.path.join('story', file_name)

        with open(save_path, 'wb') as new_file:
            new_file.write(downloaded_file.read())

        await message.answer(f"Файл '{file_name}' успешно сохранен в папку 'story'.")
    else:
        await message.answer("Пожалуйста, отправьте файл с расширением .txt.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
