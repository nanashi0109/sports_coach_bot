from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    input_login = State()
    input_password = State()
    done_registry = State()


class LoginStates(StatesGroup):
    input_login = State()
    input_password = State()
