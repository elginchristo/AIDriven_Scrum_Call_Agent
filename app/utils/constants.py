# app/utils/constants.py
"""Constants used throughout the application."""

# Meeting platforms
PLATFORM_ZOOM = "zoom"
PLATFORM_TEAMS = "teams"
PLATFORM_MEET = "meet"

# User story statuses
STATUS_TODO = "To Do"
STATUS_IN_PROGRESS = "In Progress"
STATUS_DONE = "Done"
STATUS_BLOCKED = "Blocked"

# User story priorities
PRIORITY_HIGHEST = "Highest"
PRIORITY_HIGH = "High"
PRIORITY_MEDIUM = "Medium"
PRIORITY_LOW = "Low"
PRIORITY_LOWEST = "Lowest"

# Work item types
WORK_ITEM_STORY = "Story"
WORK_ITEM_TASK = "Task"
WORK_ITEM_BUG = "Bug"
WORK_ITEM_SPIKE = "Spike"

# Blocker statuses
BLOCKER_STATUS_OPEN = "Open"
BLOCKER_STATUS_RESOLVED = "Resolved"

# Sprint health statuses
SPRINT_HEALTH_GOOD = "Good"
SPRINT_HEALTH_MODERATE = "Moderate"
SPRINT_HEALTH_AT_RISK = "At Risk"
SPRINT_HEALTH_CRITICAL = "Critical"

# API routes
API_PREFIX = "/api"
API_V1_STR = "/v1"

# Default aggressiveness level
DEFAULT_AGGRESSIVENESS = 5  # On a scale of 1-10

# Scrum call settings
MAX_RESPONSE_WAIT_TIME = 120  # Maximum wait time for a response in seconds
SILENCE_THRESHOLD = 60  # Time in seconds to consider silence and move on
DEFAULT_CRON_PATTERN = "0 10 * * 1-5"  # Weekdays at 10:00 AM
