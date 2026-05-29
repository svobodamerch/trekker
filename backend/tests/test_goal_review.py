"""Tests for Goal Review Ritual."""

import pytest
from datetime import datetime, timedelta


def test_review_goal_updates_last_reviewed_at(client, db, mock_auth, test_user):
    """Test that reviewing a goal updates last_reviewed_at timestamp."""
    from app.models import Goal
    
    # Create a goal
    goal = Goal(
        user_id=test_user.id,
        horizon="month",
        title="Test Goal",
        description="Test description",
        status="active",
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    assert goal.last_reviewed_at is None
    
    # Review the goal
    response = client.post(
        f"/goals/{goal.id}/review",
        headers={"Authorization": "Bearer mock_token"},
        json={
            "is_alive": True,
            "became_clearer": "I understand better now",
            "next_week_step": "Small step",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["last_reviewed_at"] is not None


def test_review_goal_creates_version_when_fields_changed(client, db, mock_auth, test_user):
    """Test that editing goal during review creates goal version."""
    from app.models import Goal, GoalVersion
    
    # Create a goal
    goal = Goal(
        user_id=test_user.id,
        horizon="month",
        title="Old Title",
        description="Old description",
        status="active",
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    # Review with changes
    response = client.post(
        f"/goals/{goal.id}/review",
        headers={"Authorization": "Bearer mock_token"},
        json={
            "is_alive": True,
            "became_clearer": "New clarity",
            "title": "New Title",
            "description": "New description",
        },
    )
    assert response.status_code == 200
    
    # Verify version was created with OLD values
    versions = db.query(GoalVersion).filter(GoalVersion.goal_id == goal.id).all()
    assert len(versions) == 1
    assert versions[0].title == "Old Title"  # Version stores old value
    assert "New clarity" in versions[0].change_note  # But change_note has review data


def test_goals_needing_review_detected(client, db, mock_auth, test_user):
    """Test that goals needing review are correctly detected."""
    from app.models import Goal
    
    # Create a goal never reviewed
    goal1 = Goal(
        user_id=test_user.id,
        horizon="month",
        title="Never Reviewed",
        status="active",
    )
    db.add(goal1)
    
    # Create a goal reviewed 40 days ago
    goal2 = Goal(
        user_id=test_user.id,
        horizon="year",
        title="Old Review",
        status="active",
        last_reviewed_at=datetime.utcnow() - timedelta(days=40),
    )
    db.add(goal2)
    
    # Create a goal reviewed recently
    goal3 = Goal(
        user_id=test_user.id,
        horizon="month",
        title="Recently Reviewed",
        status="active",
        last_reviewed_at=datetime.utcnow() - timedelta(days=5),
    )
    db.add(goal3)
    
    db.commit()
    
    # Get goals needing review
    response = client.get("/goals/needs-review", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    
    assert data["count"] == 2
    assert "Never Reviewed" in [g["title"] for g in data["goals"]]
    assert "Old Review" in [g["title"] for g in data["goals"]]
    assert "Recently Reviewed" not in [g["title"] for g in data["goals"]]


def test_goal_review_user_isolation(client, db, mock_auth, test_user):
    """Test that users can only review their own goals."""
    from app.models import Goal, User
    
    # Create another user
    other_user = User(
        telegram_user_id="987654321",
        username="other_user",
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    
    # Create goal for other user
    other_goal = Goal(
        user_id=other_user.id,
        horizon="month",
        title="Other User Goal",
        status="active",
    )
    db.add(other_goal)
    db.commit()
    db.refresh(other_goal)
    
    # Try to review other user's goal
    response = client.post(
        f"/goals/{other_goal.id}/review",
        headers={"Authorization": "Bearer mock_token"},
        json={"is_alive": True},
    )
    assert response.status_code == 404


def test_goal_review_without_changes_does_not_create_version(client, db, mock_auth, test_user):
    """Test that review without goal changes doesn't create version."""
    from app.models import Goal, GoalVersion
    
    # Create a goal
    goal = Goal(
        user_id=test_user.id,
        horizon="month",
        title="Test Goal",
        status="active",
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    # Review without changing goal fields
    response = client.post(
        f"/goals/{goal.id}/review",
        headers={"Authorization": "Bearer mock_token"},
        json={
            "is_alive": True,
            "became_clearer": "Just reflections",
        },
    )
    assert response.status_code == 200
    
    # No version should be created since no fields changed
    versions = db.query(GoalVersion).filter(GoalVersion.goal_id == goal.id).all()
    assert len(versions) == 0
    
    # But last_reviewed_at should be updated
    db.refresh(goal)
    assert goal.last_reviewed_at is not None
