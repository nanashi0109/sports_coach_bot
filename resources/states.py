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
