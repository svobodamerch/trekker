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
        "Это приложение для мягкого самонаблюдения в Telegram.\n\n"
        "Здесь можно:\n"
        "• за 1 минуту записывать Пульс дня\n"
        "• видеть динамику настроения, энергии и тревоги\n"
        "• формулировать цели и «жизнь мечты»\n"
        "• делать срез баланса жизни\n"
        "• получать мягкие недельные отражения\n"
        "• оставлять обратную связь и следить за развитием mini app\n\n"
        "С чего начать:\n"
        "1. Нажми «Открыть приложение»\n"
        "2. Сделай первый Пульс\n"
        "3. Если захочешь — добавь цель или срез баланса жизни\n\n"
        "Это ранняя тестовая версия. Приложение не является медицинской или психологической помощью."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📝 Открыть приложение",
                web_app=types.WebAppInfo(url=get_mini_app_url("/"))
            )
        ],
        [
            InlineKeyboardButton(
                text="❓ Как пользоваться",
                callback_data="show_help"
            )
        ],
        [
            InlineKeyboardButton(
                text="🆕 Что нового",
                callback_data="show_updates"
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 Обратная связь",
                callback_data="show_feedback"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎯 Пульс дня",
                web_app=types.WebAppInfo(url=get_mini_app_url("/pulse"))
            )
        ],
        [
            InlineKeyboardButton(
                text="� Цели и жизнь мечты",
                web_app=types.WebAppInfo(url=get_mini_app_url("/goals"))
            )
        ]
    ])
    
    await message.answer(welcome_text, reply_markup=keyboard)
