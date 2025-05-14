# app/api/endpoints/velocity.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.velocity import VelocityHistoryCreate, VelocityHistoryUpdate, VelocityHistoryResponse
from app.services.database import get_database
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/", response_model=VelocityHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_velocity_history(
        velocity: VelocityHistoryCreate,
        current_user: dict = Depends(get_current_user),
        db=Depends(get_database)
):
    """Create a new velocity history entry."""
    from datetime import datetime

    # Check if project exists
    project = await db.projects.find_one({"project_id": velocity.project_id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not found"
        )

    # Check if velocity already exists for this sprint
    existing_velocity = await db.velocity_history.find_one({
        "project_id": velocity.project_id,
        "sprint_id": velocity.sprint_id
    })

    if existing_velocity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Velocity history already exists for this sprint"
        )

    # Create a new velocity entry
    velocity_data = velocity.dict()

    # Calculate velocity and deviation if not provided
    if velocity_data["story_points_committed"] > 0:
        velocity_data["velocity"] = velocity_data["story_points_completed"] / velocity_data["story_points_committed"]
        velocity_data["deviation"] = ((velocity_data["story_points_completed"] - velocity_data[
            "story_points_committed"]) / velocity_data["story_points_committed"]) * 100
    else:
        velocity_data["velocity"] = 0
        velocity_data["deviation"] = 0

    velocity_data["created_at"] = datetime.utcnow()
    velocity_data["updated_at"] = datetime.utcnow()

    # Insert into database
    result = await db.velocity_history.insert_one(velocity_data)

    # Retrieve and return the created velocity
    created_velocity = await db.velocity_history.find_one({"_id": result.inserted_id})

    return created_velocity


@router.get("/", response_model=List[VelocityHistoryResponse])
async def get_velocity_history(
        project_id: Optional[str] = None,
        sprint_id: Optional[str] = None,
        current_user: dict = Depends(get_current_user),
        db=Depends(get_database)
):
    """Get all velocity history with optional filters."""
    # Build query filters
    query = {}
    if project_id:
        query["project_id"] = project_id
    if sprint_id:
        query["sprint_id"] = sprint_id

    # Retrieve velocity history
    velocities = await db.velocity_history.find(query).sort("_id", -1).to_list(length=100)

    return velocities


@router.get("/{velocity_id}", response_model=VelocityHistoryResponse)
async def get_velocity_history_entry(
        velocity_id: str,
        current_user: dict = Depends(get_current_user),
        db=Depends(get_database)
):
    """Get a specific velocity history entry by ID."""
    from bson import ObjectId

    # Retrieve velocity
    velocity = await db.velocity_history.find_one({"_id": ObjectId(velocity_id)})
    if not velocity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Velocity history not found"
        )

    return velocity


@router.get("/average/{project_id}", response_model=dict)
async def get_average_velocity(
        project_id: str,
        num_sprints: int = 3,
        current_user: dict = Depends(get_current_user),
        db=Depends(get_database)
):
    """Get average velocity for a project over the last N sprints."""
    # Get the last N sprint velocities
    velocities = await db.velocity_history.find({
        "project_id": project_id
    }).sort("_id", -1).limit(num_sprints).to_list(length=num_sprints)

    if not velocities:
        return {
            "project_id": project_id,
            "average_velocity": 0,
            "average_deviation": 0,
            "num_sprints": 0
        }

    # Calculate averages
    avg_velocity = sum(v["velocity"] for v in velocities) / len(velocities)
    avg_deviation = sum(v["deviation"] for v in velocities) / len(velocities)

    return {
        "project_id": project_id,
        "average_velocity": avg_velocity,
        "average_deviation": avg_deviation,
        "num_sprints": len(velocities)
    }


@router.put("/{velocity_id}", response_model=VelocityHistoryResponse)
async def update_velocity_history(
        velocity_id: str,
        velocity_update: VelocityHistoryUpdate,
        current_user: dict = Depends(get_current_user),
        db=Depends(get_database)
):
    """Update a velocity history entry."""
    from datetime import datetime
    from bson import ObjectId

    # Check if velocity exists
    existing_velocity = await db.velocity_history.find_one({"_id": ObjectId(velocity_id)})
    if not existing_velocity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Velocity history not found"
        )

    # Update fields
    update_data = velocity_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    # Recalculate velocity and deviation if story points changed
    if "story_points_committed" in update_data or "story_points_completed" in update_data:
        committed = update_data.get("story_points_committed", existing_velocity["story_points_committed"])
        completed = update_data.get("story_points_completed", existing_velocity["story_points_completed"])

        if committed > 0:
            update_data["velocity"] = completed / committed
            update_data["deviation"] = ((completed - committed) / committed) * 100
        else:
            update_data["velocity"] = 0
            update_data["deviation"] = 0

    # Update in database
    await db.velocity_history.update_one(
        {"_id": ObjectId(velocity_id)},
        {"$set": update_data}
    )

    # Retrieve and return the updated velocity
    updated_velocity = await db.velocity_history.find_one({"_id": ObjectId(velocity_id)})

    return updated_velocity


@router.delete("/{velocity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_velocity_history(
        velocity_id: str,
        current_user: dict = Depends(get_current_user),
        db=Depends(get_database)
):
    """Delete a velocity history entry."""
    from bson import ObjectId

    # Delete velocity
    result = await db.velocity_history.delete_one({"_id": ObjectId(velocity_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Velocity history not found"
        )

    return None
