from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def skip_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="Пропустить", callback_data="skip")

    return builder.as_markup()


def get_yes_or_no_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="yes")
    builder.button(text="Нет", callback_data="no")
    return builder.as_markup()
