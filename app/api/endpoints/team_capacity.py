# app/api/endpoints/team_capacity.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.team_capacity import TeamCapacityCreate, TeamCapacityUpdate, TeamCapacityResponse
from app.services.database import get_database

router = APIRouter()


@router.post("/", response_model=TeamCapacityResponse, status_code=status.HTTP_201_CREATED)
async def create_team_capacity(
        capacity: TeamCapacityCreate,
        db=Depends(get_database)
):
    """Create a new team capacity entry."""
    from datetime import datetime

    # Check if project and sprint exist
    project = await db.projects.find_one({"project_id": capacity.project_id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not found"
        )

    sprint = await db.sprint_progress.find_one({
        "project_id": capacity.project_id,
        "sprint_id": capacity.sprint_id
    })

    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sprint not found"
        )

    # Check if capacity already exists for this team member in the sprint
    existing_capacity = await db.team_capacity.find_one({
        "project_id": capacity.project_id,
        "sprint_id": capacity.sprint_id,
        "team_member": capacity.team_member
    })

    if existing_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Capacity already exists for this team member in this sprint"
        )

    # Calculate remaining hours
    capacity_data = capacity.dict()
    capacity_data["remaining_hours"] = capacity.available_hours - capacity.allocated_hours
    capacity_data["created_at"] = datetime.utcnow()
    capacity_data["updated_at"] = datetime.utcnow()

    # Insert into database
    result = await db.team_capacity.insert_one(capacity_data)

    # Retrieve and return the created capacity
    created_capacity = await db.team_capacity.find_one({"_id": result.inserted_id})

    return created_capacity


@router.get("/", response_model=List[TeamCapacityResponse])
async def get_team_capacities(
        project_id: Optional[str] = None,
        sprint_id: Optional[str] = None,
        team_member: Optional[str] = None,
        db=Depends(get_database)
):
    """Get all team capacities with optional filters."""
    # Build query filters
    query = {}
    if project_id:
        query["project_id"] = project_id
    if sprint_id:
        query["sprint_id"] = sprint_id
    if team_member:
        query["team_member"] = team_member

    # Retrieve capacities
    capacities = await db.team_capacity.find(query).to_list(length=100)

    return capacities


@router.get("/{capacity_id}", response_model=TeamCapacityResponse)
async def get_team_capacity(
        capacity_id: str,
        db=Depends(get_database)
):
    """Get a specific team capacity by ID."""
    from bson import ObjectId

    # Retrieve capacity
    capacity = await db.team_capacity.find_one({"_id": ObjectId(capacity_id)})
    if not capacity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team capacity not found"
        )

    return capacity


@router.put("/{capacity_id}", response_model=TeamCapacityResponse)
async def update_team_capacity(
        capacity_id: str,
        capacity_update: TeamCapacityUpdate,
        db=Depends(get_database)
):
    """Update a team capacity."""
    from datetime import datetime
    from bson import ObjectId

    # Check if capacity exists
    existing_capacity = await db.team_capacity.find_one({"_id": ObjectId(capacity_id)})
    if not existing_capacity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team capacity not found"
        )

    # Update fields
    update_data = capacity_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    # Calculate remaining hours if available or allocated hours changed
    if "available_hours" in update_data or "allocated_hours" in update_data:
        available = update_data.get("available_hours", existing_capacity["available_hours"])
        allocated = update_data.get("allocated_hours", existing_capacity["allocated_hours"])
        update_data["remaining_hours"] = available - allocated

    # Update in database
    await db.team_capacity.update_one(
        {"_id": ObjectId(capacity_id)},
        {"$set": update_data}
    )

    # Retrieve and return the updated capacity
    updated_capacity = await db.team_capacity.find_one({"_id": ObjectId(capacity_id)})

    return updated_capacity


@router.delete("/{capacity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_capacity(
        capacity_id: str,
        db=Depends(get_database)
):
    """Delete a team capacity."""
    from bson import ObjectId

    # Delete capacity
    result = await db.team_capacity.delete_one({"_id": ObjectId(capacity_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team capacity not found"
        )

    return None
