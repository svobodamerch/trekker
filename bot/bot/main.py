import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import settings
from bot.handlers.start import router as start_router
from bot.handlers.pulse import router as pulse_router
from bot.handlers.goals import router as goals_router
from bot.handlers.history import router as history_router
from bot.handlers.info import router as info_router
from bot.handlers.weekly_report import router as weekly_report_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.bot_token) if settings.bot_token else None
dp = Dispatcher()

# Include routers
dp.include_router(start_router)
dp.include_router(pulse_router)
dp.include_router(goals_router)
dp.include_router(history_router)
dp.include_router(info_router)
dp.include_router(weekly_report_router)


async def main() -> None:
    if not bot:
        logging.error("BOT_TOKEN not set. Bot will not start.")
        return
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
