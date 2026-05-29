"""Tests for Weekly AI Reflection endpoint."""

import pytest
from datetime import datetime, timedelta


def test_weekly_reflection_fewer_than_3_entries(client, db, mock_auth, test_user):
    """Test that reflection works with <3 entries but marks as placeholder."""
    from app.models import Entry
    
    # Create only 2 entries
    for i in range(2):
        entry = Entry(
            user_id=test_user.id,
            mood=6,
            anxiety=4,
            energy=7,
            entry_type="pulse",
            source="mini_app",
            created_at=datetime.utcnow() - timedelta(days=i),
        )
        db.add(entry)
    db.commit()
    
    response = client.post("/ai/weekly-reflection", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    
    assert data["entry_count"] == 2
    assert data["is_placeholder"] is True
    assert "Недостаточно записей" in data["patterns"]


def test_weekly_reflection_3_plus_entries_no_ai_key(client, db, mock_auth, test_user):
    """Test reflection with 3+ entries but no AI key returns graceful placeholder."""
    from app.models import Entry
    
    # Create 4 entries
    for i in range(4):
        entry = Entry(
            user_id=test_user.id,
            mood=6 + i,
            anxiety=4,
            energy=7,
            entry_type="pulse",
            source="mini_app",
            created_at=datetime.utcnow() - timedelta(days=i),
        )
        db.add(entry)
    db.commit()
    
    response = client.post("/ai/weekly-reflection", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    
    assert data["entry_count"] == 4
    assert data["is_placeholder"] is True
    assert "patterns" in data
    assert "energy_insights" in data
    assert "goal_connections" in data
    assert "next_week_question" in data
    assert "next_week_focus" in data


def test_weekly_reflection_stored_in_ai_analyses(client, db, mock_auth, test_user):
    """Test that reflection result is stored in ai_analyses table."""
    from app.models import Entry, AIAnalysis
    
    # Create 3 entries
    for i in range(3):
        entry = Entry(
            user_id=test_user.id,
            mood=7,
            anxiety=3,
            energy=8,
            entry_type="pulse",
            source="mini_app",
            created_at=datetime.utcnow() - timedelta(days=i),
        )
        db.add(entry)
    db.commit()
    
    # Create reflection
    response = client.post("/ai/weekly-reflection", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    
    # Verify stored in database
    analysis = db.query(AIAnalysis).filter(
        AIAnalysis.user_id == test_user.id,
        AIAnalysis.analysis_type == "weekly_reflection"
    ).first()
    
    assert analysis is not None
    assert analysis.entry_count == 3
    assert analysis.raw_output is not None


def test_weekly_reflection_user_isolation(client, db, mock_auth, test_user):
    """Test that users can only see their own reflections."""
    from app.models import Entry, AIAnalysis, User
    
    # Create entry for test_user
    entry = Entry(
        user_id=test_user.id,
        mood=7,
        anxiety=3,
        energy=8,
        entry_type="pulse",
        source="mini_app",
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    
    # Create reflection for test_user
    response = client.post("/ai/weekly-reflection", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    
    # Create another user
    other_user = User(
        telegram_user_id="987654321",
        username="other_user",
    )
    db.add(other_user)
    db.commit()
    
    # Create analysis manually for other user
    other_analysis = AIAnalysis(
        user_id=other_user.id,
        analysis_type="weekly_reflection",
        period_start=datetime.utcnow() - timedelta(days=7),
        period_end=datetime.utcnow(),
        entry_count=5,
        raw_output={"patterns": "other user data"},
    )
    db.add(other_analysis)
    db.commit()
    
    # Verify test_user only sees their own reflection
    response = client.get("/ai/weekly-reflection/latest", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    
    # Should be test_user's reflection, not other_user's
    assert data is not None
    assert data["entry_count"] == 1  # test_user has 1 entry


def test_latest_reflection_endpoint(client, db, mock_auth, test_user):
    """Test GET /ai/weekly-reflection/latest returns most recent reflection."""
    from app.models import Entry, AIAnalysis
    
    # Create entries and reflection
    for i in range(3):
        entry = Entry(
            user_id=test_user.id,
            mood=7,
            anxiety=3,
            energy=8,
            entry_type="pulse",
            source="mini_app",
            created_at=datetime.utcnow() - timedelta(days=i),
        )
        db.add(entry)
    db.commit()
    
    # Create first reflection
    response1 = client.post("/ai/weekly-reflection", headers={"Authorization": "Bearer mock_token"})
    assert response1.status_code == 200
    first_id = response1.json()["id"]
    
    # Wait a moment and create second reflection
    import time
    time.sleep(0.1)
    
    response2 = client.post("/ai/weekly-reflection", headers={"Authorization": "Bearer mock_token"})
    assert response2.status_code == 200
    second_id = response2.json()["id"]
    
    # Get latest - should be second
    latest_response = client.get("/ai/weekly-reflection/latest", headers={"Authorization": "Bearer mock_token"})
    assert latest_response.status_code == 200
    latest_data = latest_response.json()
    
    assert latest_data["id"] == second_id
