# app/agents/missing_developer.py
import logging
from datetime import datetime
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MissingDeveloperAgent(BaseAgent):
    """Agent responsible for tracking missing developers during scrum calls."""

    def __init__(self, call_id, redis_client, team_members):
        """Initialize the missing developer agent.

        Args:
            call_id: Unique identifier for the call.
            redis_client: Redis client for inter-agent communication.
            team_members: List of team members.
        """
        super().__init__(call_id, redis_client)
        self.team_members = team_members

    async def process(self, missing_member_name):
        """Process a missing developer.

        Args:
            missing_member_name: Name of the missing team member.

        Returns:
            dict: Missing developer data.
                {
                    "name": str,
                    "email": str,
                    "timestamp": str (ISO format),
                    "consecutive_misses": int,
                    "last_attendance": str or None (ISO format),
                    "action_required": bool,
                    "suggested_action": str
                }
        """
        try:
            logger.info(f"Processing missing developer: {missing_member_name}")

            # Find the team member in the team members list
            team_member = next((member for member in self.team_members
                                if member["name"].lower() == missing_member_name.lower()), None)

            if not team_member:
                logger.warning(f"Team member not found: {missing_member_name}")
                # Create a default team member record
                team_member = {
                    "name": missing_member_name,
                    "email": f"{missing_member_name.lower().replace(' ', '.')}@example.com"
                }

            # Check if we have previous data about this team member
            previous_data = await self.retrieve_data(f"missing_developer:{missing_member_name}")

            # Create result dictionary
            result = {
                "name": missing_member_name,
                "email": team_member.get("email", ""),
                "timestamp": datetime.utcnow().isoformat(),
                "consecutive_misses": 1,
                "last_attendance": None,
                "action_required": False,
                "suggested_action": ""
            }

            # Update with previous data if available
            if previous_data:
                result["consecutive_misses"] = previous_data["consecutive_misses"] + 1
                result["last_attendance"] = previous_data["last_attendance"]

            # Determine if action is required
            if result["consecutive_misses"] >= 2:
                result["action_required"] = True
                result["suggested_action"] = await self._generate_suggested_action(result)

            # Store the processed data
            await self.store_data(f"missing_developer:{missing_member_name}", result)

            logger.info(f"Processed missing developer: {missing_member_name}, " +
                        f"consecutive misses: {result['consecutive_misses']}, " +
                        f"action required: {result['action_required']}")

            return result

        except Exception as e:
            logger.error(f"Error processing missing developer: {str(e)}")
            # Return a basic result in case of error
            return {
                "name": missing_member_name,
                "email": "",
                "timestamp": datetime.utcnow().isoformat(),
                "consecutive_misses": 1,
                "last_attendance": None,
                "action_required": False,
                "suggested_action": "",
                "error": str(e)
            }

    async def _generate_suggested_action(self, missing_data):
        """Generate a suggested action for a missing developer.

        Args:
            missing_data: Missing developer data.

        Returns:
            str: Suggested action.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": f"""
            You are an AI Scrum Master assistant tracking attendance in daily standups.

            Team member {missing_data['name']} has missed {missing_data['consecutive_misses']} consecutive standup meetings.

            Generate a brief, professional recommendation for follow-up action. Consider:
            - If they've missed 2 meetings, suggest a friendly check-in
            - If they've missed 3 meetings, suggest notifying their manager
            - If they've missed 4+ meetings, suggest escalation to the project lead

            Keep the suggestion concise and professional (1-2 sentences).
            """
             },
            {"role": "user",
             "content": f"Suggest follow-up action for {missing_data['name']} who has missed {missing_data['consecutive_misses']} consecutive standup meetings."}
        ]

        # Call OpenAI
        return await self.call_openai(messages, max_tokens=150)
