# app/agents/user_validation.py
import logging
import json
from datetime import datetime
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class UserValidationAgent(BaseAgent):
    """Agent responsible for validating user responses during scrum calls."""

    def __init__(self, call_id, redis_client):
        """Initialize the user validation agent.

        Args:
            call_id: Unique identifier for the call.
            redis_client: Redis client for inter-agent communication.
        """
        super().__init__(call_id, redis_client)
        self.blocker_agent = None
        self.critic_agent = None
        self.missing_developer_agent = None

    def set_blocker_agent(self, agent):
        """Set the blocker agent.

        Args:
            agent: BlockerAgent instance.
        """
        self.blocker_agent = agent

    def set_critic_agent(self, agent):
        """Set the critic agent.

        Args:
            agent: CriticAgent instance.
        """
        self.critic_agent = agent

    def set_missing_developer_agent(self, agent):
        """Set the missing developer agent.

        Args:
            agent: MissingDeveloperAgent instance.
        """
        self.missing_developer_agent = agent

    async def process(self, response_data):
        """Process a user response.

        Args:
            response_data: Dictionary containing the response data.
                {
                    "team_member": str,
                    "response": str,
                    "timestamp": str (ISO format)
                }

        Returns:
            dict: Processed result with metadata about the response.
                {
                    "team_member": str,
                    "response": str,
                    "timestamp": str,
                    "has_blocker": bool,
                    "blocker": dict (if has_blocker is True),
                    "has_delay": bool,
                    "delay": dict (if has_delay is True),
                    "is_relevant": bool
                }
        """
        try:
            logger.info(f"Processing response from {response_data['team_member']}")

            # Analyze the response using OpenAI
            analysis = await self._analyze_response(response_data["response"])

            # Create result dictionary
            result = {
                "team_member": response_data["team_member"],
                "response": response_data["response"],
                "timestamp": response_data["timestamp"],
                "has_blocker": analysis["has_blocker"],
                "has_delay": analysis["has_delay"],
                "is_relevant": analysis["is_relevant"]
            }

            # Process blocker if detected
            if analysis["has_blocker"] and self.blocker_agent:
                blocker_info = {
                    "team_member": response_data["team_member"],
                    "description": analysis["blocker_description"],
                    "timestamp": datetime.utcnow().isoformat()
                }
                blocker_result = await self.blocker_agent.process(blocker_info)
                result["blocker"] = blocker_result

            # Process delay if detected
            if analysis["has_delay"] and self.critic_agent:
                delay_info = {
                    "team_member": response_data["team_member"],
                    "description": analysis["delay_description"],
                    "timestamp": datetime.utcnow().isoformat()
                }
                delay_result = await self.critic_agent.process(delay_info)
                result["delay"] = delay_result

            # Store the processed result
            await self.store_data(f"processed_response:{response_data['team_member']}", result)

            logger.info(f"Processed response from {response_data['team_member']}: " +
                        f"blocker={result['has_blocker']}, delay={result['has_delay']}, " +
                        f"relevant={result['is_relevant']}")

            return result

        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            # Return a basic result in case of error
            return {
                "team_member": response_data["team_member"],
                "response": response_data["response"],
                "timestamp": response_data["timestamp"],
                "has_blocker": False,
                "has_delay": False,
                "is_relevant": True,
                "error": str(e)
            }

    async def _analyze_response(self, response_text):
        """Analyze a response using OpenAI.

        Args:
            response_text: The text of the response.

        Returns:
            dict: Analysis results.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": """
            You are an AI assistant analyzing daily standup responses from team members.
            Your job is to extract key information and detect:
            1. Blockers - issues that are preventing progress
            2. Delays - tasks that are taking longer than expected
            3. Whether the response is relevant to the standup (discussing work, blockers, etc.)

            Provide a structured analysis in JSON format with the following fields:
            - has_blocker: boolean (true if a blocker is mentioned)
            - blocker_description: string (description of the blocker, if any)
            - has_delay: boolean (true if a delay is mentioned)
            - delay_description: string (description of the delay, if any)
            - is_relevant: boolean (true if the response is relevant to the standup)

            Examples of blockers:
            - "I'm blocked by the API team"
            - "I can't proceed until the database is set up"
            - "Waiting for credentials from DevOps"

            Examples of delays:
            - "The task is taking longer than expected"
            - "I need another day to complete this"
            - "I won't be able to finish by the end of the sprint"

            A relevant response discusses work completed, in progress, or planned, or mentions blockers.
            An irrelevant response doesn't provide update on work (e.g., "I have nothing to report").
            """
             },
            {"role": "user", "content": f"Analyze this standup response:\n\n{response_text}"}
        ]

        # Call OpenAI
        analysis_text = await self.call_openai(messages, max_tokens=500)

        # Parse JSON response
        try:
            # Find JSON object in response (sometimes the model adds text around the JSON)
            import re
            json_match = re.search(r'(\{.*\})', analysis_text, re.DOTALL)
            if json_match:
                analysis_json = json_match.group(1)
                analysis = json.loads(analysis_json)
            else:
                # Fallback: try to parse the entire response as JSON
                analysis = json.loads(analysis_text)

            # Ensure all expected fields are present
            required_fields = ["has_blocker", "blocker_description", "has_delay", "delay_description", "is_relevant"]
            for field in required_fields:
                if field not in analysis:
                    if field.startswith("has_") or field == "is_relevant":
                        analysis[field] = False
                    else:
                        analysis[field] = ""

            return analysis

        except json.JSONDecodeError:
            logger.error(f"Failed to parse analysis as JSON: {analysis_text}")
            # Return default analysis
            return {
                "has_blocker": False,
                "blocker_description": "",
                "has_delay": False,
                "delay_description": "",
                "is_relevant": True
            }
