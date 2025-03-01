from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from resources.states import SetGoalStates
from src.keyboards.workout_keyboards import get_type_activities_keyboard
from src.keyboards.goals_keyboards import get_goals_by_type
from src.keyboards.base_keyboards import skip_keyboard, get_yes_or_no_keyboard

from src.model.goal_model import Goal
from src.model.databases import goals_dp

import datetime

router = Router()


@router.message(StateFilter(None), Command("set_goal"))
async def set_goal_handler(message: types.Message, state: FSMContext):
    message_keyboard = await message.answer("Введите тип тренировки", reply_markup=get_type_activities_keyboard())

    await state.update_data(message_keyboard=message_keyboard)
    await state.set_state(SetGoalStates.input_type)


@router.message(StateFilter(SetGoalStates.input_type), F.text)
async def type_goal_handler(message: types.Message, state: FSMContext):
    type_activity = message.text
    await state.update_data(type_activity=type_activity)
    try:
        await message.answer("Выберете цель", reply_markup=get_goals_by_type(type_activity))
    except KeyError:
        await message.answer("Выберете из предложенных")
        return

    (await state.get_data()).get("message_keyboard").delete_reply_markup()
    await state.set_state(SetGoalStates.input_header)


@router.message(StateFilter(SetGoalStates.input_header), F.text)
async def goal_header_handler(message: types.Message, state: FSMContext):
    await state.update_data(goal_header=message.text)

    await message.answer("Введите значение для цели (только число)")

    await state.set_state(SetGoalStates.input_stats)


@router.message(StateFilter(SetGoalStates.input_stats), F.text)
async def goal_stats_handler(message: types.Message, state: FSMContext):
    try:
        await state.update_data(target_stats=int(message.text))
    except ValueError:
        await message.answer("Введите число!")
        return

    await message.answer("Введите срок для завершения цели (ГГГГ:ММ:ДД)")

    await state.set_state(SetGoalStates.input_deadline)


@router.message(StateFilter(SetGoalStates.input_deadline), F.text)
async def goal_deadline_handler(message: types.Message, state: FSMContext):
    try:
        date_format = '%Y:%m:%d'
        date = datetime.datetime.strptime(message.text, date_format).date()
    except ValueError:
        await message.answer("Неверный формат ввода! Попробуйте снова")
        return

    message_keyboard = await message.answer("Добавьте описание для цели", reply_markup=skip_keyboard())
    await state.update_data(message_keyboard=message_keyboard)

    await state.update_data(deadline=date)
    await state.set_state(SetGoalStates.input_description)


@router.message(StateFilter(SetGoalStates.input_description), F.text)
async def goal_description_handler(message: types.Message, state: FSMContext):
    (await state.get_data()).get("message_keyboard").delete_reply_markup()

    await state.update_data(description=message.text)
    await state.set_state(SetGoalStates.done_add_goal)

    await done_add_goal(message, state)


@router.callback_query(StateFilter(SetGoalStates.input_description), F.data == "skip")
async def skip_description_handler(callback: types.CallbackQuery, state: FSMContext):
    (await state.get_data()).get("message_keyboard").delete_reply_markup()

    message = callback.message
    await state.set_state(SetGoalStates.done_add_goal)

    await callback.answer()

    await done_add_goal(message, state)


async def done_add_goal(message: types.Message, state: FSMContext):
    data = await state.get_data()

    goal_header = data.get("goal_header")
    type_activity = data.get("type_activity")
    target_state = data.get("target_stats")
    description = data.get("description")
    deadline = data.get("deadline")

    goal = Goal(goal_header=goal_header, type_activity=type_activity, target_stat=target_state, deadline=deadline, description=description)

    await message.answer(str(goal))

    await message.answer("Сохранить цель?", reply_markup=get_yes_or_no_keyboard())
    await state.update_data(goal=goal)


@router.callback_query(StateFilter(SetGoalStates.done_add_goal), F.data == "yes")
async def save_goal_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    await message.delete_reply_markup()
    await message.answer("Цель сохранена")

    goal = (await state.get_data()).get("goal")

    goals_dp.add_goal(message.chat.id, goal)

    await state.clear()
    await callback.answer()


@router.callback_query(StateFilter(SetGoalStates.done_add_goal), F.data == "no")
async def clear_goal_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    await message.delete_reply_markup()
    await message.answer("Цель отменена")

    await state.clear()
    await callback.answer()
