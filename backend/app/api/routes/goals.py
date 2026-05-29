from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User, Goal, GoalVersion, Entry, EntryGoalLink
from datetime import datetime, timedelta
from app.schemas.goal import GoalCreate, GoalUpdate, GoalOut, GoalsByHorizon, EntryGoalLinkCreate, GoalReviewCreate, GoalNeedsReview

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=GoalOut)
def create_goal(
    goal_in: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = Goal(
        user_id=current_user.id,
        **goal_in.model_dump(),
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("", response_model=GoalsByHorizon)
def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return goals grouped by horizon."""
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.status.in_(["active", "paused"]),
    ).order_by(Goal.created_at.desc()).all()

    by_horizon = {
        "month": [],
        "year": [],
        "three_years": [],
        "five_years": [],
        "dream_life": [],
    }

    for goal in goals:
        by_horizon[goal.horizon].append(GoalOut.model_validate(goal))

    return GoalsByHorizon(**by_horizon)


@router.get("/{goal_id}", response_model=GoalOut)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id,
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.patch("/{goal_id}", response_model=GoalOut)
def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id,
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    # Save current version to history
    version = GoalVersion(
        goal_id=goal.id,
        title=goal.title,
        description=goal.description,
        desired_state=goal.desired_state,
        status=goal.status,
        change_note=goal_update.change_note or "Updated via API",
    )
    db.add(version)

    # Update goal
    update_data = goal_update.model_dump(exclude_unset=True, exclude={"change_note"})
    for field, value in update_data.items():
        setattr(goal, field, value)

    from datetime import datetime
    goal.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(goal)
    return goal


@router.post("/entry-link/{entry_id}", response_model=dict)
def link_entry_to_goal(
    entry_id: int,
    link_data: EntryGoalLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Link a daily entry to a goal or horizon."""
    # Verify entry belongs to user
    entry = db.query(Entry).filter(
        Entry.id == entry_id,
        Entry.user_id == current_user.id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # If goal_id provided, verify it belongs to user
    if link_data.goal_id:
        goal = db.query(Goal).filter(
            Goal.id == link_data.goal_id,
            Goal.user_id == current_user.id,
        ).first()
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")

    # Create link
    link = EntryGoalLink(
        entry_id=entry_id,
        goal_id=link_data.goal_id,
        horizon=link_data.horizon,
        step_text=link_data.step_text,
    )
    db.add(link)
    db.commit()

    return {"status": "linked", "link_id": link.id}


@router.post("/{goal_id}/review", response_model=GoalOut)
def review_goal(
    goal_id: int,
    review_data: GoalReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Review a goal with reflective questions and optional updates.
    
    Creates goal version if goal fields are changed.
    Updates last_reviewed_at timestamp.
    """
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id,
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Store old values for version history
    old_title = goal.title
    old_description = goal.description
    old_desired_state = goal.desired_state
    old_status = goal.status
    
    # Check if any goal fields are being updated
    fields_changed = False
    change_notes = []
    
    if review_data.title is not None and review_data.title != goal.title:
        fields_changed = True
        change_notes.append(f"title: {goal.title} -> {review_data.title}")
        goal.title = review_data.title
        
    if review_data.description is not None and review_data.description != goal.description:
        fields_changed = True
        change_notes.append("description updated")
        goal.description = review_data.description
        
    if review_data.desired_state is not None and review_data.desired_state != goal.desired_state:
        fields_changed = True
        change_notes.append("desired_state updated")
        goal.desired_state = review_data.desired_state
        
    if review_data.status is not None and review_data.status != goal.status:
        fields_changed = True
        change_notes.append(f"status: {goal.status} -> {review_data.status}")
        goal.status = review_data.status
    
    # If fields changed, create version history (with OLD values)
    if fields_changed:
        # Build change note from review answers + field changes
        review_note_parts = []
        if review_data.is_alive is not None:
            review_note_parts.append(f"Goal feels alive: {review_data.is_alive}")
        if review_data.became_clearer:
            review_note_parts.append(f"Became clearer: {review_data.became_clearer}")
        if review_data.wants_to_change:
            review_note_parts.append(f"Wants to change: {review_data.wants_to_change}")
        if review_data.next_week_step:
            review_note_parts.append(f"Next week step: {review_data.next_week_step}")
        
        full_change_note = " | ".join(review_note_parts + change_notes)
        
        version = GoalVersion(
            goal_id=goal.id,
            title=old_title,
            description=old_description,
            desired_state=old_desired_state,
            status=old_status,
            change_note=full_change_note[:500],  # Limit length
        )
        db.add(version)
    
    # Always update last_reviewed_at
    goal.last_reviewed_at = datetime.utcnow()
    goal.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/needs-review", response_model=GoalNeedsReview)
def get_goals_needing_review(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get goals that haven't been reviewed in 30+ days or never reviewed."""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.status == "active",
    ).filter(
        (Goal.last_reviewed_at == None) | (Goal.last_reviewed_at < thirty_days_ago)
    ).order_by(Goal.created_at.desc()).all()
    
    count = len(goals)
    
    if count == 0:
        message = "Все цели актуальны. Когда захочешь — можно пересмотреть в любой момент."
    elif count == 1:
        message = "Одна цель давно не проверялась. Хочешь посмотреть, всё ли ещё живое?"
    else:
        message = f"{count} целей давно не проверялись. Цели можно менять — это не провал, а уточнение направления."
    
    return GoalNeedsReview(
        goals=[GoalOut.model_validate(g) for g in goals],
        count=count,
        message=message,
    )
