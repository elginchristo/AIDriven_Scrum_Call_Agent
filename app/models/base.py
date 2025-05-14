# app/models/base.py - Pydantic v2 compatible version
from datetime import datetime
from typing import Optional, Dict, Any, Annotated
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import AfterValidator


def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


PyObjectId = Annotated[ObjectId, AfterValidator(validate_object_id)]


class MongoBaseModel(BaseModel):
    """Base model for MongoDB documents."""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda dt: dt.isoformat(),
        }
    )

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)