from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session

from app.models import User, UserSettings, ReminderLog
from app.config import settings


class ReminderService:
    def __init__(self, db: Session):
        self.db = db

    def get_pending_reminders(self) -> List[User]:
        """Get users who need a reminder now."""
        now = datetime.utcnow()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")

        # Find users with reminders enabled for current time
        users = (
            self.db.query(User)
            .join(UserSettings)
            .filter(
                UserSettings.reminder_enabled == True,
                UserSettings.reminder_time == current_time,
            )
            .all()
        )

        # Filter out users who already got reminder today
        pending = []
        for user in users:
            already_sent = (
                self.db.query(ReminderLog)
                .filter(
                    ReminderLog.user_id == user.id,
                    ReminderLog.reminder_date == current_date,
                )
                .first()
            )
            if not already_sent:
                pending.append(user)

        return pending

    def mark_reminder_sent(self, user_id: int):
        """Mark reminder as sent for today."""
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        log = ReminderLog(
            user_id=user_id,
            reminder_date=current_date,
        )
        self.db.add(log)
        self.db.commit()
