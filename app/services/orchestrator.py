# app/services/orchestrator.py - Corrected orchestrator (partial)
import logging
import json
from datetime import datetime
from redis import Redis
from app.config import settings
from app.models.scheduled_call import ScheduledCallModel
from app.models.sprint_call import SprintCallModel, BlockerItem, DelayItem
from app.services.database import get_database
from app.services.platform import connect_to_meeting

# Import agent classes
from app.agents.driving_call import DrivingCallAgent
from app.agents.user_validation import UserValidationAgent
from app.agents.blocker import BlockerAgent
from app.agents.critic import CriticAgent
from app.agents.missing_developer import MissingDeveloperAgent
from app.agents.overall import OverallAgent
from app.agents.mom import MOMAgent
from app.agents.current_status import CurrentStatusAgent

logger = logging.getLogger(__name__)


async def orchestrate_call(scheduled_call: ScheduledCallModel):
    """Orchestrate the entire call process."""
    logger.info(f"Starting call orchestration for {scheduled_call.team_name}")
    call_id = str(scheduled_call.id)

    try:
        # Initialize Redis for inter-agent communication
        redis = Redis(
            host=settings.REDIS.HOST,
            port=settings.REDIS.PORT,
            password=settings.REDIS.PASSWORD,
            db=settings.REDIS.DB
        )

        # Create a session for this call
        redis.set(f"call:{call_id}:status", "initializing", ex=3600)  # 1-hour expiry

        # Connect to the meeting platform
        meeting_session = await connect_to_meeting(scheduled_call)
        logger.info(f"Connected to meeting platform: {scheduled_call.platform}")

        # Initialize all agents
        agents = await initialize_agents(scheduled_call, meeting_session, call_id, redis)

        # Start the driving call agent
        redis.set(f"call:{call_id}:status", "in-progress", ex=3600)
        call_results = await agents["driving_call"].start_call()

        # Process results through the overall agent
        overall_summary = await agents["overall"].process_summary(call_results)

        # Generate MOM and status reports
        mom_report = await agents["mom"].generate_mom(overall_summary)
        status_report = await agents["current_status"].generate_status_report(overall_summary)

        # Store results in database
        await store_call_results(scheduled_call, overall_summary, mom_report, status_report)

        # Clean up Redis
        redis.delete(f"call:{call_id}:status")
        redis.delete(f"call:{call_id}:data")

        logger.info(f"Call orchestration completed for {scheduled_call.team_name}")
        return {"mom_report": mom_report, "status_report": status_report}

    except Exception as e:
        logger.error(f"Call orchestration failed: {str(e)}")
        raise


async def initialize_agents(scheduled_call, meeting_session, call_id, redis):
    """Initialize all agent instances."""
    # Fetch necessary data for agents
    db = get_database()
    project_data = await db.projects.find_one({"project_name": scheduled_call.project_name})
    team_members = await db.contact_details.find({"team_name": scheduled_call.team_name}).to_list(length=100)

    # Current sprint data
    now = datetime.utcnow()
    current_sprint = await db.sprint_progress.find_one({
        "project_id": project_data["project_id"],
        "start_date": {"$lte": now},
        "end_date": {"$gte": now}
    })

    # User stories for current sprint
    user_stories = await db.user_stories.find({
        "project_id": project_data["project_id"],
        "sprint_id": current_sprint["sprint_id"]
    }).to_list(length=1000)

    # Blockers
    blockers = await db.blockers.find({
        "project_id": project_data["project_id"],
        "status": "Open"
    }).to_list(length=1000)

    # Create agents
    driving_call_agent = DrivingCallAgent(
        scheduled_call,
        meeting_session,
        call_id,
        redis,
        user_stories,
        team_members,
        blockers,
        current_sprint,
        scheduled_call.aggressiveness_level
    )

    user_validation_agent = UserValidationAgent(call_id, redis)
    blocker_agent = BlockerAgent(call_id, redis, project_data["project_id"])
    critic_agent = CriticAgent(call_id, redis)
    missing_developer_agent = MissingDeveloperAgent(call_id, redis, team_members)
    overall_agent = OverallAgent(call_id, redis)
    mom_agent = MOMAgent(
        scheduled_call.team_name,
        scheduled_call.project_name,
        call_id,
        redis,
        team_members
    )
    current_status_agent = CurrentStatusAgent(
        call_id,
        redis,
        current_sprint,
        user_stories
    )

    # Set up agent relationships
    driving_call_agent.set_user_validation_agent(user_validation_agent)
    user_validation_agent.set_blocker_agent(blocker_agent)
    user_validation_agent.set_critic_agent(critic_agent)
    user_validation_agent.set_missing_developer_agent(missing_developer_agent)
    overall_agent.set_mom_agent(mom_agent)
    overall_agent.set_current_status_agent(current_status_agent)

    return {
        "driving_call": driving_call_agent,
        "user_validation": user_validation_agent,
        "blocker": blocker_agent,
        "critic": critic_agent,
        "missing_developer": missing_developer_agent,
        "overall": overall_agent,
        "mom": mom_agent,
        "current_status": current_status_agent,
    }


async def store_call_results(scheduled_call, overall_summary, mom_report, status_report):
    """Store call results in database."""
    db = get_database()

    sprint_call = SprintCallModel(
        project_name=scheduled_call.project_name,
        team_name=scheduled_call.team_name,
        date_time=datetime.utcnow(),
        scrum_summary=overall_summary["summary"],
        participants=overall_summary["participants"],
        missing_participants=overall_summary["missing_participants"],
        blockers=[BlockerItem(**blocker) for blocker in overall_summary["blockers"]],
        delays=[DelayItem(**delay) for delay in overall_summary["delays"]]
    )

    result = await db.sprint_calls.insert_one(sprint_call.dict(by_alias=True))
    sprint_call_id = result.inserted_id

    logger.info(f"Saved sprint call results to database with ID: {sprint_call_id}")

    return sprint_call_id
