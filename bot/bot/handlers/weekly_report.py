"""Weekly report handler for Telegram bot - uses HTTP API to backend."""
import httpx
from aiogram import Router, types
from aiogram.filters import Command
from datetime import datetime

from bot.config import settings

router = Router()

# API client
async def api_get(path: str, params: dict = None):
    """Make authenticated GET request to backend API."""
    async with httpx.AsyncClient() as client:
        headers = {}
        if settings.ai_api_key:
            headers["X-Admin-Key"] = settings.ai_api_key
        resp = await client.get(
            f"{settings.api_base_url}{path}",
            params=params,
            headers=headers,
            timeout=30.0
        )
        resp.raise_for_status()
        return resp.json()

async def api_post(path: str, json_data: dict = None):
    """Make authenticated POST request to backend API."""
    async with httpx.AsyncClient() as client:
        headers = {}
        if settings.ai_api_key:
            headers["X-Admin-Key"] = settings.ai_api_key
        resp = await client.post(
            f"{settings.api_base_url}{path}",
            json=json_data,
            headers=headers,
            timeout=120.0
        )
        resp.raise_for_status()
        return resp.json()


def format_user_report(report: dict) -> str:
    """Format user report for Telegram message."""
    week_start = report.get("week_start", "")[5:10].replace("-", ".")
    week_end = report.get("week_end", "")[:10].replace("-", ".")
    
    lines = [
        f"📊 *Отчёт за неделю* ({week_start} — {week_end})",
        "",
        f"📝 Записей: {report.get('entries_count', 0)} | Дней: {report.get('days_with_entries', 0)}/7",
    ]
    
    if report.get("avg_mood"):
        lines.append(f"😊 Настроение: {report['avg_mood']:.1f}/10")
    if report.get("avg_energy"):
        lines.append(f"⚡ Энергия: {report['avg_energy']:.1f}/10")
    if report.get("avg_anxiety"):
        lines.append(f"🌊 Тревога: {report['avg_anxiety']:.1f}/10")
    
    lines.extend([
        "",
        f"*{report.get('summary', '')}*",
        "",
        f"🌟 {report.get('highlights', '')}",
        "",
        f"💡 {report.get('patterns', '')}",
        "",
        f"🤗 {report.get('encouragement', '')}",
        "",
        f"✨ На следующую неделю:\n{report.get('suggestions', '')}",
    ])
    
    return "\n".join(lines)


def format_community_report(report: dict) -> str:
    """Format community report for Telegram message."""
    week_start = report.get("week_start", "")[5:10].replace("-", ".")
    week_end = report.get("week_end", "")[:10].replace("-", ".")
    
    lines = [
        f"📊 *Отчёт сообщества за неделю* {week_start} — {week_end}",
        "",
        f"{report.get('community_summary', '')}",
        "",
        "📈 Статистика:",
        f"• Активных участников: {report.get('active_users', 0)} из {report.get('total_users', 0)}",
        f"• Всего записей: {report.get('total_entries', 0)}",
        f"• Пульсов дня: {report.get('total_pulse_entries', 0)}",
        f"• Дневников: {report.get('total_diary_entries', 0)}",
    ]
    
    if report.get("community_avg_mood"):
        lines.append(f"• Среднее настроение: {report['community_avg_mood']:.1f}/10")
    
    lines.extend([
        "",
        f"🔄 {report.get('trends', '')}",
        "",
        f"💪 {report.get('encouragement', '')}",
        "",
        f"🎯 Челлендж на следующую неделю:\n{report.get('collective_challenge', '')}",
    ])
    
    return "\n".join(lines)


@router.message(Command("myweek"))
async def cmd_my_week(message: types.Message):
    """Get user's latest weekly report."""
    try:
        # This requires auth - user needs to call from Mini App context
        # For now, show message about where to find reports
        await message.answer(
            "📊 *Твой еженедельный отчёт*\n\n"
            "Отчёты приходят автоматически каждое воскресенье вечером.\n\n"
            "Пока можешь посмотреть свою динамику в Mini App: 👇",
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(
                        text="📱 Открыть Mini App",
                        web_app=types.WebAppInfo(url=settings.mini_app_url)
                    )]
                ]
            )
        )
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@router.message(Command("community_week"))
async def cmd_community_week(message: types.Message):
    """Get latest community weekly report."""
    try:
        report = await api_get("/weekly-reports/community/latest")
        text = format_community_report(report)
        await message.answer(text, parse_mode="Markdown")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await message.answer("📊 Общий отчёт пока не сформирован.")
        else:
            await message.answer(f"Ошибка загрузки: {e}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@router.message(Command("generate_reports"))
async def cmd_generate_reports(message: types.Message):
    """Admin command to trigger report generation."""
    # Simple admin check - compare with a configured admin ID
    # For now, just check if command is from specific user
    
    try:
        await message.answer("🤖 Генерирую отчёты... Это займёт 2-3 минуты.")
        
        result = await api_post("/weekly-reports/generate")
        
        await message.answer(
            f"✅ Генерация запущена!\n\n"
            f"Неделя: {result.get('week', {}).get('week_start')} — {result.get('week', {}).get('week_end')}\n\n"
            f"Отчёты будут отправлены автоматически."
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка генерации: {e}")


# Scheduler integration
async def send_weekly_reports_job(bot):
    """Called by scheduler every Sunday."""
    try:
        # Generate reports
        result = await api_post("/weekly-reports/generate")
        print(f"Weekly reports generated: {result}")
        
        # Reports are sent by backend automatically if configured
        # Or we can fetch and send them here
        
    except Exception as e:
        print(f"Weekly reports job failed: {e}")
