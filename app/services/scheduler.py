# app/services/scheduler.py - Fixed async handling
import logging
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.executors.asyncio import AsyncIOExecutor
from pymongo import MongoClient
from app.config import settings

logger = logging.getLogger(__name__)


def initialize_scheduler():
    """Initialize APScheduler."""
    logger.info("Initializing scheduler...")

    # Create a direct MongoDB connection for APScheduler
    mongo_client = MongoClient(settings.DATABASE.MONGO_URI)
    db = mongo_client[settings.DATABASE.DATABASE_NAME]

    # Set up job stores
    job_stores = {
        'default': MongoDBJobStore(database=settings.DATABASE.DATABASE_NAME,
                                   collection='scheduler_jobs',
                                   client=mongo_client)
    }

    # Set up executors - use AsyncIOExecutor for async jobs
    executors = {
        'default': AsyncIOExecutor(),
        'threadpool': ThreadPoolExecutor(20)
    }

    # Set up job defaults
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }

    # Create scheduler
    scheduler = AsyncIOScheduler(
        jobstores=job_stores,
        executors=executors,
        job_defaults=job_defaults,
        timezone='UTC'
    )

    # Schedule job to check for due calls
    scheduler.add_job(
        check_scheduled_calls,
        'interval',
        minutes=1,
        id='check_scheduled_calls',
        replace_existing=True,
        executor='default'  # Use the async executor
    )

    logger.info("Scheduler initialized")
    return scheduler


async def check_scheduled_calls():
    """Check for scheduled calls that are due."""
    logger.info("Checking for scheduled calls...")

    # Import here to avoid circular imports
    from app.services.database import get_database
    from app.models.scheduled_call import CallStatus

    # Get current time
    now = datetime.utcnow()

    # Get database
    db = get_database()

    try:
        # Find due scheduled calls
        cursor = db.scheduled_calls.find({
            "status": "scheduled",
            "scheduled_time": {"$lte": now}
        })

        # Convert cursor to list
        scheduled_calls = await cursor.to_list(length=100)

        logger.info(f"Found {len(scheduled_calls)} due calls")

        if len(scheduled_calls) == 0:
            return

        # Process each due call
        for call_data in scheduled_calls:
            try:
                logger.info(f"Processing scheduled call: {call_data.get('_id')}")

                # Update call status to in-progress
                await db.scheduled_calls.update_one(
                    {"_id": call_data["_id"]},
                    {"$set": {
                        "status": "in-progress",
                        "last_run": now,
                        "updated_at": now
                    }}
                )

                # For now, just log that we would process the call
                logger.info(f"Would orchestrate call for team: {call_data.get('team_name')}")

                # Update call status to completed (for testing)
                update_data = {
                    "status": "completed",
                    "updated_at": datetime.utcnow()
                }

                # If recurring, schedule next run
                if call_data.get('is_recurring'):
                    next_run = calculate_next_run(call_data.get('recurring_pattern'))
                    update_data.update({
                        "status": "scheduled",
                        "scheduled_time": next_run,
                        "next_run": next_run
                    })
                    logger.info(f"Next run scheduled for: {next_run}")

                await db.scheduled_calls.update_one(
                    {"_id": call_data["_id"]},
                    {"$set": update_data}
                )

            except Exception as e:
                logger.error(f"Error processing scheduled call {call_data.get('_id')}: {str(e)}")
                # Update call status to failed
                await db.scheduled_calls.update_one(
                    {"_id": call_data["_id"]},
                    {"$set": {
                        "status": "failed",
                        "updated_at": datetime.utcnow(),
                        "error": str(e)
                    }}
                )

    except Exception as e:
        logger.error(f"Error checking scheduled calls: {str(e)}")


def calculate_next_run(cron_pattern):
    """Calculate next run time based on cron pattern."""
    try:
        from croniter import croniter
        base = datetime.utcnow()
        cron = croniter(cron_pattern, base)
        return cron.get_next(datetime)
    except Exception as e:
        logger.error(f"Error calculating next run: {str(e)}")
        # Default to next day same time
        return datetime.utcnow() + timedelta(days=1)