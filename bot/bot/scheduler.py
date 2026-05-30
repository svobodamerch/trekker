"""Scheduler for automated weekly reports."""
import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from aiogram import Bot

logger = logging.getLogger(__name__)

scheduler: AsyncIOScheduler = None


def setup_scheduler(bot: Bot):
    """Initialize and start the scheduler."""
    global scheduler
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    # Schedule weekly reports: every Sunday at 18:00 MSK
    scheduler.add_job(
        send_weekly_reports_job,
        trigger=CronTrigger(day_of_week="sun", hour=18, minute=0),
        id="weekly_reports",
        name="Send weekly AI reports to all users",
        replace_existing=True,
        kwargs={"bot": bot},
    )
    
    # Schedule community report post: every Sunday at 19:00 MSK
    scheduler.add_job(
        post_community_report_job,
        trigger=CronTrigger(day_of_week="sun", hour=19, minute=0),
        id="community_weekly_report",
        name="Post community weekly report",
        replace_existing=True,
        kwargs={"bot": bot},
    )
    
    scheduler.start()
    logger.info("Scheduler started. Weekly reports scheduled for Sundays at 18:00 MSK")
    
    return scheduler


async def send_weekly_reports_job(bot: Bot):
    """Job to send individual weekly reports to all users."""
    from bot.handlers.weekly_report import send_weekly_reports_to_all_users
    
    logger.info("Starting weekly report generation and distribution...")
    try:
        await send_weekly_reports_to_all_users(bot)
        logger.info("Weekly reports job completed")
    except Exception as e:
        logger.error(f"Weekly reports job failed: {e}")


async def post_community_report_job(bot: Bot):
    """Job to post community weekly report to feed."""
    from bot.handlers.weekly_report import post_community_report_to_feed
    from app.services.weekly_report_service import WeeklyReportService
    from bot.database import get_db_session
    
    logger.info("Posting community weekly report...")
    try:
        db = get_db_session()
        try:
            service = WeeklyReportService(db)
            _, week_end = service.get_week_boundaries()
            
            # Get latest community report
            from app.models import CommunityWeeklyReport
            report = db.query(CommunityWeeklyReport).filter(
                CommunityWeeklyReport.week_end == week_end
            ).first()
            
            if report:
                await post_community_report_to_feed(db, report)
                logger.info("Community report posted successfully")
            else:
                logger.warning("No community report found for this week")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Community report job failed: {e}")


def get_next_run_time() -> datetime:
    """Get next scheduled run time for weekly reports."""
    if scheduler:
        job = scheduler.get_job("weekly_reports")
        if job:
            return job.next_run_time
    return None
