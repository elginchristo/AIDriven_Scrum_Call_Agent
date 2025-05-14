# app/api/endpoints/reports.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.sprint_call import SprintCallResponse
from app.services.database import get_database

router = APIRouter()


@router.get("/sprint-calls/", response_model=List[SprintCallResponse])
async def get_sprint_calls(
        team_name: Optional[str] = None,
        project_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db=Depends(get_database)
):
    """Get all sprint call reports with optional filters."""
    from datetime import datetime

    # Build query filters
    query = {}
    if team_name:
        query["team_name"] = team_name
    if project_name:
        query["project_name"] = project_name

    # Add date filters if provided
    date_filter = {}
    if start_date:
        date_filter["$gte"] = datetime.fromisoformat(start_date)
    if end_date:
        date_filter["$lte"] = datetime.fromisoformat(end_date)
    if date_filter:
        query["date_time"] = date_filter

    # Retrieve sprint calls
    sprint_calls = await db.sprint_calls.find(query).sort("date_time", -1).to_list(length=100)

    # Convert to response models
    return [SprintCallResponse(**call) for call in sprint_calls]


@router.get("/sprint-calls/{call_id}", response_model=SprintCallResponse)
async def get_sprint_call(
        call_id: str,
        db=Depends(get_database)
):
    """Get a specific sprint call report by ID."""
    from bson import ObjectId

    # Retrieve sprint call
    sprint_call = await db.sprint_calls.find_one({"_id": ObjectId(call_id)})
    if not sprint_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint call report not found"
        )

    return SprintCallResponse(**sprint_call)


@router.get("/latest-status/{team_name}")
async def get_latest_status(
        team_name: str,
        db=Depends(get_database)
):
    """Get the latest status report for a team."""
    # Retrieve the latest sprint call for the team
    latest_call = await db.sprint_calls.find_one(
        {"team_name": team_name},
        sort=[("date_time", -1)]
    )

    if not latest_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sprint calls found for the team"
        )

    call_id = str(latest_call["_id"])

    # Retrieve the status report
    status_key = f"call:{call_id}:status_report"
    status_report = await db.redis_data.find_one({"key": status_key})

    if not status_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status report not found for the latest call"
        )

    return status_report["data"]
