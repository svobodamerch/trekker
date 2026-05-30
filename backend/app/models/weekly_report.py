"""Weekly AI reports for users and community."""
from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class WeeklyReport(SQLModel, table=True):
    """Individual weekly AI report for a user."""
    __tablename__ = "weekly_reports"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Report period (Monday to Sunday)
    week_start: date = Field(index=True)
    week_end: date
    
    # Entry statistics
    entries_count: int = 0
    days_with_entries: int = 0
    days_missed: int = 0
    streak_at_week_end: int = 0
    
    # Average metrics
    avg_mood: Optional[float] = None
    avg_anxiety: Optional[float] = None
    avg_energy: Optional[float] = None
    
    # AI-generated content
    summary: str = ""  # Brief summary of the week
    highlights: str = ""  # Key highlights/achievements
    patterns: str = ""  # Patterns noticed
    encouragement: str = ""  # Personalized encouragement
    suggestions: str = ""  # Gentle suggestions for next week
    
    # Raw AI output for admin analysis
    raw_ai_output: Optional[str] = None
    
    # Status
    sent_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional["User"] = Relationship(back_populates="weekly_reports")


class CommunityWeeklyReport(SQLModel, table=True):
    """Community-wide weekly summary (posted to community feed)."""
    __tablename__ = "community_weekly_reports"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Report period
    week_start: date = Field(index=True, unique=True)
    week_end: date
    
    # Aggregated stats
    total_users: int = 0
    active_users: int = 0  # Users with entries
    total_entries: int = 0
    total_pulse_entries: int = 0
    total_diary_entries: int = 0
    
    # Average metrics across all users
    community_avg_mood: Optional[float] = None
    community_avg_anxiety: Optional[float] = None
    community_avg_energy: Optional[float] = None
    
    # AI-generated community content
    community_summary: str = ""  # Overall week summary
    trends: str = ""  # Trends noticed across community
    encouragement: str = ""  # Community encouragement
    collective_challenge: str = ""  # Suggested challenge for next week
    
    # Community post reference
    community_post_id: Optional[int] = Field(foreign_key="community_posts.id", default=None)
    
    # Raw data for analysis
    raw_ai_output: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    community_post: Optional["CommunityPost"] = Relationship()
