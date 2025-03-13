from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    input_login = State()
    input_password = State()
    done_registry = State()


class LoginStates(StatesGroup):
    input_login = State()
    input_password = State()


class AddWorkoutStates(StatesGroup):
    input_type = State()
    input_date = State()
    input_duration = State()
    input_distance = State()
    input_calories = State()
    input_description = State()
    done_add_workout = State()


class ViewWorkoutsStates(StatesGroup):
    input_type = State()
    input_period = State()


class SetGoalStates(StatesGroup):
    input_type = State()
    input_header = State()
    input_stats = State()
    input_description = State()
    input_deadline = State()
    done_add_goal = State()


class StatisticStates(StatesGroup):
    input_type_activity = State()
    input_period = State()
    done_statistic = State()


class ReminderStates(StatesGroup):
    input_datetime = State()
    input_repeating = State()
    done_add_remind = State()
