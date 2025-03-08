from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from resources.states import AddWorkoutStates, ViewWorkoutsStates
from src.keyboards.workout_keyboards import get_type_activities_keyboard
from src.keyboards.base_keyboards import skip_keyboard, get_yes_or_no_keyboard

from src.model.workout_model import Workout
from src.model.databases import workout_dp, goals_dp
from resources.constants import TYPES_ACTIVITIES

from src.bot import waiter

import datetime

router = Router()


@router.message(StateFilter(None), Command("add_workout"))
async def add_workout_handler(message: types.Message, state: FSMContext):
    await message.answer("Выберете тип активности", reply_markup=get_type_activities_keyboard())

    await state.set_state(AddWorkoutStates.input_type)


@router.message(StateFilter(AddWorkoutStates.input_type), F.text)
async def type_activity_handler(message: types.Message, state: FSMContext):
    await state.update_data(type_activity=message.text)

    if message.text in TYPES_ACTIVITIES:
        reply_message = await message.answer("Введите дистанцию (в км)")

        await state.update_data(reply_message=reply_message)
        await state.set_state(AddWorkoutStates.input_distance)
    else:
        await message.answer("Выберете из тренировку из списка")


@router.message(StateFilter(AddWorkoutStates.input_distance), F.text)
async def distance_handler(message: types.Message, state: FSMContext):
    try:
        distance = float(message.text)
    except ValueError:
        await message.answer("Неверный формат ввода. Нужно ввести только число")
        return

    await state.update_data(distance=distance)
    await state.set_state(AddWorkoutStates.input_date)
    await message.answer("Введите дату тренировки (ГГГГ:ММ:ДД:ЧЧ:ММ)")


@router.callback_query(StateFilter(AddWorkoutStates.input_distance), F.data == "skip")
async def skip_distance_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message

    reply_message = (await state.get_data()).get("reply_message")
    await reply_message.delete_reply_markup()

    await state.set_state(AddWorkoutStates.input_date)
    await message.answer("Введите дату тренировки (ГГГГ:ММ:ДД:ЧЧ:ММ)")

    await callback.answer()


@router.message(StateFilter(AddWorkoutStates.input_date), F.text)
async def date_activity_handler(message: types.Message, state: FSMContext):
    try:
        date_format = '%Y:%m:%d:%H:%M'
        date = datetime.datetime.strptime(message.text, date_format)
    except ValueError:
        await message.answer("Неверный формат ввода! Попробуйте снова")
        return

    await state.update_data(date=date)
    await state.set_state(AddWorkoutStates.input_duration)

    await message.answer("Введите продолжительность тренировки (ЧЧ:ММ)")


@router.message(StateFilter(AddWorkoutStates.input_duration), F.text)
async def duration_handler(message: types.Message, state: FSMContext):
    try:
        date_format = '%H:%M'
        time_duration = datetime.datetime.strptime(message.text, date_format).time()
    except ValueError:
        await message.answer("Неверный формат ввода! Попробуйте снова")
        return

    await state.update_data(duration=time_duration)
    await state.set_state(AddWorkoutStates.input_calories)

    reply_message = await message.answer("Введите количество каллорий", reply_markup=skip_keyboard())
    await state.update_data(reply_message=reply_message)


@router.message(StateFilter(AddWorkoutStates.input_calories), F.text)
async def calories_handler(message: types.Message, state: FSMContext):
    try:
        calories = int(message.text)
    except ValueError:
        await message.answer("Неверный формат ввода! Нужно ввести только число")
        return

    reply_message = (await state.get_data()).get("reply_message")
    await reply_message.delete_reply_markup()

    await state.update_data(calories=calories)
    await state.set_state(AddWorkoutStates.input_description)

    reply_message = await message.answer("Добавьте описание к тренировке", reply_markup=skip_keyboard())
    await state.update_data(reply_message=reply_message)


@router.callback_query(StateFilter(AddWorkoutStates.input_calories), F.data == "skip")
async def skip_calories_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message

    reply_message = (await state.get_data()).get("reply_message")
    await reply_message.delete_reply_markup()

    await state.set_state(AddWorkoutStates.input_description)
    reply_message = await message.answer("Добавьте описание к тренировке", reply_markup=skip_keyboard())
    await state.update_data(reply_message=reply_message)

    await callback.answer()


@router.message(StateFilter(AddWorkoutStates.input_description), F.text)
async def comment_handler(message: types.Message, state: FSMContext):
    reply_message = (await state.get_data()).get("reply_message")
    await reply_message.delete_reply_markup()

    await state.update_data(description=message.text)
    await state.set_state(AddWorkoutStates.done_add_workout)

    await done_add_workout(message, state)


@router.callback_query(StateFilter(AddWorkoutStates.input_description), F.data == "skip")
async def skip_comment_handler(callback: types.CallbackQuery, state: FSMContext):
    reply_message = (await state.get_data()).get("reply_message")
    await reply_message.delete_reply_markup()

    message = callback.message
    await state.set_state(AddWorkoutStates.done_add_workout)

    await callback.answer()

    await done_add_workout(message, state)


async def done_add_workout(message: types.Message, state: FSMContext):
    data = await state.get_data()

    type_activity = data.get("type_activity")
    distance = data.get("distance")
    date_activity = data.get("date")
    duration = data.get("duration")
    calories = data.get("calories")
    description = data.get("description")

    workout = Workout(type_activity, date_activity, duration, distance, calories, description)

    time_delta = datetime.timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)

    date_ending = date_activity + time_delta

    waiter.add_time_to_wait(date_ending, goals_dp.update_goal_states, type_activity, distance)

    await state.update_data(workout=workout)

    await message.answer(str(workout))
    await message.answer("Сохранить тренировку?", reply_markup=get_yes_or_no_keyboard())


@router.callback_query(StateFilter(AddWorkoutStates.done_add_workout), F.data == "yes")
async def save_workout_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    await message.delete_reply_markup()
    await message.answer("Тренировка сохранена")

    workout = (await state.get_data()).get("workout")

    workout_dp.add_workout(message.chat.id, workout)

    await state.clear()
    await callback.answer()


@router.callback_query(StateFilter(AddWorkoutStates.done_add_workout), F.data == "no")
async def clear_workout_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    await message.delete_reply_markup()
    await message.answer("Тренировка отменена")

    await state.clear()
    await callback.answer()


@router.message(StateFilter(None), Command("view_workouts"))
async def view_workouts_handler(message: types.Message, state: FSMContext):
    reply_message = await message.answer("Введите тип тренировок", reply_markup=skip_keyboard())

    await state.update_data(reply_message=reply_message)
    await state.set_state(ViewWorkoutsStates.input_type)


@router.message(StateFilter(ViewWorkoutsStates.input_type), F.text)
async def view_type_activity_handler(message: types.Message, state: FSMContext):

    if message.text not in TYPES_ACTIVITIES:
        await message.answer("Выберете из предложенных")
        return

    type_activity = message.text

    reply_message = (await state.get_data()).get("reply_message")
    await reply_message.delete_reply_markup()

    await state.update_data(type_activity=type_activity)

    reply_message = await message.answer("Введите кол-во дней, за которые вы хотите посмотреть тренировки",
                                         reply_markup=skip_keyboard())
    await state.update_data(reply_message=reply_message)

    await state.set_state(ViewWorkoutsStates.input_period)


@router.callback_query(StateFilter(ViewWorkoutsStates.input_type), F.data == "skip")
async def skip_view_type_activity_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message

    reply_message = (await state.get_data()).get("reply_message")
    await reply_message.delete_reply_markup()

    reply_message = await message.answer("Введите кол-во дней, за которые вы хотите посмотреть тренировки",
                                         reply_markup=skip_keyboard())
    await state.update_data(reply_message=reply_message)

    await state.set_state(ViewWorkoutsStates.input_period)
    await callback.answer()


@router.message(StateFilter(ViewWorkoutsStates.input_period), F.text)
async def view_period_activity_handler(message: types.Message, state: FSMContext):
    period = message.text
    try:
        period = int(period)
    except ValueError:
        await message.answer("Нужно ввести только число дней. Попробуйте снова")
        return

    reply_message = (await state.get_data()).get("reply_message")
    await reply_message.delete_reply_markup()

    await state.update_data(period=period)
    await view_workouts(message, state)


@router.callback_query(StateFilter(ViewWorkoutsStates.input_period), F.data == "skip")
async def skip_view_period_activity_handler(callback: types.CallbackQuery, state: FSMContext):
    reply_message = (await state.get_data()).get("reply_message")
    await reply_message.delete_reply_markup()

    await view_workouts(callback.message, state)
    await callback.answer()


async def view_workouts(message: types.Message, state: FSMContext):
    data = await state.get_data()

    type_activity = data.get("type_activity")
    period = data.get("period")

    workouts = workout_dp.get_all_workouts_by_user_id(message.chat.id)

    if type_activity is not None:
        workouts = workout_dp.sort_workouts_by_type(workouts, type_activity)
    if period is not None:
        workouts = workout_dp.sort_workouts_by_period_of_time(workouts, period)

    if len(workouts) == 0:
        await message.answer("У вас пока нет тренировок")
    else:
        for workout in workouts:
            await message.answer(str(workout))

    await state.clear()
