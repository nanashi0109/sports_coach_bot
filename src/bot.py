import asyncio
from aiogram import Bot, Dispatcher
from resources.config import TOKEN
from src.tools.bot_message import BotMessage
from src.tools.time_waiter import Waiter
from handlers import start_handler, workout_handler, goal_handler, statistic_handler


async def main():

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    BotMessage.set_bot(bot)

    dp.include_routers(start_handler.router, workout_handler.router, goal_handler.router, statistic_handler.router)
    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(Waiter.wait())

    await dp.start_polling(bot)



if __name__ == "__main__":
    print("Bot start")
    Waiter.recover_waiting()
    asyncio.run(main())

print(f"Bot: {bot_messanger}")
