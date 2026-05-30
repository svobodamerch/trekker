"""Community Support Circle API routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select, func, and_, or_

from app.api.deps import get_current_user, get_db
from app.models import User, CommunityPost, CommunityComment, CommunityReaction, CommunityReport
from app.models.entry import Entry
from app.models.goal import Goal
from app.models.life_balance import LifeBalanceSnapshot
from app.schemas.community import (
    CommunityPostCreate, CommunityPostUpdate, CommunityPostInFeed, CommunityPostDetail,
    CommunityCommentCreate, CommunityCommentResponse,
    CommunityReactionCreate, CommunityReactionResponse,
    CommunityReportCreate, CommunityReportResponse,
    CommunityFeedResponse, ShareSourcePreview, ShareSourceRequest,
)

router = APIRouter(prefix="/community", tags=["community"])


def get_display_name(user: User, visibility: str) -> str:
    """Get display name based on visibility setting."""
    if visibility == "anonymous":
        return "Пользователь"
    # For named visibility, use full name if available
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    return user.username or user.first_name or "Пользователь"


def check_source_ownership(db: Session, source_type: str, source_id: int, user_id: int) -> bool:
    """Verify user owns the source object they want to share."""
    if source_type == "pulse":
        entry = db.query(Entry).filter_by(id=source_id).first()
        return entry is not None and entry.user_id == user_id
    elif source_type == "goal":
        goal = db.query(Goal).filter_by(id=source_id).first()
        return goal is not None and goal.user_id == user_id
    elif source_type == "life_balance":
        snapshot = db.query(LifeBalanceSnapshot).filter_by(id=source_id).first()
        return snapshot is not None and snapshot.user_id == user_id
    elif source_type == "custom":
        return True  # No source to verify
    return False


def get_source_preview(db: Session, source_type: str, source_id: int) -> tuple[Optional[str], str]:
    """Get title and body preview from source."""
    if source_type == "pulse":
        entry = db.query(Entry).filter_by(id=source_id).first()
        if entry:
            title = f"Пульс от {entry.created_at.strftime('%d.%m')}"
            body = entry.body_state or entry.insight or entry.gratitude or entry.tomorrow_commitment or ""
            return title, body[:500]
    elif source_type == "goal":
        goal = db.query(Goal).filter_by(id=source_id).first()
        if goal:
            return goal.current_title, goal.current_description or ""[:500]
    elif source_type == "life_balance":
        snapshot = db.query(LifeBalanceSnapshot).filter_by(id=source_id).first()
        if snapshot:
            return f"Срез баланса ({snapshot.created_at.strftime('%d.%m')})", snapshot.notes or ""
    return None, ""


# === Feed Routes ===

@router.get("/feed", response_model=CommunityFeedResponse)
async def get_feed(
    cursor: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get community feed with published posts."""
    # Query published posts, newest first
    query = (
        select(CommunityPost)
        .where(CommunityPost.status == "published")
        .options(joinedload(CommunityPost.user))
        .order_by(CommunityPost.created_at.desc())
    )
    
    # Add cursor pagination
    if cursor:
        cursor_id = int(cursor)
        query = query.where(CommunityPost.id < cursor_id)
    
    result = db.execute(query.limit(limit + 1))
    posts = result.scalars().all()
    
    has_more = len(posts) > limit
    posts = posts[:limit]
    
    # Build response with counts
    result_posts = []
    for post in posts:
        # Count comments
        comment_count = db.scalar(
            select(func.count())
            .where(CommunityComment.post_id == post.id)
            .where(CommunityComment.status == "published")
        ) or 0
        
        # Count reactions and check if user reacted
        reaction_count = db.scalar(
            select(func.count())
            .where(CommunityReaction.post_id == post.id)
        ) or 0
        
        has_user_reacted = db.scalar(
            select(func.count())
            .where(CommunityReaction.post_id == post.id)
            .where(CommunityReaction.user_id == current_user.id)
        ) or 0 > 0
        
        # Get source preview
        source_preview = None
        if post.source_type != "custom":
            _, source_preview = get_source_preview(db, post.source_type, post.source_id)
        
        result_posts.append(CommunityPostInFeed(
            id=post.id,
            author={
                "id": post.user_id,
                "display_name": get_display_name(post.user, post.visibility),
                "avatar": None
            },
            title=post.title,
            body=post.body,
            discussion_prompt=post.discussion_prompt,
            source_type=post.source_type,
            source_preview=source_preview,
            comment_count=comment_count,
            reaction_count=reaction_count,
            has_user_reacted=has_user_reacted,
            is_own_post=post.user_id == current_user.id,
            created_at=post.created_at
        ))
    
    next_cursor = str(posts[-1].id) if posts and has_more else None
    
    return CommunityFeedResponse(
        posts=result_posts,
        has_more=has_more,
        next_cursor=next_cursor
    )


# === Post Routes ===

@router.post("/posts", response_model=CommunityPostInFeed)
async def create_post(
    data: CommunityPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new community post (manual)."""
    # If sharing from source, verify ownership
    if data.source_type != "custom" and data.source_id:
        if not check_source_ownership(db, data.source_type, data.source_id, current_user.id):
            raise HTTPException(403, "Можно делиться только своими записями")
        
        title, body = get_source_preview(db, data.source_type, data.source_id)
        post_body = data.body or body or ""
        post_title = data.title or title
    else:
        post_body = data.body
        post_title = data.title
    
    post = CommunityPost(
        user_id=current_user.id,
        source_type=data.source_type,
        source_id=data.source_id,
        title=post_title,
        body=post_body,
        discussion_prompt=data.discussion_prompt,
        visibility=data.visibility,
        status="published"
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return CommunityPostInFeed(
        id=post.id,
        author={
            "id": current_user.id,
            "display_name": get_display_name(current_user, post.visibility),
            "avatar": None
        },
        title=post.title,
        body=post.body,
        discussion_prompt=post.discussion_prompt,
        source_type=post.source_type,
        source_preview=None,
        comment_count=0,
        reaction_count=0,
        has_user_reacted=False,
        is_own_post=True,  # User always owns their own new post
        created_at=post.created_at
    )


@router.get("/posts/{post_id}", response_model=CommunityPostDetail)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single post with comments."""
    result = db.execute(
        select(CommunityPost)
        .where(CommunityPost.id == post_id)
        .where(CommunityPost.status == "published")
        .options(joinedload(CommunityPost.user))
    )
    post = result.scalars().first()
    
    if not post:
        raise HTTPException(404, "Публикация не найдена")
    
    # Get comments
    comments_result = db.execute(
        select(CommunityComment)
        .where(CommunityComment.post_id == post_id)
        .where(CommunityComment.status == "published")
        .options(joinedload(CommunityComment.user))
        .order_by(CommunityComment.created_at.asc())
    )
    comments = comments_result.scalars().all()
    
    comment_responses = [
        CommunityCommentResponse(
            id=c.id,
            author={
                "id": c.user_id,
                "display_name": "Пользователь"  # Comments always anonymous
            },
            body=c.body,
            comment_type=c.comment_type,
            status=c.status,
            created_at=c.created_at
        )
        for c in comments
    ]
    
    # Get counts
    reaction_count = db.scalar(
        select(func.count())
        .where(CommunityReaction.post_id == post_id)
    ) or 0
    
    has_user_reacted = db.scalar(
        select(func.count())
        .where(CommunityReaction.post_id == post_id)
        .where(CommunityReaction.user_id == current_user.id)
    ) or 0 > 0
    
    source_preview = None
    if post.source_type != "custom":
        _, source_preview = get_source_preview(db, post.source_type, post.source_id)
    
    return CommunityPostDetail(
        id=post.id,
        author={
            "id": post.user_id,
            "display_name": get_display_name(post.user, post.visibility),
            "avatar": None
        },
        title=post.title,
        body=post.body,
        discussion_prompt=post.discussion_prompt,
        source_type=post.source_type,
        source_preview=source_preview,
        comment_count=len(comment_responses),
        reaction_count=reaction_count,
        has_user_reacted=has_user_reacted,
        is_own_post=post.user_id == current_user.id,
        created_at=post.created_at,
        comments=comment_responses
    )


@router.patch("/posts/{post_id}", response_model=CommunityPostInFeed)
async def update_post(
    post_id: int,
    data: CommunityPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update own post."""
    post = db.query(CommunityPost).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(404, "Публикация не найдена")
    
    if post.user_id != current_user.id:
        raise HTTPException(403, "Можно редактировать только свои публикации")
    
    # Update fields
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    
    return await get_post(post_id, db, current_user)


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete (soft) own post."""
    post = db.query(CommunityPost).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(404, "Публикация не найдена")
    
    if post.user_id != current_user.id:
        raise HTTPException(403, "Можно удалять только свои публикации")
    
    post.status = "deleted"
    db.commit()
    
    return {"success": True, "message": "Публикация удалена"}


# === Comment Routes ===

@router.post("/posts/{post_id}/comments", response_model=CommunityCommentResponse)
async def create_comment(
    post_id: int,
    data: CommunityCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add comment to post."""
    # Verify post exists and is published
    post = db.query(CommunityPost).filter_by(id=post_id).first()
    if not post or post.status != "published":
        raise HTTPException(404, "Публикация не найдена")
    
    # Prevent self-commenting (optional, but good for support circle)
    if post.user_id == current_user.id:
        raise HTTPException(400, "Не стоит оставлять комментарии к своей публикации")
    
    comment = CommunityComment(
        post_id=post_id,
        user_id=current_user.id,
        body=data.body,
        comment_type=data.comment_type,
        status="published"
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return CommunityCommentResponse(
        id=comment.id,
        author={
            "id": current_user.id,
            "display_name": "Пользователь"
        },
        body=comment.body,
        comment_type=comment.comment_type,
        status=comment.status,
        created_at=comment.created_at
    )


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete (soft) own comment."""
    comment = db.query(CommunityComment).filter_by(id=comment_id).first()
    if not comment:
        raise HTTPException(404, "Комментарий не найден")
    
    if comment.user_id != current_user.id:
        raise HTTPException(403, "Можно удалять только свои комментарии")
    
    comment.status = "deleted"
    db.commit()
    
    return {"success": True, "message": "Комментарий удален"}


# === Reaction Routes ===

@router.post("/posts/{post_id}/reactions", response_model=CommunityReactionResponse)
async def add_reaction(
    post_id: int,
    data: CommunityReactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add reaction to post (or toggle if already exists)."""
    # Verify post exists
    post = db.query(CommunityPost).filter_by(id=post_id).first()
    if not post or post.status != "published":
        raise HTTPException(404, "Публикация не найдена")
    
    # Check if already reacted
    existing = db.execute(
        select(CommunityReaction)
        .where(CommunityReaction.post_id == post_id)
        .where(CommunityReaction.user_id == current_user.id)
        .where(CommunityReaction.reaction_type == data.reaction_type)
    ).scalars().first()
    
    if existing:
        # Remove reaction (toggle off)
        db.delete(existing)
        db.commit()
        return CommunityReactionResponse(
            id=existing.id,
            user_id=current_user.id,
            reaction_type=data.reaction_type,
            created_at=existing.created_at,
            removed=True
        )
    
    # Add new reaction
    reaction = CommunityReaction(
        post_id=post_id,
        user_id=current_user.id,
        reaction_type=data.reaction_type
    )
    
    db.add(reaction)
    db.commit()
    db.refresh(reaction)
    
    return CommunityReactionResponse(
        id=reaction.id,
        user_id=current_user.id,
        reaction_type=reaction.reaction_type,
        created_at=reaction.created_at
    )


# === Report Routes ===

@router.post("/reports", response_model=CommunityReportResponse)
async def create_report(
    data: CommunityReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Report post or comment."""
    # Validate at least one of post_id or comment_id
    if not data.post_id and not data.comment_id:
        raise HTTPException(400, "Укажите пост или комментарий для репорта")
    
    # Verify existence
    if data.post_id:
        post = db.query(CommunityPost).filter_by(id=data.post_id).first()
        if not post:
            raise HTTPException(404, "Публикация не найдена")
    
    if data.comment_id:
        comment = db.query(CommunityComment).filter_by(id=data.comment_id).first()
        if not comment:
            raise HTTPException(404, "Комментарий не найден")
    
    report = CommunityReport(
        reporter_user_id=current_user.id,
        post_id=data.post_id,
        comment_id=data.comment_id,
        reason=data.reason,
        details=data.details,
        status="new"
    )
    
    db.add(report)
    db.commit()
    
    return CommunityReportResponse(
        id=report.id,
        status=report.status,
        message="Спасибо. Я получил репорт и разберусь."
    )


# === Share from Source Routes ===

@router.get("/share-preview", response_model=ShareSourcePreview)
async def preview_share(
    source_type: str,
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Preview before sharing from source."""
    can_share = check_source_ownership(db, source_type, source_id, current_user.id)
    title, body = get_source_preview(db, source_type, source_id)
    
    error_message = None
    if not can_share:
        error_message = "Можно делиться только своими записями"
    
    return ShareSourcePreview(
        source_type=source_type,
        source_id=source_id,
        title=title,
        body_preview=body[:500] if body else "",
        can_share=can_share,
        error_message=error_message
    )


@router.post("/share", response_model=CommunityPostInFeed)
async def share_from_source(
    data: ShareSourceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Share from source (Pulse, Goal, Life Balance)."""
    if not check_source_ownership(db, data.source_type, data.source_id, current_user.id):
        raise HTTPException(403, "Можно делиться только своими записями")
    
    title, body = get_source_preview(db, data.source_type, data.source_id)
    
    post = CommunityPost(
        user_id=current_user.id,
        source_type=data.source_type,
        source_id=data.source_id,
        title=data.title or title,
        body=body,
        discussion_prompt=data.discussion_prompt,
        visibility=data.visibility,
        status="published"
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return CommunityPostInFeed(
        id=post.id,
        author={
            "id": current_user.id,
            "display_name": get_display_name(current_user, post.visibility),
            "avatar": None
        },
        title=post.title,
        body=post.body,
        discussion_prompt=post.discussion_prompt,
        source_type=post.source_type,
        source_preview=None,
        comment_count=0,
        reaction_count=0,
        has_user_reacted=False,
        is_own_post=True,
        created_at=post.created_at
    )


# === User Stats ===

@router.get("/user/stats")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's community activity stats."""
    posts_count = db.scalar(
        select(func.count())
        .where(CommunityPost.user_id == current_user.id)
        .where(CommunityPost.status == "published")
    ) or 0
    
    comments_count = db.scalar(
        select(func.count())
        .where(CommunityComment.user_id == current_user.id)
        .where(CommunityComment.status == "published")
    ) or 0
    
    reactions_given = db.scalar(
        select(func.count())
        .where(CommunityReaction.user_id == current_user.id)
    ) or 0
    
    # Reactions received on user's posts
    reactions_received = db.scalar(
        select(func.count())
        .select_from(CommunityReaction)
        .join(CommunityPost, CommunityReaction.post_id == CommunityPost.id)
        .where(CommunityPost.user_id == current_user.id)
    ) or 0
    
    return {
        "posts_count": posts_count,
        "comments_count": comments_count,
        "reactions_given": reactions_given,
        "reactions_received": reactions_received
    }
