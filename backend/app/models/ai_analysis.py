from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON


class AIAnalysis(SQLModel, table=True):
    """AI analysis of user entries and patterns."""
    __tablename__ = "ai_analyses"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Source of analysis
    source_type: str = Field(default="pulse")  # pulse, goal, life_balance, combined
    source_ids: List[int] = Field(default=[], sa_column=Column(JSON))
    
    # Analysis content
    analysis_type: str = Field(default="summary")  # summary, patterns, insights, recommendations
    content: str  # The actual AI-generated analysis
    
    # Metadata
    model_used: str = Field(default="claude-3-haiku-20240307")
    tokens_used: Optional[int] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="ai_analyses")


class AIAnalysisRequest(SQLModel, table=True):
    """Queue for AI analysis requests."""
    __tablename__ = "ai_analysis_requests"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    request_type: str = Field(default="pulse_analysis")
    status: str = Field(default="pending")  # pending, processing, completed, failed
    
    # Input data
    source_type: str
    source_ids: List[int] = Field(default=[], sa_column=Column(JSON))
    
    # Result
    result_id: Optional[int] = Field(foreign_key="ai_analyses.id", default=None)
    error_message: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
