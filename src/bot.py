import asyncio
from aiogram import Bot, Dispatcher
from resources.config import TOKEN
from handlers import start_handler, workout_handler, goal_handler


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_routers(start_handler.router, workout_handler.router, goal_handler.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
