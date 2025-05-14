# app/agents/overall.py
import logging
import json
from datetime import datetime
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class OverallAgent(BaseAgent):
    """Agent responsible for aggregating and summarizing scrum call data."""

    def __init__(self, call_id, redis_client):
        """Initialize the overall agent.

        Args:
            call_id: Unique identifier for the call.
            redis_client: Redis client for inter-agent communication.
        """
        super().__init__(call_id, redis_client)
        self.mom_agent = None
        self.current_status_agent = None

    def set_mom_agent(self, agent):
        """Set the MOM agent.

        Args:
            agent: MOMAgent instance.
        """
        self.mom_agent = agent

    def set_current_status_agent(self, agent):
        """Set the current status agent.

        Args:
            agent: CurrentStatusAgent instance.
        """
        self.current_status_agent = agent

    async def process_summary(self, call_results):
        """Process and summarize call results.

        Args:
            call_results: Dictionary containing call results.
                {
                    "questions": list,
                    "responses": list,
                    "missing_participants": list,
                    "blockers": list,
                    "delays": list
                }

        Returns:
            dict: Processed summary.
                {
                    "summary": str,
                    "participants": list,
                    "missing_participants": list,
                    "blockers": list,
                    "delays": list,
                    "stories_status": dict,
                    "sprint_health": str,
                    "action_items": list
                }
        """
        try:
            logger.info("Generating overall summary for call")

            # Extract participants (team members who responded)
            participants = [response["team_member"] for response in call_results["responses"]]

            # Deduplicate participants and missing participants
            unique_participants = list(set(participants))
            unique_missing = list(set(call_results["missing_participants"]))

            # Generate natural language summary
            summary = await self._generate_summary(call_results)

            # Extract stories status from responses
            stories_status = await self._extract_stories_status(call_results["responses"])

            # Determine sprint health
            sprint_health = await self._determine_sprint_health(
                stories_status, call_results["blockers"], call_results["delays"]
            )

            # Generate action items
            action_items = await self._generate_action_items(
                call_results["blockers"], call_results["delays"], unique_missing
            )

            # Create result dictionary
            result = {
                "summary": summary,
                "participants": unique_participants,
                "missing_participants": unique_missing,
                "blockers": call_results["blockers"],
                "delays": call_results["delays"],
                "stories_status": stories_status,
                "sprint_health": sprint_health,
                "action_items": action_items,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Store the processed summary
            await self.store_data("overall_summary", result)

            logger.info(f"Generated overall summary: participants={len(unique_participants)}, " +
                        f"missing={len(unique_missing)}, blockers={len(call_results['blockers'])}, " +
                        f"delays={len(call_results['delays'])}, sprint_health={sprint_health}")

            return result

        except Exception as e:
            logger.error(f"Error generating overall summary: {str(e)}")
            # Return a basic result in case of error
            return {
                "summary": f"Error generating summary: {str(e)}",
                "participants": participants if 'participants' in locals() else [],
                "missing_participants": call_results["missing_participants"],
                "blockers": call_results["blockers"],
                "delays": call_results["delays"],
                "stories_status": {},
                "sprint_health": "Unknown",
                "action_items": [],
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    async def _generate_summary(self, call_results):
        """Generate a natural language summary of the call.

        Args:
            call_results: Call results data.

        Returns:
            str: Call summary.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": """
            You are an AI Scrum Master assistant summarizing a daily standup meeting.

            Create a clear, professional summary of the standup meeting based on the data provided.

            Your summary should include:
            1. Overview of attendance and participation
            2. Key updates from team members
            3. Summary of blockers and their impact
            4. Summary of delays and their impact on the sprint
            5. Overall assessment of sprint progress

            Keep the summary concise (300-500 words) and focus on key information.
            Use professional language but maintain a positive, supportive tone.
            """
             },
            {"role": "user", "content": f"""
            Call Data:
            - Total Responses: {len(call_results['responses'])}
            - Missing Participants: {', '.join(call_results['missing_participants']) if call_results['missing_participants'] else 'None'}
            - Blockers: {len(call_results['blockers'])}
            - Delays: {len(call_results['delays'])}

            Participant Responses:
            {json.dumps([{
                'team_member': r['team_member'],
                'response': r['response']
            } for r in call_results['responses']], indent=2)}

            Blockers:
            {json.dumps(call_results['blockers'], indent=2) if call_results['blockers'] else 'None identified'}

            Delays:
            {json.dumps(call_results['delays'], indent=2) if call_results['delays'] else 'None identified'}

            Generate a professional summary of this standup meeting.
            """}
        ]

        # Call OpenAI
        return await self.call_openai(messages, max_tokens=800)

    async def _extract_stories_status(self, responses):
        """Extract status of user stories from responses.

        Args:
            responses: List of participant responses.

        Returns:
            dict: Status of user stories.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": """
            You are an AI assistant extracting information about user stories from standup responses.

            Analyze the responses and extract mentions of user stories and their status.

            For each story mentioned, provide:
            - story_id: The ID of the story (e.g., "PROJ-123") if mentioned, otherwise leave blank
            - title: A brief title or description of the work
            - status: Current status (To Do, In Progress, Done, Blocked)
            - completion_percentage: Estimated percentage complete (0-100)
            - assignee: Person working on it
            - notes: Any relevant notes about progress or issues

            Return your analysis as a JSON object where keys are story IDs (or sequential numbers if IDs not mentioned)
            and values are objects with the fields listed above.
            """
             },
            {"role": "user", "content": f"""
            Participant Responses:
            {json.dumps([{
                'team_member': r['team_member'],
                'response': r['response']
            } for r in responses], indent=2)}

            Extract information about user stories and their status from these responses.
            """}
        ]

        # Call OpenAI
        status_text = await self.call_openai(messages, max_tokens=800)

        # Parse JSON response
        try:
            # Find JSON object in response
            import re
            json_match = re.search(r'(\{.*\})', status_text, re.DOTALL)
            if json_match:
                status_json = json_match.group(1)
                stories_status = json.loads(status_json)
            else:
                # Fallback: try to parse the entire response as JSON
                stories_status = json.loads(status_text)

            return stories_status

        except json.JSONDecodeError:
            logger.error(f"Failed to parse stories status as JSON: {status_text}")
            # Return empty dictionary in case of error
            return {}

    async def _determine_sprint_health(self, stories_status, blockers, delays):
        """Determine the overall health of the sprint.

        Args:
            stories_status: Status of user stories.
            blockers: List of blockers.
            delays: List of delays.

        Returns:
            str: Sprint health (Good, Moderate, At Risk, Critical).
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": """
            You are an AI Scrum Master assistant assessing sprint health.

            Based on the data provided, assess the overall health of the sprint.

            Categorize the sprint health as one of:
            - Good: Sprint is on track with minimal issues
            - Moderate: Some issues, but sprint goals still achievable
            - At Risk: Significant issues threatening sprint goals
            - Critical: Sprint goals unlikely to be achieved

            Consider:
            - Number and severity of blockers
            - Number and impact of delays
            - Status of user stories
            - Overall progress and velocity

            Provide just the health category as a single word.
            """
             },
            {"role": "user", "content": f"""
            Stories Status:
            {json.dumps(stories_status, indent=2)}

            Blockers:
            {json.dumps(blockers, indent=2) if blockers else 'None identified'}

            Delays:
            {json.dumps(delays, indent=2) if delays else 'None identified'}

            Determine the overall health of the sprint.
            """}
        ]

        # Call OpenAI
        health_text = await self.call_openai(messages, max_tokens=50)

        # Extract health category (assuming it's one of the expected values)
        health_text = health_text.strip().lower()
        if "critical" in health_text:
            return "Critical"
        elif "risk" in health_text:
            return "At Risk"
        elif "moderate" in health_text:
            return "Moderate"
        else:
            return "Good"

    async def _generate_action_items(self, blockers, delays, missing_participants):
        """Generate action items based on blockers, delays, and missing participants.

        Args:
            blockers: List of blockers.
            delays: List of delays.
            missing_participants: List of missing participants.

        Returns:
            list: Action items.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": """
            You are an AI Scrum Master assistant generating action items after a standup.

            Based on the blockers, delays, and missing participants, generate a list of specific, 
            actionable items that should be addressed after the meeting.

            For each action item, include:
            - action: Brief description of what needs to be done
            - assignee: Who should take this action (if obvious from context)
            - priority: High, Medium, or Low

            Return your action items as a JSON array of objects with the fields above.
            """
             },
            {"role": "user", "content": f"""
            Blockers:
            {json.dumps(blockers, indent=2) if blockers else 'None identified'}

            Delays:
            {json.dumps(delays, indent=2) if delays else 'None identified'}

            Missing Participants:
            {', '.join(missing_participants) if missing_participants else 'None'}

            Generate actionable follow-up items from this standup meeting.
            """}
        ]

        # Call OpenAI
        actions_text = await self.call_openai(messages, max_tokens=500)

        # Parse JSON response
        try:
            # Find JSON array in response
            import re
            json_match = re.search(r'(\[.*\])', actions_text, re.DOTALL)
            if json_match:
                actions_json = json_match.group(1)
                action_items = json.loads(actions_json)
            else:
                # Fallback: try to parse the entire response as JSON
                action_items = json.loads(actions_text)

            # Ensure result is a list
            if not isinstance(action_items, list):
                action_items = []

            return action_items

        except json.JSONDecodeError:
            logger.error(f"Failed to parse action items as JSON: {actions_text}")
            # Extract action items based on line breaks and hyphens/numbers
            action_items = []
            lines = actions_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line)):
                    action_items.append({
                        "action": line.lstrip('-*0123456789. '),
                        "assignee": "Team",
                        "priority": "Medium"
                    })

            return action_items
