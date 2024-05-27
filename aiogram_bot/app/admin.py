import os
import shutil
import requests
import json
import time
import base64
from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
import app.keyboards as kb

# Загрузка переменных из .env файла
load_dotenv()
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS').split(',')))

router = Router()

# Класс состояния для FSM
class GenImageStates(StatesGroup):
    waiting_for_zapros = State()
    waiting_for_etap = State()
    waiting_for_image_count = State()
    waiting_for_clear_confirmation = State()
    waiting_for_additional_gen = State()

# Функции для генерации изображений
class Text2ImageAPI:
    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        return response.json()[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {"query": prompt}
        }
        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        return response.json()['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']
            attempts -= 1
            time.sleep(delay)

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def clear_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

def get_next_file_number(directory, prefix):
    existing_files = [f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith(".jpg")]
    numeric_files = [int(f.split('_')[1].split('.')[0]) for f in existing_files if f.split('_')[1].split('.')[0].isdigit()]
    return max(numeric_files, default=0) + 1

async def gen(prompt, dirr="photo", etap="Etap 1", image_name_prefix="v", num_images=1, progress_callback=None):
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/',
                        '3E522E54EB474C0AA97156C5021EFE00',
                        'E7A5EE1FCBB86DCBC49DE04EABC06AAE')
    model_id = api.get_model()
    etap_dir = ensure_directory_exists(os.path.join(dirr, f"Etap {etap}"))

    for i in range(num_images):
        uuid = api.generate(prompt, model_id)
        images = api.check_generation(uuid)

        image_base64 = images[0]
        image_data = base64.b64decode(image_base64)

        next_file_number = get_next_file_number(etap_dir, image_name_prefix)
        save_path = os.path.join(etap_dir, f"{image_name_prefix}_{next_file_number}.jpg")

        with open(save_path, "wb") as file:
            file.write(image_data)
        
        if progress_callback:
            await progress_callback(i + 1, num_images)

# Команды для бота
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

async def ask_additional_gen(message: Message, state: FSMContext):
    await state.set_state(GenImageStates.waiting_for_additional_gen)
    await message.answer("Сгенерировать ещё изображения? (да/нет)")

async def handle_additional_gen(message: Message, state: FSMContext):
    if message.text.lower() in ['да', 'yes', 'y']:
        await message.answer("Введите количество дополнительных изображений для генерации:")
        await state.set_state(GenImageStates.waiting_for_image_count)
    else:
        await message.answer("Генерация завершена!")
        await state.clear()

async def gen_image(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет прав администратора.")
        return
    await state.set_state(GenImageStates.waiting_for_zapros)
    await message.answer("Введите запрос для генерации изображения:")

async def del_image(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет прав администратора.")
        return
    await state.set_state(GenImageStates.waiting_for_etap)
    await message.answer("Введите номер этапа, изображения которого нужно удалить:")

async def get_zapros(message: Message, state: FSMContext):
    await state.update_data(zapros=message.text)
    await state.set_state(GenImageStates.waiting_for_etap)
    await message.answer("Введите номер этапа игры:")

async def get_etap(message: Message, state: FSMContext):
    await state.update_data(etap=message.text)
    user_data = await state.get_data()
    dir_path = f"photo/Etap {user_data['etap']}"

    if os.path.exists(dir_path) and os.listdir(dir_path):
        await state.set_state(GenImageStates.waiting_for_clear_confirmation)
        await message.answer(f"В папке {dir_path} уже есть изображения. Очистить папку перед генерацией? (да/нет)")
    else:
        await state.set_state(GenImageStates.waiting_for_image_count)
        await message.answer("Введите количество изображений для генерации:")

async def clear_confirmation(message: Message, state: FSMContext):
    if message.text.lower() in ['да', 'yes', 'y']:
        user_data = await state.get_data()
        dir_path = f"photo/Etap {user_data['etap']}"
        clear_directory(dir_path)
        await message.answer(f"Папка {dir_path} очищена.")
    await state.set_state(GenImageStates.waiting_for_image_count)
    await message.answer("Введите количество изображений для генерации:")

async def get_image_count(message: Message, state: FSMContext):
    try:
        image_count = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число.")
        return

    user_data = await state.get_data()
    zapros = user_data.get('zapros')
    etap = user_data.get('etap')

    async def progress_callback(current, total):
        await message.answer(f"{current}/{total} изображений сгенерировано")

    await gen(zapros, dirr="photo", etap=etap, num_images=image_count, progress_callback=progress_callback)

    await ask_additional_gen(message, state)

async def handle_txt_file(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У вас нет прав администратора.")
        return

    document = message.document
    if document.mime_type != 'text/plain':
        await message.answer("Пожалуйста, отправьте текстовый файл с расширением .txt.")
        return

    file_info = await message.bot.get_file(document.file_id)
    downloaded_file = await message.bot.download_file(file_info.file_path)
    content = downloaded_file.getvalue().decode('utf-8').splitlines()

    if len(content) < 3:
        await message.answer("Файл должен содержать как минимум три строки.")
        return

    query1, query2, storyline = content[0], content[1], content[2]
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

    etap_number = ''.join(filter(str.isdigit, document.file_name))

    async def progress_callback(current, total):
        await message.answer(f"{current}/{total} изображений сгенерировано")

    await gen(query1, dirr="photo", etap=etap_number, image_name_prefix=f"v1_{etap_number}", num_images=1, progress_callback=progress_callback)
    await message.answer(f"Изображение по первому запросу сгенерировано в папку 'Etap {etap_number}' под именем 'v1_{etap_number}.jpg'.")

    await gen(query2, dirr="photo", etap=etap_number, image_name_prefix=f"v2_{etap_number}", num_images=1, progress_callback=progress_callback)
    await message.answer(f"Изображение по второму запросу сгенерировано в папку 'Etap {etap_number}' под именем 'v2_{etap_number}.jpg'.")

    await ask_additional_gen(message, state)

# Регистрация команд
router.message.register(cmd_admin, Command("admin"))
router.message.register(download_story, F.text == "Загрузить сюжет")
router.message.register(gen_image, F.text == "Сгенерировать изображения")
router.message.register(del_image, F.text == "Удалить изображения")
router.message.register(get_zapros, GenImageStates.waiting_for_zapros)
router.message.register(get_etap, GenImageStates.waiting_for_etap)
router.message.register(clear_confirmation, GenImageStates.waiting_for_clear_confirmation)
router.message.register(get_image_count, GenImageStates.waiting_for_image_count)
router.message.register(handle_additional_gen, GenImageStates.waiting_for_additional_gen)
router.message.register(handle_txt_file, F.document.mime_type == "text/plain")
