# app/api/endpoints/projects.py
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.database import get_database
from app.utils.security import get_current_user

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
        project: ProjectCreate,
        current_user: dict = Depends(get_current_user),
        db=Depends(get_database)
):
    """Create a new project."""
    from datetime import datetime

    # Check if project with same ID or key already exists
    existing_project = await db.projects.find_one({
        "$or": [
            {"project_id": project.project_id},
            {"project_key": project.project_key}
        ]
    })

    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this ID or key already exists"
        )

    # Create a new project
    project_data = project.dict()
    project_data["created_at"] = datetime.utcnow()
    project_data["updated_at"] = datetime.utcnow()

    # Insert into database
    result = await db.projects.insert_one(project_data)

    # Retrieve and return the created project
    created_project = await db.projects.find_one({"_id": result.inserted_id})

    return created_project


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
        project_name: Optional[str] = None,
        project_type: Optional[str] = None,
        current_user: dict = Depends(get_current_user),
        db=Depends(get_database)
):
    """Get all projects with optional filters."""
    # Build query filters
    query = {}
    if project_name:
        query["project_name"] = {"$regex": project_name, "$options": "i"}
    if project_type:
        query["project_type"] = project_type

    # Retrieve projects
    projects = await db.projects.find(query).to_list(length=100)

    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
        project_id: str,
        current_user: dict = Depends(get_current_user),
        db=Depends(get_database)
):
    """Get a specific project by ID."""
    # Retrieve project
    project = await db.projects.find_one({"project_id": project_id})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
        project_id: str,
        project_update: ProjectUpdate,
        current_user: dict = Depends(get_current_user),
        db=Depends(get_database)
):
    """Update a project."""
    from datetime import datetime

    # Check if project exists
    existing_project = await db.projects.find_one({"project_id": project_id})
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Update fields
    update_data = project_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    # Update in database
    await db.projects.update_one(
        {"project_id": project_id},
        {"$set": update_data}
    )

    # Retrieve and return the updated project
    updated_project = await db.projects.find_one({"project_id": project_id})

    return updated_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
        project_id: str,
        current_user: dict = Depends(get_current_user),
        db=Depends(get_database)
):
    """Delete a project."""
    # Delete project
    result = await db.projects.delete_one({"project_id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return None
