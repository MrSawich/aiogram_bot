import os
import random
from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
import app.keyboards as kb

router = Router()
actors = dict()

def get_user_stats(user_id):
    return actors.get(user_id, ["", 0, 0, 0])

def update_user_stats(user_id, money_delta=0, energy_delta=0, points_delta=0):
    if user_id in actors:
        actors[user_id][1] += money_delta
        actors[user_id][2] += energy_delta
        actors[user_id][3] += points_delta
    else:
        actors[user_id] = ["", money_delta, energy_delta, points_delta]

def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def get_random_image():
    photo_dir = "photo"
    images = [img for img in os.listdir(photo_dir) if img.endswith(".jpg")]
    if not images:
        raise FileNotFoundError("No images found in the 'photo' directory.")
    return os.path.join(photo_dir, random.choice(images))

async def send_message_and_photo(message, text, photo_path, reply_markup=None):
    await message.answer(text)
    await message.answer_photo(FSInputFile(photo_path), reply_markup=reply_markup)

async def send_stats(callback: CallbackQuery):
    user_data = get_user_stats(callback.message.chat.id)
    await callback.message.answer(
        f"<b>Деньги:</b> <em>{user_data[1]}</em>, <b>Энергия:</b> <em>{user_data[2]}</em>, <b>Баллы:</b> <em>{user_data[3]}</em>",
        parse_mode='html'
    )

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.chat.id
    if user_id not in actors:
        actors[user_id] = [f"{message.from_user.first_name} {message.from_user.last_name}", 1000, 10, 0]
    await message.answer(f"Привет, {message.from_user.first_name}!", reply_markup=kb.main)
    print(actors)

@router.message(Command("id"))
async def my_id(message: Message):
    await message.answer(f"Ваш id: {message.from_user.id}")

@router.message(F.text == "Начать игру")
async def start(message: Message):
    prequel_txt = read_file("text/prequel.txt")
    storyline_path = "story/etap1.txt"
    if os.path.exists(storyline_path):
        with open(storyline_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            if len(lines) >= 3:
                storyline = lines[2]
            else:
                storyline = "Сюжет не найден."
    else:
        storyline = "Файл сюжета не найден."
    await message.answer(prequel_txt)
    await message.answer(storyline)
    await message.answer_photo(FSInputFile("photo/etap1.png"), reply_markup=kb.choice)

@router.message(F.text == "Правила игры")
async def rule(message: Message):
    rule_txt = read_file("text/rule.txt")
    await message.answer(rule_txt, reply_markup=kb.start)

async def handle_choice(callback: CallbackQuery, file_path, money_delta=0, energy_delta=0, points_delta=0, next_markup=None):
    user_id = callback.message.chat.id
    update_user_stats(user_id, money_delta, energy_delta, points_delta)
    stats = get_user_stats(user_id)
    etap_txt = read_file(file_path)
    await callback.message.answer(etap_txt)
    await callback.message.answer_photo(FSInputFile(get_random_image()))
    await callback.message.answer(
        f"<b>Деньги:</b> <em>{stats[1]}</em>, <b>Энергия:</b> <em>{stats[2]}</em>, <b>Баллы:</b> <em>{stats[3]}</em>",
        parse_mode='html', reply_markup=next_markup
    )
    await callback.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data == "ch1")
async def ch1(callback: CallbackQuery):
    await handle_choice(callback, "text/answer1.txt", energy_delta=+1, next_markup=kb.game_2)

@router.callback_query(F.data == "ch2")
async def ch2(callback: CallbackQuery):
    await handle_choice(callback, "text/answer2.txt", energy_delta=-1, points_delta=10, next_markup=kb.game_2)

@router.callback_query(F.data == "ch3")
async def ch3(callback: CallbackQuery):
    await handle_choice(callback, "text/answer3.txt", money_delta=-500, next_markup=kb.game_3)

@router.callback_query(F.data == "ch4")
async def ch4(callback: CallbackQuery):
    await handle_choice(callback, "text/answer4.txt", energy_delta=-1, points_delta=10, next_markup=kb.game_3)

@router.callback_query(F.data == "ch5")
async def ch5(callback: CallbackQuery):
    await handle_choice(callback, "text/answer5.txt", money_delta=150, energy_delta=-1, points_delta=10, next_markup=kb.game_4)

@router.callback_query(F.data == "ch6")
async def ch6(callback: CallbackQuery):
    await handle_choice(callback, "text/answer6.txt", money_delta=-300, next_markup=kb.game_4)

@router.callback_query(F.data == "ch7")
async def ch7(callback: CallbackQuery):
    await handle_choice(callback, "text/answer7.txt", energy_delta=-1, points_delta=20, next_markup=kb.game_5)

@router.callback_query(F.data == "ch8")
async def ch8(callback: CallbackQuery):
    await handle_choice(callback, "text/answer8.txt", money_delta=-200, energy_delta=1, points_delta=5, next_markup=kb.game_5)

@router.callback_query(F.data == "ch9")
async def ch9(callback: CallbackQuery):
    await handle_choice(callback, "text/answer9.txt", energy_delta=-2, points_delta=20, next_markup=kb.final)

@router.callback_query(F.data == "ch10")
async def ch10(callback: CallbackQuery):
    await handle_choice(callback, "text/answer10.txt", money_delta=-400, energy_delta=1, points_delta=-10, next_markup=kb.final)

@router.callback_query(F.data.startswith("game_"))
async def game(callback: CallbackQuery):
    stage_number = callback.data.split("_")[-1]
    etap_txt_path = f"story/etap{stage_number}.txt"
    if os.path.exists(etap_txt_path):
        with open(etap_txt_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            if len(lines) >= 3:
                etap_txt = lines[2]
            else:
                etap_txt = "Сюжет не найден."
    else:
        etap_txt = "Файл сюжета не найден."
    await callback.message.answer(etap_txt)
    await callback.message.answer_photo(FSInputFile(f"photo/etap{stage_number}.png"), reply_markup=kb.__dict__[f"choice{stage_number}"])

@router.callback_query(F.data == "final")
async def final(callback: CallbackQuery):
    user_id = callback.message.chat.id
    stats = get_user_stats(user_id)
    ending = determine_ending(stats)
    await callback.message.answer(ending)
    await callback.message.answer_photo(FSInputFile(get_random_image()))

def determine_ending(stats):
    points, energy, money = stats[3], stats[2], stats[1]
    if points >= 80:
        file_path = "text/ending1.txt"
    elif 60 <= points < 80 and energy >= 3:
        file_path = "text/ending2.txt"
    elif points < 60 and money >= 500:
        file_path = "text/ending3.txt"
    else:
        file_path = "text/default_ending.txt"
    return read_file(file_path)
