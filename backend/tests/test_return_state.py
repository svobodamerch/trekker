"""Tests for soft return mechanic - return state calculation."""

import pytest
from datetime import datetime, timedelta
from app.schemas.home import HomeSummary


def test_new_user_state(client, db, mock_auth):
    """Test new_user state when no entries exist."""
    response = client.get("/entries/home/summary", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    assert data["return_state"] == "new_user"
    assert data["has_entries"] is False
    assert data["days_since_last_entry"] is None


def test_active_today_state(client, db, mock_auth, test_user):
    """Test active_today state when entry exists today."""
    from app.models import Entry
    
    # Create entry for today
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
    
    response = client.get("/entries/home/summary", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    assert data["return_state"] == "active_today"
    assert data["has_entries"] is True
    assert data["days_since_last_entry"] == 0


def test_one_day_gap_state(client, db, mock_auth, test_user):
    """Test one_day_gap state when last entry was yesterday."""
    from app.models import Entry
    
    # Create entry from yesterday
    entry = Entry(
        user_id=test_user.id,
        mood=6,
        anxiety=4,
        energy=7,
        entry_type="pulse",
        source="mini_app",
        created_at=datetime.utcnow() - timedelta(days=1),
    )
    db.add(entry)
    db.commit()
    
    response = client.get("/entries/home/summary", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    assert data["return_state"] == "one_day_gap"
    assert data["days_since_last_entry"] == 1


def test_after_pause_state(client, db, mock_auth, test_user):
    """Test after_pause state when 3+ days passed."""
    from app.models import Entry
    
    # Create entry from 4 days ago
    entry = Entry(
        user_id=test_user.id,
        mood=5,
        anxiety=5,
        energy=5,
        entry_type="pulse",
        source="mini_app",
        created_at=datetime.utcnow() - timedelta(days=4),
    )
    db.add(entry)
    db.commit()
    
    response = client.get("/entries/home/summary", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    assert data["return_state"] == "after_pause"
    assert data["days_since_last_entry"] >= 3


def test_long_pause_state(client, db, mock_auth, test_user):
    """Test long_pause state when 7+ days passed."""
    from app.models import Entry
    
    # Create entry from 8 days ago
    entry = Entry(
        user_id=test_user.id,
        mood=4,
        anxiety=6,
        energy=4,
        entry_type="pulse",
        source="mini_app",
        created_at=datetime.utcnow() - timedelta(days=8),
    )
    db.add(entry)
    db.commit()
    
    response = client.get("/entries/home/summary", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    assert data["return_state"] == "long_pause"
    assert data["days_since_last_entry"] >= 7


def test_two_day_gap_is_one_day_gap(client, db, mock_auth, test_user):
    """Test that 2-day gap is treated as one_day_gap (not a pause)."""
    from app.models import Entry
    
    # Create entry from 2 days ago
    entry = Entry(
        user_id=test_user.id,
        mood=6,
        anxiety=4,
        energy=6,
        entry_type="pulse",
        source="mini_app",
        created_at=datetime.utcnow() - timedelta(days=2),
    )
    db.add(entry)
    db.commit()
    
    response = client.get("/entries/home/summary", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    assert data["return_state"] == "one_day_gap"
    assert data["days_since_last_entry"] == 2
