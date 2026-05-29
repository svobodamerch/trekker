from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import settings

router = Router()


def get_mini_app_url(path: str = "") -> str:
    """Build Mini App URL with specific route."""
    base = settings.mini_app_url.rstrip('/')
    return f"{base}{path}"


@router.message(Command("pulse"))
async def cmd_pulse(message: types.Message):
    """Open Mini App directly on Pulse entry page."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📝 Записать Пульс",
                web_app=types.WebAppInfo(url=get_mini_app_url("/pulse"))
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
        "Открой Mini App для записи Пульса:",
        reply_markup=keyboard
    )
