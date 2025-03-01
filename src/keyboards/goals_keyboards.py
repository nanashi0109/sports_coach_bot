from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from resources.constants import GOALS_FOR_TYPES_ACTIVITIES


def get_goals_by_type(type_activity):
    goals = GOALS_FOR_TYPES_ACTIVITIES[type_activity]
    print(len(goals))
    builder = ReplyKeyboardBuilder()

    for goal in goals:
        builder.button(text=goal)

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
