from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from resources.states import RegistrationStates, LoginStates
from resources import constants

from src.model import user_model
from src.model.databases import user_dp

from src.keyboards.base_keyboards import get_yes_or_no_keyboard


router = Router()


@router.message(StateFilter(None), Command("help"))
async def help_handler(message: types.Message, state: FSMContext):
    await message.answer(constants.HELP_MESSAGE)


@router.message(StateFilter(None), Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer(constants.HELLO_MESSAGE)


@router.message(StateFilter(None), Command("register"))
async def registry_handler(message: types.message, state: FSMContext):
    if is_registry(message.chat.id):
        await message.answer("Вы уже зарегестрированы!")
        return

    await message.answer("Введите логин")

    await state.set_state(RegistrationStates.input_login)


def is_registry(chat_id):
    if user_dp.get_user_by_chat_id(chat_id) is None:
        return False

    return True


@router.message(StateFilter(RegistrationStates.input_login), F.text)
async def registry_login_handler(message: types.message, state: FSMContext):
    if message.text in user_dp.get_all_logins():
        await message.answer("Введёный вами логин уже существует! Попробуйте другой")
    else:
        await message.answer("Введите пароль")

        await state.update_data(login=message.text)
        await state.set_state(RegistrationStates.input_password)


@router.message(StateFilter(RegistrationStates.input_password), F.text)
async def registry_password_handler(message: types.message, state: FSMContext):
    await message.answer("Пароль успешно сохранен!")

    await state.update_data(password=message.text)
    await state.set_state(RegistrationStates.done_registry)

    data = await state.get_data()

    await message.answer(f"Ваш логин: {data["login"]} \nВаш пароль: {data["password"]}")
    await message.answer("Сохранить?", reply_markup=get_yes_or_no_keyboard())


@router.callback_query(StateFilter(RegistrationStates.done_registry), F.data == "yes")
async def save_data_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message

    data = await state.get_data()
    user = user_model.User(data["login"], data["password"], message.chat.id)
    user_dp.add_user(user)

    await message.delete_reply_markup()
    await message.answer("Вы успешно зарегестрировались! Теперь вы можете пользоваться ботом")

    await state.clear()
    await callback.answer()


@router.callback_query(StateFilter(RegistrationStates.done_registry), F.data == "no")
async def clear_data_handler(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    await message.delete_reply_markup()
    await message.answer("Регестрация отменена")

    await state.clear()
    await callback.answer()


@router.message(StateFilter(None), Command("login"))
async def login_handler(message: types.message, state: FSMContext):
    if is_registry(message.chat.id):
        await message.answer("Вы уже авторизованы")
        return

    print(user_dp.get_all_logins())

    await message.answer("Введите логин")
    await state.set_state(LoginStates.input_login)


@router.message(StateFilter(LoginStates.input_login), F.text)
async def login_login_handler(message: types.message, state: FSMContext):
    print(message.text)
    target_user = user_dp.get_user_by_login(message.text)
    if (target_user is None) or (target_user.login != message.text):
        await message.answer("Неверный логин! Попробуйте снова")
        return

    await message.answer("Введите пароль")
    await state.update_data(user=target_user)
    await state.set_state(LoginStates.input_password)


@router.message(StateFilter(LoginStates.input_password), F.text)
async def login_password_handler(message: types.message, state: FSMContext):
    data = await state.get_data()
    target_password = data["user"].password

    if target_password != message.text:
        await message.answer("Неверный пароль! Попробуйте снова")
        return

    await message.answer("Вы успешно авторизовались! Теперь вы можете пользоваться ботом")

    await state.clear()
