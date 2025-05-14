# app/utils/mongodb.py - MongoDB utility functions
from typing import Dict, List, Any

def convert_mongo_id(document: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB _id to id field."""
    if document and "_id" in document:
        document["id"] = str(document.pop("_id"))
    return document

def convert_mongo_ids(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert MongoDB _id to id field for a list of documents."""
    return [convert_mongo_id(doc) for doc in documents]