from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
from typing import List


def wrong_button(temp_str: str):
    """
    Generate a wrong answer button that is not equal to the correct answer.
    :param temp_str: str, correct answer of the captcha
    :return: InlineKeyboardButton with a wrong answer
    """
    correct_answer = int(temp_str)
    while True:
        key = random.randint(0, (abs(correct_answer) + 1))
        if key != correct_answer:
            break

    w_b = InlineKeyboardButton(
        text=f'{key}', callback_data=f"answer_button:{key}"
    )
    return w_b



def gen_captcha_keys(temp: int) -> List[InlineKeyboardButton]:
    """
     Take answer, generate object buttons, return list of object: "KeyboardButton"
    param temp: int answer of the captcha
    return: list of "KeyboardButton" with answer
    """
    temp_str: str = str(temp)
    numbers_wrong_button: int = 3
    first_button: InlineKeyboardButton = InlineKeyboardButton(
        text=temp_str, callback_data=f"answer_button:{temp_str}")

    out_list = [first_button, *[wrong_button(temp_str) for _ in range(numbers_wrong_button)]]
    random.shuffle(out_list)
    return out_list


def gen_captcha_button_builder(temp: int) -> InlineKeyboardMarkup:
    """trow int, add buttons, return object:"ReplyKeyboardMarkup"
       param temp: int answer of the captcha
       return object:ReplyKeyboardMarkup"""
    captcha_builder: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=1)
    captcha_buttons: list = gen_captcha_keys(temp)
    for i in range(len(captcha_buttons)):
        captcha_builder.add(captcha_buttons[i])
    keyboard_captcha: InlineKeyboardMarkup = captcha_builder
    return keyboard_captcha


if __name__ == '__main__':
    pass
