# app/api/endpoints/contacts.py - Contacts endpoint without authentication
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.contact import ContactDetailsCreate, ContactDetailsUpdate, ContactDetailsResponse
from app.services.database import get_database

router = APIRouter()


@router.post("/", response_model=ContactDetailsResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
        contact: ContactDetailsCreate,
        db=Depends(get_database)
):
    """Create a new contact."""
    from datetime import datetime

    # Check if contact already exists
    existing_contact = await db.contact_details.find_one({
        "email": contact.email
    })

    if existing_contact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact with this email already exists"
        )

    # Create a new contact
    contact_data = contact.dict()
    contact_data["created_at"] = datetime.utcnow()
    contact_data["updated_at"] = datetime.utcnow()

    # Insert into database
    result = await db.contact_details.insert_one(contact_data)

    # Retrieve and return the created contact
    created_contact = await db.contact_details.find_one({"_id": result.inserted_id})

    return created_contact


@router.get("/", response_model=List[ContactDetailsResponse])
async def get_contacts(
        team_name: Optional[str] = None,
        name: Optional[str] = None,
        db=Depends(get_database)
):
    """Get all contacts with optional filters."""
    # Build query filters
    query = {}
    if team_name:
        query["team_name"] = team_name
    if name:
        query["name"] = {"$regex": name, "$options": "i"}

    # Retrieve contacts
    contacts = await db.contact_details.find(query).to_list(length=1000)

    return contacts


@router.get("/{contact_id}", response_model=ContactDetailsResponse)
async def get_contact(
        contact_id: str,
        db=Depends(get_database)
):
    """Get a specific contact by ID."""
    from bson import ObjectId

    # Retrieve contact
    contact = await db.contact_details.find_one({"_id": ObjectId(contact_id)})
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return contact


@router.put("/{contact_id}", response_model=ContactDetailsResponse)
async def update_contact(
        contact_id: str,
        contact_update: ContactDetailsUpdate,
        db=Depends(get_database)
):
    """Update a contact."""
    from datetime import datetime
    from bson import ObjectId

    # Check if contact exists
    existing_contact = await db.contact_details.find_one({"_id": ObjectId(contact_id)})
    if not existing_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    # Update fields
    update_data = contact_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    # Update in database
    await db.contact_details.update_one(
        {"_id": ObjectId(contact_id)},
        {"$set": update_data}
    )

    # Retrieve and return the updated contact
    updated_contact = await db.contact_details.find_one({"_id": ObjectId(contact_id)})

    return updated_contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
        contact_id: str,
        db=Depends(get_database)
):
    """Delete a contact."""
    from bson import ObjectId

    # Delete contact
    result = await db.contact_details.delete_one({"_id": ObjectId(contact_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return None