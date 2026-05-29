#!/usr/bin/env python3
"""
Admin script to delete a user by telegram_user_id.
Usage: python delete_user.py <telegram_user_id>
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import (
    User, Entry, Goal, GoalVersion, AIAnalysis, 
    EntryGoalLink, ReminderLog, VoiceNote, UserSettings
)


def delete_user_by_telegram_id(telegram_user_id: str, db: Session):
    """Delete user and all associated data."""
    
    # Find user
    user = db.query(User).filter(User.telegram_user_id == telegram_user_id).first()
    if not user:
        print(f"User {telegram_user_id} not found")
        return False
    
    user_id = user.id
    print(f"Found user {user_id} (telegram: {telegram_user_id})")
    
    # Count data before deletion
    stats = {
        "entries": db.query(Entry).filter(Entry.user_id == user_id).count(),
        "goals": db.query(Goal).filter(Goal.user_id == user_id).count(),
        "analyses": db.query(AIAnalysis).filter(AIAnalysis.user_id == user_id).count(),
    }
    
    print(f"Will delete: {stats['entries']} entries, {stats['goals']} goals, {stats['analyses']} analyses")
    
    # Delete in correct order (respect foreign keys)
    # 1. Delete entry-goal links
    entry_ids = [e.id for e in db.query(Entry).filter(Entry.user_id == user_id).all()]
    if entry_ids:
        db.query(EntryGoalLink).filter(EntryGoalLink.entry_id.in_(entry_ids)).delete(synchronize_session=False)
        print(f"Deleted entry-goal links")
    
    # 2. Delete goal versions
    goal_ids = [g.id for g in db.query(Goal).filter(Goal.user_id == user_id).all()]
    if goal_ids:
        db.query(GoalVersion).filter(GoalVersion.goal_id.in_(goal_ids)).delete(synchronize_session=False)
        print(f"Deleted goal versions")
    
    # 3. Delete analyses
    db.query(AIAnalysis).filter(AIAnalysis.user_id == user_id).delete(synchronize_session=False)
    
    # 4. Delete voice notes
    db.query(VoiceNote).filter(VoiceNote.user_id == user_id).delete(synchronize_session=False)
    
    # 5. Delete reminder logs
    db.query(ReminderLog).filter(ReminderLog.user_id == user_id).delete(synchronize_session=False)
    
    # 6. Delete entries
    db.query(Entry).filter(Entry.user_id == user_id).delete(synchronize_session=False)
    
    # 7. Delete goals
    db.query(Goal).filter(Goal.user_id == user_id).delete(synchronize_session=False)
    
    # 8. Delete user settings
    db.query(UserSettings).filter(UserSettings.user_id == user_id).delete(synchronize_session=False)
    
    # 9. Delete user
    db.delete(user)
    
    # Commit
    db.commit()
    print(f"Successfully deleted user {telegram_user_id} and all associated data")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python delete_user.py <telegram_user_id>")
        print("Example: python delete_user.py 123456789")
        sys.exit(1)
    
    telegram_user_id = sys.argv[1]
    
    db = SessionLocal()
    try:
        success = delete_user_by_telegram_id(telegram_user_id, db)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()
