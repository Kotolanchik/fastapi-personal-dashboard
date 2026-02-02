from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ... import schemas
from ...services.goals import (
    create_goal as create_goal_svc,
    delete_goal,
    get_goal,
    get_goals_with_progress,
    list_goals,
    update_goal as update_goal_svc,
)
from ..deps import get_current_user, get_db_session

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=schemas.GoalsProgressResponse)
def get_goals(
    period: str = Query("7d", description="Progress period: 7d, month, deadline"),
    include_archived: bool = Query(False, description="Include archived goals"),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    if period not in schemas.GOAL_PROGRESS_PERIODS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"period must be one of {schemas.GOAL_PROGRESS_PERIODS}",
        )
    return get_goals_with_progress(db, user.id, period=period, include_archived=include_archived)


@router.post("", response_model=schemas.GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: schemas.GoalCreate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    if payload.sphere not in schemas.GOAL_SPHERES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"sphere must be one of {schemas.GOAL_SPHERES}",
        )
    goals = list_goals(db, user.id, include_archived=False)
    if len(goals) >= schemas.GOAL_MAX_ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {schemas.GOAL_MAX_ACTIVE} active goals. Archive or delete one first.",
        )
    from ...services.goals import count_active_goals_by_sphere
    if count_active_goals_by_sphere(db, user.id, payload.sphere) >= schemas.GOAL_MAX_PER_SPHERE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {schemas.GOAL_MAX_PER_SPHERE} active goals per sphere ({payload.sphere}). Archive or delete one first.",
        )
    if getattr(payload, "course_id", None) is not None:
        from ... import models
        course = db.query(models.LearningCourse).filter(
            models.LearningCourse.id == payload.course_id,
            models.LearningCourse.user_id == user.id,
        ).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course not found or not owned by you.",
            )
    return create_goal_svc(db, user.id, payload)


@router.get("/{goal_id}", response_model=schemas.GoalRead)
def read_goal(
    goal_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    goal = get_goal(db, goal_id, user.id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


@router.patch("/{goal_id}", response_model=schemas.GoalRead)
def update_goal(
    goal_id: int,
    payload: schemas.GoalUpdate,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    goal = get_goal(db, goal_id, user.id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    if payload.sphere is not None and payload.sphere not in schemas.GOAL_SPHERES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"sphere must be one of {schemas.GOAL_SPHERES}",
        )
    return update_goal_svc(db, goal, payload)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_goal(
    goal_id: int,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    goal = get_goal(db, goal_id, user.id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    delete_goal(db, goal)
