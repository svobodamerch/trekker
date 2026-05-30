from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.models import User, Entry
from app.api.routes import entries, auth, goals, reminders, weekly_reflection, feedback, life_balance, voice, community

app = FastAPI(title="Self-Observation API", version="0.1.0")
app.include_router(entries.router)
app.include_router(auth.router)
app.include_router(goals.router)
app.include_router(reminders.router)
app.include_router(weekly_reflection.router)
app.include_router(feedback.router)
app.include_router(life_balance.router)
app.include_router(voice.router)
app.include_router(community.router)

from app.config import settings

# CORS configuration
if settings.app_env == "production":
    # Parse comma-separated origins from env or use defaults
    cors_origins = getattr(settings, 'cors_origins', '')
    if cors_origins:
        allow_origins = [origin.strip() for origin in cors_origins.split(',')]
    else:
        # Fallback - must be configured in production
        allow_origins = [settings.mini_app_url] if settings.mini_app_url else []
else:
    allow_origins = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Self-Observation API is running"}


@app.post("/smoke-test")
def smoke_test(db: Session = Depends(get_db)):
    """Create test user and entry to verify database works."""
    # Check if test user exists
    user = db.query(User).filter(User.telegram_user_id == "test123").first()
    if not user:
        user = User(
            telegram_user_id="test123",
            username="testuser",
            first_name="Test",
            timezone="UTC",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create a test entry
    entry = Entry(
        user_id=user.id,
        entry_type="pulse",
        mood=7,
        anxiety=4,
        energy=6,
        insight="Smoke test entry",
        source="test",
    )
    db.add(entry)
    db.commit()

    return {
        "user_id": user.id,
        "entry_id": entry.id,
        "status": "database smoke test passed",
    }


@app.get("/smoke-verify")
def smoke_verify(db: Session = Depends(get_db)):
    """Verify test data exists."""
    user_count = db.query(User).count()
    entry_count = db.query(Entry).count()
    return {
        "users": user_count,
        "entries": entry_count,
    }
