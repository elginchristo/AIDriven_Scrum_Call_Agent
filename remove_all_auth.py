# remove_all_auth.py - Remove authentication from all files
import os
import re


def remove_auth_from_file(filepath):
    """Remove authentication dependencies from a Python file."""

    with open(filepath, 'r') as f:
        content = f.read()

    # Remove authentication imports
    content = re.sub(r'from app\.utils\.security import get_current_user.*\n', '', content)
    content = re.sub(r'from app\.dependencies import get_current_user.*\n', '', content)

    # Remove authentication parameters from functions
    content = re.sub(r',?\s*current_user[^,\)]*=\s*Depends\(get_current_user\)', '', content)
    content = re.sub(r',?\s*current_user:\s*dict\s*=\s*Depends\(get_current_user\)', '', content)

    # Replace db dependencies
    content = re.sub(r'db=Depends\(get_database\)', 'db=Depends(get_database)', content)

    # Save the modified content
    with open(filepath, 'w') as f:
        f.write(content)

    print(f"✓ Removed auth from {filepath}")


def main():
    """Remove authentication from all API endpoints."""
    print("🔓 Removing authentication from all API endpoints")
    print("=" * 50)

    # List of files to modify
    endpoint_files = [
        "app/api/endpoints/projects.py",
        "app/api/endpoints/sprints.py",
        "app/api/endpoints/stories.py",
        "app/api/endpoints/contacts.py",
        "app/api/endpoints/schedules.py",
        "app/api/endpoints/reports.py",
        "app/api/endpoints/team_capacity.py",
        "app/api/endpoints/velocity.py"
    ]

    # Process each file
    for filepath in endpoint_files:
        if os.path.exists(filepath):
            remove_auth_from_file(filepath)
        else:
            print(f"⚠️ File not found: {filepath}")

    # Update dependencies.py
    deps_content = '''# app/dependencies.py - Version without any authentication
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.database import get_database
from app.config import settings

# Simple database dependency
async def get_db():
    """Get database instance."""
    return get_database()

# Settings dependency
def get_settings():
    """Get application settings."""
    return settings

# Pagination parameters
def get_pagination_params(skip: int = 0, limit: int = 100):
    """Common pagination parameters."""
    return {
        "skip": max(0, skip),
        "limit": min(1000, limit)
    }
'''

    with open("app/dependencies.py", 'w') as f:
        f.write(deps_content)
    print("✓ Updated app/dependencies.py")

    print("\n✅ Authentication removed from all endpoints!")
    print("\nNow restart your API server:")
    print("1. Stop the current server (Ctrl+C)")
    print("2. Start it again: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()