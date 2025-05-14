# app/api/endpoints/sprints.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.sprint import SprintCreate, SprintUpdate, SprintResponse
from app.services.database import get_database

router = APIRouter()


@router.post("/", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
        sprint: SprintCreate,
        db=Depends(get_database)
):
    """Create a new sprint."""
    from datetime import datetime

    # Check if project exists
    project = await db.projects.find_one({"project_id": sprint.project_id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not found"
        )

    # Check if sprint with same ID already exists
    existing_sprint = await db.sprint_progress.find_one({
        "project_id": sprint.project_id,
        "sprint_id": sprint.sprint_id
    })

    if existing_sprint:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sprint already exists for this project"
        )

    # Create a new sprint
    sprint_data = sprint.dict()
    sprint_data["created_at"] = datetime.utcnow()
    sprint_data["updated_at"] = datetime.utcnow()

    # Initialize burndown trend
    from datetime import timedelta

    start_date = sprint.start_date
    end_date = sprint.end_date
    current_date = start_date
    burndown_trend = []

    while current_date <= end_date:
        burndown_trend.append({
            "date": current_date,
            "remaining_points": sprint.total_story_points
        })
        current_date += timedelta(days=1)

    sprint_data["burndown_trend"] = burndown_trend

    # Insert into database
    result = await db.sprint_progress.insert_one(sprint_data)

    # Retrieve and return the created sprint
    created_sprint = await db.sprint_progress.find_one({"_id": result.inserted_id})

    return created_sprint


@router.get("/", response_model=List[SprintResponse])
async def get_sprints(
        project_id: Optional[str] = None,
        current: Optional[bool] = None,
        db=Depends(get_database)
):
    """Get all sprints with optional filters."""
    from datetime import datetime

    # Build query filters
    query = {}
    if project_id:
        query["project_id"] = project_id

    if current:
        now = datetime.utcnow()
        query["start_date"] = {"$lte": now}
        query["end_date"] = {"$gte": now}

    # Retrieve sprints
    sprints = await db.sprint_progress.find(query).to_list(length=100)

    return sprints


@router.get("/{sprint_id}", response_model=SprintResponse)
async def get_sprint(
        sprint_id: str,
        project_id: str,
        db=Depends(get_database)
):
    """Get a specific sprint by ID."""
    # Retrieve sprint
    sprint = await db.sprint_progress.find_one({
        "project_id": project_id,
        "sprint_id": sprint_id
    })

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint not found"
        )

    return sprint


@router.put("/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
        sprint_id: str,
        project_id: str,
        sprint_update: SprintUpdate,
        db=Depends(get_database)
):
    """Update a sprint."""
    from datetime import datetime

    # Check if sprint exists
    existing_sprint = await db.sprint_progress.find_one({
        "project_id": project_id,
        "sprint_id": sprint_id
    })

    if not existing_sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint not found"
        )

    # Update fields
    update_data = sprint_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    # Calculate percentage completion if points changed
    if "completed_story_points" in update_data or "total_story_points" in update_data:
        total_points = update_data.get("total_story_points", existing_sprint["total_story_points"])
        completed_points = update_data.get("completed_story_points", existing_sprint["completed_story_points"])

        if total_points > 0:
            update_data["percent_completion"] = (completed_points / total_points) * 100
        else:
            update_data["percent_completion"] = 0

        update_data["remaining_story_points"] = total_points - completed_points

    # Update burndown trend if needed
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    if "remaining_story_points" in update_data:
        burndown_trend = existing_sprint["burndown_trend"]

        # Find today's entry or the most recent entry
        updated = False
        for entry in burndown_trend:
            entry_date = entry["date"].replace(hour=0, minute=0, second=0, microsecond=0)
            if entry_date == today:
                entry["remaining_points"] = update_data["remaining_story_points"]
                updated = True
                break

        if not updated and burndown_trend:
            # Add new entry for today
            burndown_trend.append({
                "date": today,
                "remaining_points": update_data["remaining_story_points"]
            })

        update_data["burndown_trend"] = burndown_trend

    # Update in database
    await db.sprint_progress.update_one(
        {"project_id": project_id, "sprint_id": sprint_id},
        {"$set": update_data}
    )

    # Retrieve and return the updated sprint
    updated_sprint = await db.sprint_progress.find_one({
        "project_id": project_id,
        "sprint_id": sprint_id
    })

    return updated_sprint
