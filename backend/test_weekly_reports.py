#!/usr/bin/env python3
"""Test script for weekly reports system."""
import asyncio
import sys
sys.path.insert(0, '/Users/svoboda.site/Documents/Svoboda.site/trekker/backend')

from datetime import datetime, timedelta, date
from sqlmodel import Session, select
from app.models import (
    User, Entry, WeeklyReport, CommunityWeeklyReport, 
    CommunityPost, CommunityComment
)
from app.database import engine
from app.services.weekly_report_service import WeeklyReportService
from app.config import settings


def create_test_data():
    """Create test user and entries."""
    print("\n📦 Создаём тестовые данные...")
    
    with Session(engine) as session:
        # Create test user
        user = session.exec(select(User).where(User.telegram_user_id == "123456789")).first()
        if not user:
            user = User(
                telegram_user_id="123456789",
                username="test_user",
                first_name="Test",
                language_code="ru"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"   ✅ Создан пользователь: {user.username} (ID: {user.id})")
        else:
            print(f"   ℹ️ Пользователь уже существует: {user.username}")
        
        # Create entries for last week
        today = date.today()
        week_start = today - timedelta(days=today.weekday() + 7)  # Last Monday
        
        for i in range(5):  # 5 entries
            entry_date = week_start + timedelta(days=i)
            existing = session.exec(
                select(Entry).where(
                    Entry.user_id == user.id,
                    Entry.date == entry_date
                )
            ).first()
            
            if not existing:
                entry = Entry(
                    user_id=user.id,
                    date=entry_date,
                    mood=7 + (i % 3),  # 7, 8, 9, 7, 8
                    anxiety=5 - (i % 3),  # 5, 4, 3, 5, 4
                    energy=6 + (i % 2),  # 6, 7, 6, 7, 6
                    notes=f"Тестовая запись за {entry_date}. Сегодня был хороший день!"
                )
                session.add(entry)
        
        session.commit()
        print(f"   ✅ Создано/обновлено записей за прошлую неделю")
        
        return user.id


async def test_generate_reports():
    """Test report generation."""
    print("\n🤖 Тестируем генерацию отчётов...")
    
    with Session(engine) as session:
        service = WeeklyReportService(session)
        
        # Test week boundaries
        week_start, week_end = service.get_week_boundaries()
        print(f"   📅 Текущая неделя: {week_start} — {week_end}")
        
        # Generate reports (without sending to Telegram)
        print("   ⏳ Генерируем отчёты (это может занять 30-60 сек)...")
        
        try:
            community_report = await service.generate_all_reports(
                target_date=None,
                send_via_telegram=False  # Don't send real messages during test
            )
            
            if community_report:
                print(f"   ✅ Общий отчёт создан (ID: {community_report.id})")
                print(f"      Активных пользователей: {community_report.active_users}")
                print(f"      Всего записей: {community_report.total_entries}")
            
            # Check individual reports
            user_reports = session.exec(select(WeeklyReport)).all()
            print(f"   ✅ Создано личных отчётов: {len(user_reports)}")
            
            for report in user_reports[:2]:  # Show first 2
                print(f"\n   📊 Отчёт пользователя {report.user_id}:")
                print(f"      Записей: {report.entries_count}")
                print(f"      Настроение: {report.avg_mood:.1f}/10")
                print(f"      Сводка: {report.summary[:60]}...")
            
            # Check community post
            community_posts = session.exec(
                select(CommunityPost).where(CommunityPost.is_weekly_report == True)
            ).all()
            print(f"\n   ✅ Постов в сообществе: {len(community_posts)}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False


def check_environment():
    """Check if required environment variables are set."""
    print("\n🔍 Проверка окружения:")
    
    missing = []
    
    if settings.ai_api_key in ['', 'sk-ant-api03-your-key-here']:
        missing.append("AI_API_KEY (Claude API)")
        print("   ⚠️  AI_API_KEY: не настроен")
    else:
        print(f"   ✅ AI_API_KEY: настроен ({settings.ai_api_key[:15]}...)")
    
    if settings.bot_token in ['', 'your-bot-token-here', 'your-telegram-bot-token-from-botfather']:
        missing.append("BOT_TOKEN (Telegram)")
        print("   ⚠️  BOT_TOKEN: не настроен (нужен для отправки сообщений)")
    else:
        print(f"   ✅ BOT_TOKEN: настроен")
    
    if missing:
        print(f"\n   ⚠️  Отсутствуют переменные: {', '.join(missing)}")
        print("   💡 Тест можно запустить без них, но AI-анализ и отправка работать не будут")
        return False
    
    return True


async def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🧪 ТЕСТИРОВАНИЕ ЕЖЕНЕДЕЛЬНЫХ ОТЧЁТОВ                    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    env_ok = check_environment()
    
    # Create test data
    user_id = create_test_data()
    
    if env_ok:
        # Generate reports
        success = await test_generate_reports()
        
        if success:
            print("\n✅ Тест успешно пройден!")
            print("\n📋 Что дальше:")
            print("   1. Настроить реальный AI_API_KEY для генерации отчётов")
            print("   2. Настроить BOT_TOKEN для отправки в Telegram")
            print("   3. Запустить бэкенд: cd backend && python -m uvicorn app.main:app --reload")
            print("   4. Запустить бота: cd bot && python -m bot.main")
            print("   5. В воскресенье в 18:00 отчёты придут автоматически")
        else:
            print("\n❌ Тест не пройден. Проверьте ошибки выше.")
    else:
        print("\n⚠️  Тест пропущен - не настроены API ключи.")
        print("   Заполните backend/.env и запустите тест снова.")


if __name__ == "__main__":
    asyncio.run(main())
