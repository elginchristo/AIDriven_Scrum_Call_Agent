# app/agents/critic.py
import logging
from datetime import datetime
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CriticAgent(BaseAgent):
    """Agent responsible for analyzing and addressing delays in work progress."""

    def __init__(self, call_id, redis_client):
        """Initialize the critic agent.

        Args:
            call_id: Unique identifier for the call.
            redis_client: Redis client for inter-agent communication.
        """
        super().__init__(call_id, redis_client)

    async def process(self, delay_info):
        """Process a delay.

        Args:
            delay_info: Dictionary containing delay information.
                {
                    "team_member": str,
                    "description": str,
                    "timestamp": str (ISO format)
                }

        Returns:
            dict: Processed delay with additional metadata.
                {
                    "team_member": str,
                    "description": str,
                    "timestamp": str,
                    "delay_id": str,
                    "affected_item_id": str,
                    "estimated_recovery_days": int,
                    "impact_level": str,
                    "root_cause": str,
                    "mitigation_suggestion": str
                }
        """
        try:
            logger.info(f"Processing delay for {delay_info['team_member']}")

            # Generate delay details using OpenAI
            delay_details = await self._generate_delay_details(delay_info["description"])

            # Create result dictionary
            result = {
                "team_member": delay_info["team_member"],
                "description": delay_info["description"],
                "timestamp": delay_info["timestamp"],
                "delay_id": f"DLY-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "affected_item_id": delay_details["affected_item_id"],
                "estimated_recovery_days": delay_details["estimated_recovery_days"],
                "impact_level": delay_details["impact_level"],
                "root_cause": delay_details["root_cause"],
                "mitigation_suggestion": delay_details["mitigation_suggestion"]
            }

            # Generate follow-up questions based on delay details
            follow_up_questions = await self._generate_follow_up_questions(result)
            result["follow_up_questions"] = follow_up_questions

            # Store the processed delay
            await self.store_data(f"delay:{result['delay_id']}", result)

            logger.info(f"Processed delay: {result['delay_id']} for {result['team_member']}")
            return result

        except Exception as e:
            logger.error(f"Error processing delay: {str(e)}")
            # Return a basic result in case of error
            return {
                "team_member": delay_info["team_member"],
                "description": delay_info["description"],
                "timestamp": delay_info["timestamp"],
                "delay_id": f"DLY-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "affected_item_id": "",
                "estimated_recovery_days": 1,
                "impact_level": "Medium",
                "root_cause": "Unknown",
                "mitigation_suggestion": "Please provide more details about this delay.",
                "follow_up_questions": ["What is causing this delay?", "When do you expect to complete this task?"],
                "error": str(e)
            }

    async def _generate_delay_details(self, description):
        """Generate delay details using OpenAI.

        Args:
            description: The delay description.

        Returns:
            dict: Delay details.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": """
            You are an AI assistant analyzing delays reported during daily standups.
            Your job is to extract key information about the delay and suggest next steps.

            Provide a structured analysis in JSON format with the following fields:
            - affected_item_id: string (the item ID being delayed, e.g. "PROJ-123", or empty if not mentioned)
            - estimated_recovery_days: int (estimated days needed to recover from the delay)
            - impact_level: string (Critical, High, Medium, or Low)
            - root_cause: string (concise reason for the delay)
            - mitigation_suggestion: string (what should be done to mitigate the delay)

            Guidelines for impact level:
            - Critical: Jeopardizes sprint goals, affects multiple stories or team members
            - High: Puts individual story at risk, affects core functionality
            - Medium: Causes some delay but story can still be completed within sprint
            - Low: Minor delay, minimal impact on sprint goals

            For estimated_recovery_days, provide your best estimate based on the description.
            If no timeline is mentioned, estimate conservatively based on the described work.
            """
             },
            {"role": "user", "content": f"Analyze this delay description and provide details:\n\n{description}"}
        ]

        # Call OpenAI
        details_text = await self.call_openai(messages, max_tokens=500)

        # Parse JSON response
        try:
            # Find JSON object in response
            import re
            import json
            json_match = re.search(r'(\{.*\})', details_text, re.DOTALL)
            if json_match:
                details_json = json_match.group(1)
                details = json.loads(details_json)
            else:
                # Fallback: try to parse the entire response as JSON
                details = json.loads(details_text)

            # Ensure all expected fields are present
            required_fields = ["affected_item_id", "estimated_recovery_days", "impact_level", "root_cause",
                               "mitigation_suggestion"]
            for field in required_fields:
                if field not in details:
                    if field == "estimated_recovery_days":
                        details[field] = 1
                    else:
                        details[field] = ""

            return details

        except json.JSONDecodeError:
            logger.error(f"Failed to parse delay details as JSON: {details_text}")
            # Return default details
            return {
                "affected_item_id": "",
                "estimated_recovery_days": 1,
                "impact_level": "Medium",
                "root_cause": "Not specified",
                "mitigation_suggestion": "Request more details about the nature of the delay."
            }

    async def _generate_follow_up_questions(self, delay_result):
        """Generate follow-up questions based on delay details.

        Args:
            delay_result: The processed delay result.

        Returns:
            list: List of follow-up questions.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": """
            You are an AI Scrum Master assistant following up on a reported delay.
            Your job is to generate 1-3 follow-up questions to better understand and address the delay.

            The questions should be:
            1. Specific to the reported delay
            2. Aimed at gathering additional information
            3. Focused on finding solutions or mitigations
            4. Concise and direct

            Provide exactly 1-3 questions as a JSON array of strings. Each question should be a complete sentence.
            """
             },
            {"role": "user", "content": f"""
            Team member: {delay_result['team_member']}
            Reported delay: {delay_result['description']}
            Affected item: {delay_result['affected_item_id']}
            Estimated recovery days: {delay_result['estimated_recovery_days']}
            Impact level: {delay_result['impact_level']}
            Root cause: {delay_result['root_cause']}

            Generate follow-up questions to address this delay.
            """}
        ]

        # Call OpenAI
        questions_text = await self.call_openai(messages, max_tokens=300)

        # Parse JSON response
        try:
            # Find JSON array in response
            import re
            import json
            json_match = re.search(r'(\[.*\])', questions_text, re.DOTALL)
            if json_match:
                questions_json = json_match.group(1)
                questions = json.loads(questions_json)
            else:
                # Fallback: try to parse the entire response as JSON
                questions = json.loads(questions_text)

            # Ensure we have at least one question
            if not questions or not isinstance(questions, list):
                questions = ["Could you provide more details about this delay?"]

            return questions[:3]  # Limit to max 3 questions

        except json.JSONDecodeError:
            logger.error(f"Failed to parse follow-up questions as JSON: {questions_text}")
            # Extract questions based on line breaks
            questions = [q.strip() for q in questions_text.split('\n') if q.strip() and '?' in q]
            if not questions:
                questions = ["Could you provide more details about this delay?"]
            return questions[:3]  # Limit to max 3 questions