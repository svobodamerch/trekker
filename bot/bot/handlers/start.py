from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.config import settings

router = Router()


def get_mini_app_url(path: str = "") -> str:
    """Build Mini App URL with specific route."""
    base = settings.mini_app_url.rstrip('/')
    return f"{base}{path}"


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Main entry point - shows all navigation options."""
    welcome_text = (
        "Привет.\n\n"
        "Я помогу тебе мягко наблюдать за состоянием и связывать каждый день с большими ориентирами.\n\n"
        "Можно начать с короткого Пульса на 1 минуту: настроение, энергия, тревога, инсайт и один фокус на завтра.\n\n"
        "Это ранняя тестовая версия. Приложение не является медицинской или психологической помощью."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📝 Записать Пульс",
                web_app=types.WebAppInfo(url=get_mini_app_url("/pulse"))
            )
        ],
        [
            InlineKeyboardButton(
                text="🎯 Мои цели",
                web_app=types.WebAppInfo(url=get_mini_app_url("/goals"))
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 История",
                web_app=types.WebAppInfo(url=get_mini_app_url("/history"))
            )
        ],
        [
            InlineKeyboardButton(
                text="🏠 Главная",
                web_app=types.WebAppInfo(url=get_mini_app_url("/"))
            )
        ]
    ])
    
    await message.answer(welcome_text, reply_markup=keyboard)
