import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import settings
from bot.handlers import start, pulse, goals, history, info, weekly_report
from bot.scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.bot_token) if settings.bot_token else None
dp = Dispatcher()

# Include routers
dp.include_router(start.router)
dp.include_router(pulse.router)
dp.include_router(goals.router)
dp.include_router(history.router)
dp.include_router(info.router)
dp.include_router(weekly_report.router)


async def main() -> None:
    if not bot:
        logging.error("BOT_TOKEN not set. Bot will not start.")
        return
    
    # Setup scheduler for weekly reports
    setup_scheduler(bot)
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
