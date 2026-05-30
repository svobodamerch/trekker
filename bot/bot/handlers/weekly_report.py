"""Weekly report handler for Telegram bot."""
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.orm import Session
from datetime import date

from bot.database import get_db_session
from bot.config import get_mini_app_url
from app.services.weekly_report_service import WeeklyReportService
from app.models import WeeklyReport, CommunityWeeklyReport, User, CommunityPost

router = Router()


@router.message(Command("myweek"))
async def cmd_my_week(message: types.Message):
    """Get user's latest weekly report."""
    db: Session = get_db_session()
    try:
        # Find user by telegram_id
        user = db.query(User).filter(User.telegram_user_id == str(message.from_user.id)).first()
        if not user:
            await message.answer("Сначала нужно зарегистрироваться через Mini App.")
            return
        
        # Get latest report
        report = db.query(WeeklyReport).filter(
            WeeklyReport.user_id == user.id,
        ).order_by(WeeklyReport.week_start.desc()).first()
        
        if not report:
            await message.answer(
                "📊 *Отчётов пока нет*\n\n"
                "Начни записывать Пульс дня — первый отчёт появится в конце недели.",
                parse_mode="Markdown"
            )
            return
        
        # Format report
        service = WeeklyReportService(db)
        text = service.format_user_report_for_bot(report)
        
        await message.answer(text, parse_mode="Markdown")
        
    finally:
        db.close()


@router.message(Command("community_week"))
async def cmd_community_week(message: types.Message):
    """Get latest community weekly report."""
    db: Session = get_db_session()
    try:
        report = db.query(CommunityWeeklyReport).order_by(
            CommunityWeeklyReport.week_start.desc()
        ).first()
        
        if not report:
            await message.answer("📊 Общий отчёт пока не сформирован.")
            return
        
        service = WeeklyReportService(db)
        title, body = service.format_community_report_for_post(report)
        
        text = f"*{title}*\n\n{body}"
        
        await message.answer(text, parse_mode="Markdown")
        
    finally:
        db.close()


async def send_weekly_reports_to_all_users(bot):
    """Send weekly reports to all users (called by scheduler)."""
    db: Session = get_db_session()
    try:
        service = WeeklyReportService(db)
        week_start, week_end = service.get_week_boundaries()
        
        # Ensure reports are generated
        community_report = await service.generate_all_reports()
        
        # Post community report to community feed
        if community_report:
            await post_community_report_to_feed(db, community_report)
        
        # Get all unsent individual reports for this week
        reports = db.query(WeeklyReport).filter(
            WeeklyReport.week_start == week_start,
            WeeklyReport.sent_at.is_(None),
        ).all()
        
        sent_count = 0
        for report in reports:
            try:
                # Get user's telegram_id
                user = db.query(User).filter(User.id == report.user_id).first()
                if not user:
                    continue
                
                # Format and send
                text = service.format_user_report_for_bot(report)
                
                await bot.send_message(
                    chat_id=user.telegram_user_id,
                    text=text,
                    parse_mode="Markdown",
                )
                
                # Mark as sent
                report.sent_at = datetime.utcnow()
                sent_count += 1
                
            except Exception as e:
                print(f"Failed to send report to user {report.user_id}: {e}")
        
        db.commit()
        print(f"Sent {sent_count} weekly reports")
        
    finally:
        db.close()


async def post_community_report_to_feed(db: Session, report: CommunityWeeklyReport):
    """Post community weekly report to community feed."""
    from app.api.routes.community import create_community_post_internal
    
    service = WeeklyReportService(db)
    title, body = service.format_community_report_for_post(report)
    
    # Create as system post (no specific user)
    try:
        post = CommunityPost(
            user_id=None,  # System post
            title=title,
            body=body,
            visibility="named",  # Everyone can see
            is_weekly_report=True,
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        
        # Link report to post
        report.community_post_id = post.id
        db.commit()
        
        print(f"Posted community weekly report as post {post.id}")
        
    except Exception as e:
        print(f"Failed to post community report: {e}")


@router.message(Command("generate_reports"))
async def cmd_generate_reports(message: types.Message):
    """Admin command to trigger report generation."""
    # TODO: Add admin check
    db: Session = get_db_session()
    try:
        service = WeeklyReportService(db)
        
        # Run generation
        await message.answer("🤖 Генерирую отчёты... Это может занять несколько минут.")
        
        community_report = await service.generate_all_reports()
        
        # Post to community
        await post_community_report_to_feed(db, community_report)
        
        await message.answer(
            f"✅ Отчёты сгенерированы!\n\n"
            f"Период: {community_report.week_start.strftime('%d.%m')} — {community_report.week_end.strftime('%d.%m')}\n"
            f"Активных пользователей: {community_report.active_users}\n"
            f"Всего записей: {community_report.total_entries}"
        )
        
    finally:
        db.close()
