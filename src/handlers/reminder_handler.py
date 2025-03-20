from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from resources.states import ReminderStates
from resources.constants import DATETIME_FORMAT, TYPES_REPEATING_REMINDER, WORKOUT_REMINDER_TEXT, NEED_REGISTRY_TEXT

from src.model.databases import reminder_dp
from src.model.reminder_model import ReminderModel, ReminderRepeating, ReminderController
from src.keyboards.reminder_keyboard import get_type_reminder_repeating_keyboard
from src.keyboards.base_keyboards import get_yes_or_no_keyboard

from src.handlers.start_handler import is_registry

import datetime


router = Router()


@router.message(StateFilter(None), Command("set_reminder"))
async def add_reminder_handler(message: types.Message, state: FSMContext):
    if not is_registry(message.chat.id):
        await message.answer(NEED_REGISTRY_TEXT)
        return

    await message.answer("Введите дату и время напоминания (ГГГГ:ММ:ДД:ЧЧ:ММ)")

    await state.set_state(ReminderStates.input_datetime)


@router.message(StateFilter(ReminderStates.input_datetime), F.text)
async def date_reminder_handler(message: types.Message, state: FSMContext):
    try:
        date_remind = datetime.datetime.strptime(message.text, DATETIME_FORMAT)
    except ValueError:
        await message.answer("Неверный формат ввода. Попробуйте снова")
        return

    await message.answer("Выберете, когда повторять напоминание", reply_markup=get_type_reminder_repeating_keyboard())

    await state.update_data(date=date_remind)
    await state.set_state(ReminderStates.input_repeating)


@router.message(StateFilter(ReminderStates.input_repeating), F.text)
async def repeating_reminder_handler(message: types.Message, state: FSMContext):
    if message.text not in TYPES_REPEATING_REMINDER:
        await message.answer("Выберете из списка")
        return

    for type_i in range(0, len(TYPES_REPEATING_REMINDER), 1):
        print("3")
        if TYPES_REPEATING_REMINDER[type_i].lower() == message.text.lower():
            print("4")
            await state.update_data(repeat=ReminderRepeating(type_i))
            break

    await state.set_state(ReminderStates.done_add_remind)

    await done_adding_reminder(message, state)


async def done_adding_reminder(message: types.Message, state: FSMContext):
    data = await state.get_data()

    date = data.get("date")
    repeat = data.get("repeat")

    reminder = ReminderModel(time_remind=date, repeating=repeat, description=WORKOUT_REMINDER_TEXT)
    await state.update_data(reminder=reminder)

    await message.answer(str(reminder))
    await message.answer("Сохранить напоминание?", reply_markup=get_yes_or_no_keyboard())


@router.callback_query(StateFilter(ReminderStates.done_add_remind), F.data == "yes")
async def save_reminder_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    await message.delete_reply_markup()
    await message.answer("Напоминание сохранено")

    reminder = (await state.get_data()).get("reminder")

    ReminderController.add_reminder(message.chat.id, reminder)

    await state.clear()
    await callback.answer()


@router.callback_query(StateFilter(ReminderStates.done_add_remind), F.data == "no")
async def clear_reminder_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    await message.delete_reply_markup()
    await message.answer("Напоминание отменено")

    await state.clear()
    await callback.answer()


@router.message(StateFilter(None), Command("view_reminders"))
async def view_reminders_handler(message: types.Message, state: FSMContext):
    if not is_registry(message.chat.id):
        await message.answer(NEED_REGISTRY_TEXT)
        return

    reminders = reminder_dp.get_all_user_reminder_by_user_id(message.chat.id)

    if len(reminders) == 0:
        await message.answer("У вас не напоминаний")

    for reminder in reminders:
        await message.answer(str(reminder))


@router.message(StateFilter(None), Command("remove_reminder"))
async def remove_reminder_handler(message: types.Message, state: FSMContext):
    if not is_registry(message.chat.id):
        await message.answer(NEED_REGISTRY_TEXT)
        return

    await message.answer("Введите уникальный номер напоминание (-1 для отмены)")
    await state.set_state(ReminderStates.remove_reminder)


@router.message(StateFilter(ReminderStates.remove_reminder), F.text)
async def id_reminder_handler(message: types.Message, state: FSMContext):
    try:
        reminder_id = int(message.text)
    except ValueError:
        await message.answer("Введите число")
        return

    if reminder_id == -1:
        await message.answer("Действие отменено")
        await state.clear()
        return

    reminder_dp.remove_by_id_and_user_id(reminder_id, message.chat.id)
    await state.clear()
