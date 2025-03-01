from aiogram.utils.keyboard import ReplyKeyboardBuilder
from resources.constants import TYPES_ACTIVITIES


def get_type_activities_keyboard():
    builder = ReplyKeyboardBuilder()

    for type_w in TYPES_ACTIVITIES:
        builder.button(text=type_w)

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)





