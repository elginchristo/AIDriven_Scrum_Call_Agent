# create_test_data_simple.py - Create test data without auth concerns
import requests
import json
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime

BASE_URL = "http://localhost:8000"
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "scrum_agent"


async def create_data_directly():
    """Create data directly in MongoDB to bypass API issues."""
    print("🔧 Creating test data directly in MongoDB")
    print("=" * 50)

    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    # Create a test project
    project = {
        "project_id": "DEMO-001",
        "project_key": "DEMO",
        "project_name": "Demo Project",
        "project_type": "Software",
        "project_lead": "John Doe",
        "project_description": "Demo project for testing",
        "project_url": "https://demo.example.com",
        "project_category": "Testing",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        result = await db.projects.insert_one(project)
        print(f"✓ Created project: {project['project_name']}")
        print(f"  ID: {result.inserted_id}")
    except Exception as e:
        print(f"✗ Error creating project: {e}")

    # Create team members
    team_members = [
        {
            "team_name": "Demo Team",
            "name": "John Doe",
            "email": "john@example.com",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "team_name": "Demo Team",
            "name": "Jane Smith",
            "email": "jane@example.com",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    for member in team_members:
        try:
            result = await db.contact_details.insert_one(member)
            print(f"✓ Created team member: {member['name']}")
        except Exception as e:
            print(f"✗ Error creating team member: {e}")

    # Create a sprint
    sprint = {
        "project_id": "DEMO-001",
        "sprint_id": "SPR-001",
        "sprint_name": "Sprint 1",
        "start_date": datetime.utcnow(),
        "end_date": datetime.utcnow().replace(day=datetime.utcnow().day + 14),
        "total_story_points": 0,
        "completed_story_points": 0,
        "percent_completion": 0,
        "remaining_story_points": 0,
        "burndown_trend": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        result = await db.sprint_progress.insert_one(sprint)
        print(f"✓ Created sprint: {sprint['sprint_name']}")
    except Exception as e:
        print(f"✗ Error creating sprint: {e}")

    # Close connection
    client.close()

    print("\n✅ Test data created successfully!")
    print("\nNow test the API:")

    # Test API access
    try:
        response = requests.get(f"{BASE_URL}/api/projects/")
        print(f"\nAPI GET /projects status: {response.status_code}")
        if response.status_code == 200:
            projects = response.json()
            print(f"Found {len(projects)} projects via API")
            for project in projects:
                print(f"  - {project['project_name']} ({project['project_id']})")
    except Exception as e:
        print(f"API error: {e}")


if __name__ == "__main__":
    print("This script will create test data directly in MongoDB")
    print("Make sure MongoDB is running at localhost:27017")

    # Run the async function
    asyncio.run(create_data_directly())