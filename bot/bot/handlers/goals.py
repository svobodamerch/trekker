from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import settings

router = Router()


def get_mini_app_url(path: str = "") -> str:
    """Build Mini App URL with specific route."""
    base = settings.mini_app_url.rstrip('/')
    return f"{base}{path}"


@router.message(Command("goals"))
async def cmd_goals(message: types.Message):
    """Open Mini App directly on Goals page."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎯 Мои цели",
                web_app=types.WebAppInfo(url=get_mini_app_url("/goals"))
            )
        ],
        [
            InlineKeyboardButton(
                text="➕ Новая цель",
                web_app=types.WebAppInfo(url=get_mini_app_url("/goals/new"))
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
        "Твои цели и ориентиры:",
        reply_markup=keyboard
    )
