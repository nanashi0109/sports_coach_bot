from aiogram import Bot
import asyncio


class BotMessage:
    __bot: Bot = None

    @classmethod
    def send_message(cls, chat_id: int, message: str):
        asyncio.create_task(cls.async_sending(chat_id, message))

    @classmethod
    async def async_sending(cls, chat_id: int, message: str):
        await cls.__bot.send_message(chat_id, message)

    @classmethod
    def set_bot(cls, bot: Bot):
        cls.__bot = bot
