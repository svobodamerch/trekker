"""
Voice entry endpoint: upload audio, transcribe, parse into Entry or Goal.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_current_user, get_db
from app.models import User, Entry, Goal
from app.services.voice_service import VoiceService
from app.schemas.entry import EntryOut
from app.schemas.goal import GoalOut

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/process", response_model=dict)
async def process_voice(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Process voice recording:
    1. Transcribe audio using Groq Whisper
    2. Parse transcript with AI
    3. Create Entry or Goal based on parsed data
    4. Return created object + transcript
    """
    # Read audio bytes
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    # Process voice
    voice_service = VoiceService()
    result = await voice_service.process_voice(audio_bytes, audio.filename)

    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])

    # Determine type and create appropriate object
    entry_type = result.get("type", "entry")
    data = result.get("data", {})
    transcript = result.get("transcript", "")

    created_obj = None

    if entry_type == "goal":
        # Create Goal
        goal = Goal(
            user_id=current_user.id,
            horizon=data.get("horizon", "month"),
            title=data.get("title", "Голосовая цель"),
            description=data.get("description", transcript),  # Fallback to full transcript
            status=data.get("status", "active"),
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        created_obj = {
            "type": "goal",
            "id": goal.id,
            "title": goal.title,
            "horizon": goal.horizon,
        }

    else:
        # Create Entry (default)
        entry = Entry(
            user_id=current_user.id,
            entry_type=data.get("entry_type", "pulse"),
            mood=data.get("mood"),
            energy=data.get("energy"),
            anxiety=data.get("anxiety"),
            body_state=data.get("body_state"),
            insight=data.get("insight"),
            gratitude=data.get("gratitude"),
            today_moment=data.get("today_moment"),
            tomorrow_commitment=data.get("tomorrow_commitment"),
            raw_text=transcript,  # Save full transcript
            source="voice",
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        created_obj = {
            "type": "entry",
            "id": entry.id,
            "entry_type": entry.entry_type,
            "mood": entry.mood,
            "energy": entry.energy,
            "anxiety": entry.anxiety,
        }

    return {
        "success": True,
        "recognized_type": entry_type,
        "confidence": result.get("confidence", 0.5),
        "transcript": transcript,
        "created": created_obj,
        "parsed": result.get("parsed", False),
    }


@router.post("/transcribe-only")
async def transcribe_only(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Just transcribe audio to text without creating anything.
    Useful for preview before saving.
    """
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    voice_service = VoiceService()

    # Only transcribe, no parsing
    transcript = await voice_service._transcribe(audio_bytes, audio.filename)

    if not transcript:
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")

    return {
        "transcript": transcript,
        "language": "ru",
    }
