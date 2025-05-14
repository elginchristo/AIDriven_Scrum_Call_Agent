# app/agents/blocker.py
import logging
import asyncio
from datetime import datetime
from app.agents.base_agent import BaseAgent
from app.services.jira import jira_service
from app.services.email import email_service

logger = logging.getLogger(__name__)


class BlockerAgent(BaseAgent):
    """Agent responsible for handling blockers identified during scrum calls."""

    def __init__(self, call_id, redis_client, project_id):
        """Initialize the blocker agent.

        Args:
            call_id: Unique identifier for the call.
            redis_client: Redis client for inter-agent communication.
            project_id: ID of the project.
        """
        super().__init__(call_id, redis_client)
        self.project_id = project_id

    async def process(self, blocker_info):
        """Process a blocker.

        Args:
            blocker_info: Dictionary containing blocker information.
                {
                    "team_member": str,
                    "description": str,
                    "timestamp": str (ISO format)
                }

        Returns:
            dict: Processed blocker with additional metadata.
                {
                    "team_member": str,
                    "description": str,
                    "timestamp": str,
                    "blocker_id": str,
                    "jira_updated": bool,
                    "email_sent": bool,
                    "action_required": bool,
                    "suggested_action": str
                }
        """
        try:
            logger.info(f"Processing blocker for {blocker_info['team_member']}")

            # Generate blocker details using OpenAI
            blocker_details = await self._generate_blocker_details(blocker_info["description"])

            # Create result dictionary
            result = {
                "team_member": blocker_info["team_member"],
                "description": blocker_info["description"],
                "timestamp": blocker_info["timestamp"],
                "blocker_id": f"BLK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "jira_updated": False,
                "email_sent": False,
                "action_required": blocker_details["action_required"],
                "suggested_action": blocker_details["suggested_action"],
                "affected_item_id": blocker_details["affected_item_id"],
                "severity": blocker_details["severity"],
                "blocking_reason": blocker_details["blocking_reason"]
            }

            # Update JIRA if an affected item was identified
            if result["affected_item_id"]:
                # Check if the item ID looks like a JIRA issue key
                import re
                if re.match(r'^[A-Z]+-\d+$', result["affected_item_id"]):
                    # Update JIRA status to "Blocked"
                    jira_updated = await jira_service.update_issue_status(
                        result["affected_item_id"],
                        "31"  # Assuming 31 is the transition ID for "Set as Blocked"
                    )

                    if jira_updated:
                        # Add a comment about the blocker
                        comment = (
                            f"Blocker reported during scrum call by {result['team_member']}:\n\n"
                            f"{result['description']}\n\n"
                            f"Blocking reason: {result['blocking_reason']}\n"
                            f"Severity: {result['severity']}\n"
                            f"Suggested action: {result['suggested_action']}"
                        )
                        await jira_service.add_comment(result["affected_item_id"], comment)

                        result["jira_updated"] = True
                        logger.info(f"Updated JIRA issue {result['affected_item_id']} for blocker")

            # Send email notification for high severity blockers
            if result["severity"] in ["High", "Critical"]:
                # In a real implementation, we would fetch stakeholder emails from the database
                stakeholder_emails = ["stakeholder@example.com", "manager@example.com"]

                email_html = f"""
                <h2>High Severity Blocker Reported</h2>
                <p><strong>Reported by:</strong> {result['team_member']}</p>
                <p><strong>Affected Item:</strong> {result['affected_item_id']}</p>
                <p><strong>Severity:</strong> {result['severity']}</p>
                <p><strong>Description:</strong> {result['description']}</p>
                <p><strong>Blocking Reason:</strong> {result['blocking_reason']}</p>
                <p><strong>Suggested Action:</strong> {result['suggested_action']}</p>
                <p><strong>Reported:</strong> {datetime.fromisoformat(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</p>
                """

                # Send email
                email_sent = await email_service.send_email(
                    to_emails=stakeholder_emails,
                    subject=f"[BLOCKER] {result['affected_item_id']} - {result['blocking_reason']}",
                    body_html=email_html
                )

                result["email_sent"] = email_sent
                logger.info(f"Email notification sent for blocker: {result['email_sent']}")

            # Store the processed blocker
            await self.store_data(f"blocker:{result['blocker_id']}", result)

            return result

        except Exception as e:
            logger.error(f"Error processing blocker: {str(e)}")
            # Return a basic result in case of error
            return {
                "team_member": blocker_info["team_member"],
                "description": blocker_info["description"],
                "timestamp": blocker_info["timestamp"],
                "blocker_id": f"BLK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "jira_updated": False,
                "email_sent": False,
                "action_required": True,
                "suggested_action": "Please investigate this blocker manually.",
                "error": str(e)
            }

    async def _generate_blocker_details(self, description):
        """Generate blocker details using OpenAI.

        Args:
            description: The blocker description.

        Returns:
            dict: Blocker details.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": """
            You are an AI assistant analyzing blockers reported during daily standups.
            Your job is to extract key information about the blocker and suggest next steps.

            Provide a structured analysis in JSON format with the following fields:
            - affected_item_id: string (the item ID being blocked, e.g. "PROJ-123", or empty if not mentioned)
            - severity: string (Critical, High, Medium, or Low)
            - blocking_reason: string (concise reason for the blocker)
            - action_required: boolean (true if immediate action is needed)
            - suggested_action: string (what should be done to resolve the blocker)

            Guidelines for severity:
            - Critical: Completely blocks progress, affects multiple team members, jeopardizes sprint goals
            - High: Significantly blocks progress, affects core functionality, puts individual stories at risk
            - Medium: Partially blocks progress, workarounds available, may cause delays
            - Low: Minor blocker, minimal impact, easy workarounds available
            """
            },
            {"role": "user", "content": f"Analyze this blocker description and provide details:\n\n{description}"}
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
            required_fields = ["affected_item_id", "severity", "blocking_reason", "action_required", "suggested_action"]
            for field in required_fields:
                if field not in details:
                    if field == "action_required":
                        details[field] = True
                    else:
                        details[field] = ""

            return details

        except json.JSONDecodeError:
            logger.error(f"Failed to parse blocker details as JSON: {details_text}")
            # Return default details
            return {
                "affected_item_id": "",
                "severity": "Medium",
                "blocking_reason": description,
                "action_required": True,
                "suggested_action": "Investigate the blocker and assign to the appropriate team."
            }