from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import settings

router = Router()


def get_mini_app_url(path: str = "") -> str:
    """Build Mini App URL with specific route."""
    base = settings.mini_app_url.rstrip('/')
    return f"{base}{path}"


@router.message(Command("history"))
async def cmd_history(message: types.Message):
    """Open Mini App on History or Analytics page."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📊 История записей",
                web_app=types.WebAppInfo(url=get_mini_app_url("/history"))
            )
        ],
        [
            InlineKeyboardButton(
                text="📈 Динамика",
                web_app=types.WebAppInfo(url=get_mini_app_url("/analytics"))
            )
        ],
        [
            InlineKeyboardButton(
                text="🏠 На главную",
                web_app=types.WebAppInfo(url=get_mini_app_url("/"))
            )
        ]
    ])
    
    await message.answer(
        "Посмотри свои записи и динамику:",
        reply_markup=keyboard
    )
