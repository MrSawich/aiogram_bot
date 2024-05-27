from aiogram.types import  (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                            InlineKeyboardButton, KeyboardButton)

main = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text="Правила игры"),
                 KeyboardButton(text="Начать игру")]],
                 resize_keyboard=True,  one_time_keyboard=True)

start = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Начать игру"),]], resize_keyboard=True, one_time_keyboard=True)

admin = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text="Загрузить сюжет"),
                 KeyboardButton(text="Сгенерировать изображения"),
                 KeyboardButton(text="Удалить изображения"),
                 KeyboardButton(text="Правила загрузки")]],
                 resize_keyboard=True)



choice = InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text="1 Вариант", callback_data="ch1")],
                [InlineKeyboardButton(text="2 вариант", callback_data="ch2")]])

choice2 = InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text="1 Вариант", callback_data="ch3")],
                [InlineKeyboardButton(text="2 вариант", callback_data="ch4")]])

choice3 = InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text="1 Вариант", callback_data="ch5")],
                [InlineKeyboardButton(text="2 вариант", callback_data="ch6")]])

choice4 = InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text="1 Вариант", callback_data="ch7")],
                [InlineKeyboardButton(text="2 вариант", callback_data="ch8")]])

choice5 = InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text="1 Вариант", callback_data="ch9")],
                [InlineKeyboardButton(text="2 вариант", callback_data="ch10")]])

game_2 = InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text="Далее", callback_data="game_2")]])

game_3 = InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text="Далее", callback_data="game_3")]])

game_4 = InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text="Далее", callback_data="game_4")]])

game_5 = InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text="Далее", callback_data="game_5")]])

final = InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text="Завершить игру", callback_data="final")]])