# app/api/endpoints/schedules.py - Fixed version
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.scheduled_call import (
    ScheduledCallCreate,
    ScheduledCallUpdate,
    ScheduledCallInDB,
    ScheduledCallResponse
)
from app.services.database import get_database
from app.services.scheduler import calculate_next_run
from app.models.scheduled_call import CallStatus, PlatformType

router = APIRouter()


@router.post("/", response_model=ScheduledCallResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_call(
        call: ScheduledCallCreate,
        db=Depends(get_database)
):
    """Create a new scheduled call."""
    # Check if the scheduled time is in the future
    if call.scheduled_time < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduled time must be in the future"
        )

    # Create a new scheduled call
    call_data = call.dict()
    call_data["status"] = CallStatus.SCHEDULED
    call_data["created_at"] = datetime.utcnow()
    call_data["updated_at"] = datetime.utcnow()

    # Calculate next run if recurring
    if call.is_recurring:
        call_data["next_run"] = calculate_next_run(call.recurring_pattern)

    # Insert into database
    result = await db.scheduled_calls.insert_one(call_data)

    # Retrieve and return the created call
    created_call = await db.scheduled_calls.find_one({"_id": result.inserted_id})
    if not created_call:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created scheduled call"
        )

    # Convert MongoDB document to response model
    created_call["id"] = str(created_call.pop("_id"))
    return created_call


@router.get("/", response_model=List[ScheduledCallResponse])
async def get_scheduled_calls(
        team_name: Optional[str] = None,
        project_name: Optional[str] = None,
        status: Optional[str] = None,
        db=Depends(get_database)
):
    """Get all scheduled calls with optional filters."""
    # Build query filters
    query = {}
    if team_name:
        query["team_name"] = team_name
    if project_name:
        query["project_name"] = project_name
    if status:
        query["status"] = status

    # Retrieve calls
    cursor = db.scheduled_calls.find(query)
    calls = await cursor.to_list(length=100)

    # Convert MongoDB documents to response models
    response_calls = []
    for call in calls:
        call["id"] = str(call.pop("_id"))
        response_calls.append(call)

    return response_calls


@router.get("/{call_id}", response_model=ScheduledCallResponse)
async def get_scheduled_call(
        call_id: str,
        db=Depends(get_database)
):
    """Get a specific scheduled call by ID."""
    from bson import ObjectId

    # Retrieve call
    call = await db.scheduled_calls.find_one({"_id": ObjectId(call_id)})
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled call not found"
        )

    # Convert MongoDB document to response model
    call["id"] = str(call.pop("_id"))
    return call


@router.put("/{call_id}", response_model=ScheduledCallResponse)
async def update_scheduled_call(
        call_id: str,
        call_update: ScheduledCallUpdate,
        db=Depends(get_database)
):
    """Update a scheduled call."""
    from bson import ObjectId

    # Check if the call exists
    existing_call = await db.scheduled_calls.find_one({"_id": ObjectId(call_id)})
    if not existing_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled call not found"
        )

    # Update fields
    update_data = call_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    # Calculate next run if recurring pattern is updated
    if "recurring_pattern" in update_data and update_data.get("is_recurring", existing_call["is_recurring"]):
        update_data["next_run"] = calculate_next_run(update_data["recurring_pattern"])

    # Update in database
    await db.scheduled_calls.update_one(
        {"_id": ObjectId(call_id)},
        {"$set": update_data}
    )

    # Retrieve and return the updated call
    updated_call = await db.scheduled_calls.find_one({"_id": ObjectId(call_id)})

    # Convert MongoDB document to response model
    updated_call["id"] = str(updated_call.pop("_id"))
    return updated_call


@router.delete("/{call_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scheduled_call(
        call_id: str,
        db=Depends(get_database)
):
    """Delete a scheduled call."""
    from bson import ObjectId

    # Delete call
    result = await db.scheduled_calls.delete_one({"_id": ObjectId(call_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled call not found"
        )

    return None