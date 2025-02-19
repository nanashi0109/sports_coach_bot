from aiogram.fsm.state import StatesGroup, State


class RegistrationState:
    input_login = State()
    input_password = State()

