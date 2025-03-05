from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from resources.states import StatisticStates
from src.keyboards.statistics_keyboards import get_type_activities_keyboard
from src.keyboards.base_keyboards import skip_keyboard

from src.model.statistic_model import Statistics
from resources.constants import TYPES_ACTIVITIES

router = Router()


@router.message(StateFilter(None), Command("statistics"))
async def get_statistic_handler(message: types.Message, state: FSMContext):
    await message.answer("Выберете тип активности", reply_markup=get_type_activities_keyboard())

    await state.set_state(StatisticStates.input_type_activity)


@router.message(StateFilter(StatisticStates.input_type_activity), F.text)
async def type_activity_handler(message: types.Message, state: FSMContext):
    print(message.text.lower())
    if message.text.lower() != "пропустить":
        await state.update_data(type_activity=message.text)

    if (message.text not in TYPES_ACTIVITIES) and (message.text.lower() != "пропустить"):
        await message.answer("Выберете тренировку из списка")
        return

    reply_message = await message.answer("Введите период времени, за который хотите просмотреть статистику",
                                         reply_markup=skip_keyboard())

    await state.update_data(reply_message=reply_message)
    await state.set_state(StatisticStates.input_period)


@router.message(StateFilter(StatisticStates.input_period), F.text)
async def statistic_period_handler(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число")
        return

    reply_message = (await state.get_data()).get("reply_message")
    await reply_message.delete_reply_markup()

    await state.update_data(period=int(message.text))
    await state.set_state(StatisticStates.done_statistic)

    await view_statistic(message, state)


@router.callback_query(StateFilter(StatisticStates.input_period), F.data == "skip")
async def statistic_skip_period_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message

    reply_message = (await state.get_data()).get("reply_message")
    await reply_message.delete_reply_markup()

    await state.set_state(StatisticStates.done_statistic)
    await callback.answer()

    await view_statistic(message, state)


async def view_statistic(message: types.Message, state: FSMContext):
    data = await state.get_data()

    user_id = message.chat.id
    type_activity = data.get("type_activity")
    period = data.get("period")

    await message.answer(f"Всего тренировок: {Statistics.get_count_training(user_id, type_activity, period)}")

    await message.answer(f"Суммарная дистанция: {Statistics.get_summary_distance(user_id, type_activity, period)}\n"
                         f"Средняя дистанция: {Statistics.get_avg_distance(user_id, type_activity, period)}")

    await message.answer(f"Суммарная продолжительность тренировок: {Statistics.get_summary_duration_training(user_id, type_activity, period)}\n"
                         f"Средняя продолжительность тренировок: {Statistics.get_avg_duration_training(user_id, type_activity, period)}")

    await message.answer(f"Суммарная потеря калорий: {Statistics.get_summary_calories_training(user_id, type_activity, period)}\n"
                         f"Средняя потеря калорий: {Statistics.get_avg_calories(user_id, type_activity, period)}")

    await state.clear()
