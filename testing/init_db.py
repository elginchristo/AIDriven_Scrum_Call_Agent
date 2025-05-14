# init_db.py - Complete database initialization script
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_indexes(db):
    """Create all necessary indexes for optimal performance."""
    logger.info("Creating database indexes...")

    # Projects collection indexes
    await db.projects.create_index("project_id", unique=True)
    await db.projects.create_index("project_key", unique=True)
    await db.projects.create_index("project_name")
    await db.projects.create_index("created_at")
    logger.info("Created indexes for projects collection")

    # Sprint Progress collection indexes
    await db.sprint_progress.create_index([("project_id", 1), ("sprint_id", 1)], unique=True)
    await db.sprint_progress.create_index("start_date")
    await db.sprint_progress.create_index("end_date")
    await db.sprint_progress.create_index([("project_id", 1), ("start_date", -1)])
    logger.info("Created indexes for sprint_progress collection")

    # User Stories collection indexes
    await db.user_stories.create_index([("project_id", 1), ("story_id", 1)], unique=True)
    await db.user_stories.create_index("assignee")
    await db.user_stories.create_index("status")
    await db.user_stories.create_index([("project_id", 1), ("sprint_id", 1)])
    await db.user_stories.create_index([("assignee", 1), ("status", 1)])
    logger.info("Created indexes for user_stories collection")

    # Blockers collection indexes
    await db.blockers.create_index("project_id")
    await db.blockers.create_index("status")
    await db.blockers.create_index("assignee")
    await db.blockers.create_index([("project_id", 1), ("status", 1)])
    await db.blockers.create_index("blocker_raised_date")
    logger.info("Created indexes for blockers collection")

    # Team Capacity collection indexes
    await db.team_capacity.create_index([("project_id", 1), ("sprint_id", 1), ("team_member", 1)], unique=True)
    await db.team_capacity.create_index("team_member")
    logger.info("Created indexes for team_capacity collection")

    # Velocity History collection indexes
    await db.velocity_history.create_index([("project_id", 1), ("sprint_id", 1)], unique=True)
    await db.velocity_history.create_index("project_id")
    logger.info("Created indexes for velocity_history collection")

    # Contact Details collection indexes
    await db.contact_details.create_index("email", unique=True)
    await db.contact_details.create_index("team_name")
    await db.contact_details.create_index("name")
    logger.info("Created indexes for contact_details collection")

    # Sprint Calls collection indexes
    await db.sprint_calls.create_index([("project_name", 1), ("team_name", 1), ("date_time", -1)])
    await db.sprint_calls.create_index("date_time")
    await db.sprint_calls.create_index("team_name")
    logger.info("Created indexes for sprint_calls collection")

    # Scheduled Calls collection indexes
    await db.scheduled_calls.create_index("scheduled_time")
    await db.scheduled_calls.create_index("status")
    await db.scheduled_calls.create_index([("team_name", 1), ("project_name", 1)])
    await db.scheduled_calls.create_index([("status", 1), ("scheduled_time", 1)])
    logger.info("Created indexes for scheduled_calls collection")

    # Users collection indexes (for authentication)
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
    logger.info("Created indexes for users collection")

    logger.info("All indexes created successfully!")


async def create_initial_data(db):
    """Create initial test data for development."""
    logger.info("Creating initial test data...")

    # Create a test user
    test_user = {
        "_id": "test_user_001",
        "username": "admin",
        "email": "admin@scrumbot.com",
        "full_name": "Admin User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36PQqFDJH7Kd7PoX7yF.3LO",  # password: admin123
        "is_active": True,
        "is_admin": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        await db.users.insert_one(test_user)
        logger.info("Created test user - username: admin, password: admin123")
    except Exception as e:
        logger.warning(f"Test user might already exist: {e}")

    # Create a sample project
    project = {
        "project_id": "DEMO-001",
        "project_key": "DEMO",
        "project_name": "Demo Project",
        "project_type": "Software",
        "project_lead": "Admin User",
        "project_description": "A demo project for testing the Scrum Agent",
        "project_url": "https://demo.scrumbot.com",
        "project_category": "Internal",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        await db.projects.insert_one(project)
        logger.info("Created demo project")
    except Exception as e:
        logger.warning(f"Demo project might already exist: {e}")

    # Create current sprint
    sprint_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    sprint_end = sprint_start + timedelta(days=14)

    sprint = {
        "project_id": "DEMO-001",
        "sprint_id": "SPR-001",
        "sprint_name": "Sprint 1",
        "start_date": sprint_start,
        "end_date": sprint_end,
        "total_story_points": 0,
        "completed_story_points": 0,
        "percent_completion": 0,
        "remaining_story_points": 0,
        "burndown_trend": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        await db.sprint_progress.insert_one(sprint)
        logger.info("Created current sprint")
    except Exception as e:
        logger.warning(f"Sprint might already exist: {e}")

    # Create team members
    team_members = [
        {
            "team_name": "Demo Team",
            "name": "John Doe",
            "email": "john.doe@scrumbot.com",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "team_name": "Demo Team",
            "name": "Jane Smith",
            "email": "jane.smith@scrumbot.com",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "team_name": "Demo Team",
            "name": "Bob Johnson",
            "email": "bob.johnson@scrumbot.com",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "team_name": "Demo Team",
            "name": "Alice Brown",
            "email": "alice.brown@scrumbot.com",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    for member in team_members:
        try:
            await db.contact_details.insert_one(member)
            logger.info(f"Created team member: {member['name']}")
        except Exception as e:
            logger.warning(f"Team member might already exist: {e}")

    # Create user stories
    stories = [
        {
            "project_id": "DEMO-001",
            "sprint_id": "SPR-001",
            "story_id": "DEMO-101",
            "story_title": "Implement voice processing module",
            "assignee": "John Doe",
            "status": "In Progress",
            "priority": "High",
            "story_points": 8,
            "work_item_type": "Story",
            "days_in_current_status": 2,
            "last_status_change_date": datetime.utcnow() - timedelta(days=2),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "project_id": "DEMO-001",
            "sprint_id": "SPR-001",
            "story_id": "DEMO-102",
            "story_title": "Create agent orchestration system",
            "assignee": "Jane Smith",
            "status": "To Do",
            "priority": "High",
            "story_points": 13,
            "work_item_type": "Story",
            "days_in_current_status": 0,
            "last_status_change_date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "project_id": "DEMO-001",
            "sprint_id": "SPR-001",
            "story_id": "DEMO-103",
            "story_title": "Setup database schemas",
            "assignee": "Bob Johnson",
            "status": "Done",
            "priority": "Medium",
            "story_points": 5,
            "work_item_type": "Task",
            "days_in_current_status": 0,
            "last_status_change_date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "project_id": "DEMO-001",
            "sprint_id": "SPR-001",
            "story_id": "DEMO-104",
            "story_title": "Implement JIRA integration",
            "assignee": "Alice Brown",
            "status": "In Progress",
            "priority": "Medium",
            "story_points": 8,
            "work_item_type": "Story",
            "days_in_current_status": 1,
            "last_status_change_date": datetime.utcnow() - timedelta(days=1),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    total_points = 0
    completed_points = 0

    for story in stories:
        try:
            await db.user_stories.insert_one(story)
            logger.info(f"Created user story: {story['story_title']}")
            total_points += story['story_points']
            if story['status'] == 'Done':
                completed_points += story['story_points']
        except Exception as e:
            logger.warning(f"User story might already exist: {e}")

    # Update sprint with story points
    await db.sprint_progress.update_one(
        {"sprint_id": "SPR-001"},
        {
            "$set": {
                "total_story_points": total_points,
                "completed_story_points": completed_points,
                "remaining_story_points": total_points - completed_points,
                "percent_completion": (completed_points / total_points * 100) if total_points > 0 else 0
            }
        }
    )

    # Create team capacity entries
    capacities = [
        {
            "project_id": "DEMO-001",
            "sprint_id": "SPR-001",
            "team_member": "John Doe",
            "available_hours": 80,
            "allocated_hours": 72,
            "remaining_hours": 8,
            "days_off": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "project_id": "DEMO-001",
            "sprint_id": "SPR-001",
            "team_member": "Jane Smith",
            "available_hours": 72,
            "allocated_hours": 64,
            "remaining_hours": 8,
            "days_off": 1,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "project_id": "DEMO-001",
            "sprint_id": "SPR-001",
            "team_member": "Bob Johnson",
            "available_hours": 80,
            "allocated_hours": 40,
            "remaining_hours": 40,
            "days_off": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "project_id": "DEMO-001",
            "sprint_id": "SPR-001",
            "team_member": "Alice Brown",
            "available_hours": 80,
            "allocated_hours": 80,
            "remaining_hours": 0,
            "days_off": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    for capacity in capacities:
        try:
            await db.team_capacity.insert_one(capacity)
            logger.info(f"Created capacity for: {capacity['team_member']}")
        except Exception as e:
            logger.warning(f"Capacity entry might already exist: {e}")

    # Create a sample blocker
    blocker = {
        "project_id": "DEMO-001",
        "blocked_item_id": "DEMO-104",
        "blocked_item_title": "Implement JIRA integration",
        "assignee": "Alice Brown",
        "blocker_description": "Waiting for JIRA API credentials from the client",
        "blocker_raised_date": datetime.utcnow() - timedelta(days=1),
        "blocking_reason": "External dependency",
        "status": "Open",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        await db.blockers.insert_one(blocker)
        logger.info("Created sample blocker")
    except Exception as e:
        logger.warning(f"Blocker might already exist: {e}")

    # Create a scheduled call
    scheduled_call = {
        "team_name": "Demo Team",
        "project_name": "Demo Project",
        "scheduled_time": datetime.utcnow() + timedelta(minutes=30),
        "platform": "zoom",
        "platform_credentials": {
            "username": "demo@scrumbot.com",
            "password": "demo_password"
        },
        "email_credentials": {
            "username": "notifications@scrumbot.com",
            "password": "email_password"
        },
        "aggressiveness_level": 5,
        "status": "scheduled",
        "is_recurring": True,
        "recurring_pattern": "0 10 * * 1-5",  # Every weekday at 10 AM
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        await db.scheduled_calls.insert_one(scheduled_call)
        logger.info("Created scheduled call for 30 minutes from now")
    except Exception as e:
        logger.warning(f"Scheduled call might already exist: {e}")

    logger.info("Initial test data created successfully!")


async def initialize_database():
    """Initialize the database with collections and indexes."""
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.scrum_agent

    logger.info("Connected to MongoDB")

    # Create indexes
    await create_indexes(db)

    # Ask if user wants to create test data
    create_test = input("\nDo you want to create test data? (y/n): ")
    if create_test.lower() == 'y':
        await create_initial_data(db)

    logger.info("\nDatabase initialization complete!")
    logger.info("You can now start the application with: uvicorn app.main:app --reload")

    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(initialize_database())