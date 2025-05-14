# app/api/endpoints/stories.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.user_story import UserStoryCreate, UserStoryUpdate, UserStoryResponse
from app.services.database import get_database

router = APIRouter()


@router.post("/", response_model=UserStoryResponse, status_code=status.HTTP_201_CREATED)
async def create_story(
        story: UserStoryCreate,
        db=Depends(get_database)
):
    """Create a new user story."""
    from datetime import datetime

    # Check if project exists
    project = await db.projects.find_one({"project_id": story.project_id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not found"
        )

    # Check if sprint exists
    sprint = await db.sprint_progress.find_one({
        "project_id": story.project_id,
        "sprint_id": story.sprint_id
    })

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sprint not found"
        )

    # Check if story with same ID already exists
    existing_story = await db.user_stories.find_one({
        "project_id": story.project_id,
        "story_id": story.story_id
    })

    if existing_story:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Story already exists for this project"
        )

    # Create a new story
    story_data = story.dict()
    story_data["created_at"] = datetime.utcnow()
    story_data["updated_at"] = datetime.utcnow()
    story_data["last_status_change_date"] = datetime.utcnow()
    story_data["days_in_current_status"] = 0

    # Insert into database
    result = await db.user_stories.insert_one(story_data)

    # Update sprint total points
    if story.story_points > 0:
        await db.sprint_progress.update_one(
            {"project_id": story.project_id, "sprint_id": story.sprint_id},
            {"$inc": {"total_story_points": story.story_points}}
        )

    # Retrieve and return the created story
    created_story = await db.user_stories.find_one({"_id": result.inserted_id})

    return created_story


@router.get("/", response_model=List[UserStoryResponse])
async def get_stories(
        project_id: Optional[str] = None,
        sprint_id: Optional[str] = None,
        assignee: Optional[str] = None,
        status: Optional[str] = None,
        db=Depends(get_database)
):
    """Get all user stories with optional filters."""
    # Build query filters
    query = {}
    if project_id:
        query["project_id"] = project_id
    if sprint_id:
        query["sprint_id"] = sprint_id
    if assignee:
        query["assignee"] = assignee
    if status:
        query["status"] = status

    # Retrieve stories
    stories = await db.user_stories.find(query).to_list(length=1000)

    return stories


@router.put("/{story_id}", response_model=UserStoryResponse)
async def update_story(
        story_id: str,
        project_id: str,
        story_update: UserStoryUpdate,
        db=Depends(get_database)
):
    """Update a user story."""
    from datetime import datetime

    # Check if story exists
    existing_story = await db.user_stories.find_one({
        "project_id": project_id,
        "story_id": story_id
    })

    if not existing_story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )

    # Update fields
    update_data = story_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    # Handle status change
    if "status" in update_data and update_data["status"] != existing_story["status"]:
        update_data["last_status_change_date"] = datetime.utcnow()
        update_data["days_in_current_status"] = 0

        # Update sprint completed points if status changed to/from "Done"
        if update_data["status"] == "Done" and existing_story["status"] != "Done":
            # Story was completed
            await db.sprint_progress.update_one(
                {"project_id": project_id, "sprint_id": existing_story["sprint_id"]},
                {"$inc": {"completed_story_points": existing_story["story_points"]}}
            )
        elif update_data["status"] != "Done" and existing_story["status"] == "Done":
            # Story was un-completed
            await db.sprint_progress.update_one(
                {"project_id": project_id, "sprint_id": existing_story["sprint_id"]},
                {"$inc": {"completed_story_points": -existing_story["story_points"]}}
            )

    # Handle story points change
    if "story_points" in update_data and update_data["story_points"] != existing_story["story_points"]:
        # Update sprint total points
        points_diff = update_data["story_points"] - existing_story["story_points"]
        await db.sprint_progress.update_one(
            {"project_id": project_id, "sprint_id": existing_story["sprint_id"]},
            {"$inc": {"total_story_points": points_diff}}
        )

        # If story is done, also update completed points
        if existing_story["status"] == "Done":
            await db.sprint_progress.update_one(
                {"project_id": project_id, "sprint_id": existing_story["sprint_id"]},
                {"$inc": {"completed_story_points": points_diff}}
            )

    # Update in database
    await db.user_stories.update_one(
        {"project_id": project_id, "story_id": story_id},
        {"$set": update_data}
    )

    # Retrieve and return the updated story
    updated_story = await db.user_stories.find_one({
        "project_id": project_id,
        "story_id": story_id
    })

    return updated_story
