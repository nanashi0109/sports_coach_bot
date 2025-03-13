from aiogram.utils.keyboard import ReplyKeyboardBuilder
from resources.constants import TYPES_REPEATING_REMINDER


def get_type_reminder_repeating_keyboard():
    builder = ReplyKeyboardBuilder()

    for type_r in TYPES_REPEATING_REMINDER:
        builder.button(text=type_r)

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)