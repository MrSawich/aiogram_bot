import os
from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import app.keyboards as kb

# Загрузка переменных из .env файла
load_dotenv()

# Получение списка администраторов
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS').split(',')))

router = Router()


async def cmd_admin(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет прав администратора.")
        return
    await message.answer("Вы авторизованы как администратор", reply_markup=kb.admin)


async def download_story(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет прав администратора.")
        return
    await message.answer("Отправьте мне .txt файл, и я сохраню его.")


async def handle_txt_file(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет прав администратора.")
        return

    document = message.document
    if document.mime_type != 'text/plain':
        await message.answer("Пожалуйста, отправьте текстовый файл с расширением .txt.")
        return

    file_info = await message.bot.get_file(document.file_id)
    downloaded_file = await message.bot.download_file(file_info.file_path)

    # Чтение содержимого файла
    content = downloaded_file.getvalue().decode('utf-8').splitlines()

    if len(content) < 3:
        await message.answer("Файл должен содержать как минимум три строки.")
        return

    query1, query2, storyline = content[0], content[1], content[2]

    # Сохранение текста в папку story
    if not os.path.exists('story'):
        os.makedirs('story')

    file_path = os.path.join('story', f"{document.file_name}")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))

    await message.answer(f"Файл '{document.file_name}' успешно сохранен в папку 'story'.")
    await message.answer(
        f"<b>Первый запрос</b>: {query1}\n"
        f"<b>Второй запрос</b>: {query2}\n"
        f"<b>Текст сюжета</b>: {storyline}",
        parse_mode="HTML"
    )


router.message.register(cmd_admin, Command("admin"))
router.message.register(download_story, F.text == "Загрузить сюжет")
router.message.register(handle_txt_file, F.document.mime_type == "text/plain")
