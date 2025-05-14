# app/api/router.py
from fastapi import APIRouter
from app.api.endpoints import projects, sprints, stories, schedules, reports, contacts, team_capacity, velocity

api_router = APIRouter()

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(sprints.router, prefix="/sprints", tags=["sprints"])
api_router.include_router(stories.router, prefix="/stories", tags=["stories"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(team_capacity.router, prefix="/team-capacity", tags=["team-capacity"])
api_router.include_router(velocity.router, prefix="/velocity", tags=["velocity"])
