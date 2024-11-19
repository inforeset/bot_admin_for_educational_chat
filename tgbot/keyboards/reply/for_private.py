from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard() -> ReplyKeyboardMarkup:

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    button_1 = KeyboardButton(text='Команды для чата: инструкция')
    button_2 = KeyboardButton(text='Полезные ссылки для написания бота')

    keyboard.add(button_1, button_2)

    return keyboard
