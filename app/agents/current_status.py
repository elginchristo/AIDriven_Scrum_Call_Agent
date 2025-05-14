# app/agents/current_status.py
import logging
import json
from datetime import datetime
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CurrentStatusAgent(BaseAgent):
    """Agent responsible for generating current sprint status."""

    def __init__(self, call_id, redis_client, current_sprint, user_stories):
        """Initialize the current status agent.

        Args:
            call_id: Unique identifier for the call.
            redis_client: Redis client for inter-agent communication.
            current_sprint: Current sprint information.
            user_stories: List of user stories for the current sprint.
        """
        super().__init__(call_id, redis_client)
        self.current_sprint = current_sprint
        self.user_stories = user_stories

    async def generate_status_report(self, overall_summary):
        """Generate current status report.

        Args:
            overall_summary: Overall summary of the call.

        Returns:
            dict: Status report.
                {
                    "percentage": int,
                    "status": dict,
                    "health_indicators": dict,
                    "recommendations": list,
                    "timestamp": str (ISO format)
                }
        """
        try:
            logger.info("Generating current status report")

            # Calculate overall sprint completion percentage
            total_points = sum(story["story_points"] for story in self.user_stories if "story_points" in story)
            completed_points = sum(
                story["story_points"] for story in self.user_stories
                if "story_points" in story and story["status"] == "Done"
            )
            percentage = int((completed_points / total_points * 100) if total_points > 0 else 0)

            # Generate status for each story
            story_status = {}
            for story_id, status_info in overall_summary["stories_status"].items():
                # Determine status category (On Track, Delayed, Backlog)
                if status_info.get("status") == "Done":
                    category = "Completed"
                elif status_info.get("status") == "Blocked":
                    category = "Blocked"
                elif status_info.get("completion_percentage", 0) >= 50:
                    category = "On Track"
                elif status_info.get("completion_percentage", 0) > 0:
                    category = "Delayed"
                else:
                    category = "Backlog"

                story_status[story_id] = {
                    "title": status_info.get("title", ""),
                    "category": category,
                    "completion": status_info.get("completion_percentage", 0),
                    "assignee": status_info.get("assignee", "")
                }

            # Generate health indicators
            health_indicators = await self._generate_health_indicators(overall_summary)

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                overall_summary, percentage, story_status, health_indicators
            )

            # Create result dictionary
            result = {
                "percentage": percentage,
                "status": story_status,
                "health_indicators": health_indicators,
                "recommendations": recommendations,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Store the status report
            await self.store_data("status_report", result)

            logger.info(f"Generated status report: completion={percentage}%, " +
                        f"stories={len(story_status)}, indicators={len(health_indicators)}")

            return result

        except Exception as e:
            logger.error(f"Error generating status report: {str(e)}")
            # Return a basic result in case of error
            return {
                "percentage": 0,
                "status": {},
                "health_indicators": {
                    "overall": "Unknown",
                    "error": str(e)
                },
                "recommendations": [
                    "Review sprint status manually due to error in status generation."
                ],
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    async def _generate_health_indicators(self, overall_summary):
        """Generate health indicators for the sprint.

        Args:
            overall_summary: Overall summary of the call.

        Returns:
            dict: Health indicators.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": """
            You are an AI assistant analyzing sprint health based on standup data.

            Generate a set of health indicators for the sprint as a JSON object with these fields:
            - overall: Overall health (Good, Moderate, At Risk, Critical)
            - velocity: Velocity assessment (Above Target, On Target, Below Target)
            - quality: Quality assessment (Good, Needs Attention, Poor)
            - team_collaboration: Team collaboration assessment (Strong, Adequate, Weak)
            - risk_factors: Array of specific risk factors (if any)
            - positive_factors: Array of specific positive factors (if any)

            Base your assessment on the provided data about blockers, delays, and progress.
            """
             },
            {"role": "user", "content": f"""
            Sprint Health from Summary: {overall_summary['sprint_health']}

            Blockers:
            {json.dumps(overall_summary['blockers'], indent=2) if overall_summary['blockers'] else 'None identified'}

            Delays:
            {json.dumps(overall_summary['delays'], indent=2) if overall_summary['delays'] else 'None identified'}

            Stories Status:
            {json.dumps(overall_summary['stories_status'], indent=2)}

            Missing Participants:
            {', '.join(overall_summary['missing_participants']) if overall_summary['missing_participants'] else 'None'}

            Generate health indicators for this sprint.
            """}
        ]

        # Call OpenAI
        indicators_text = await self.call_openai(messages, max_tokens=800)

        # Parse JSON response
        try:
            # Find JSON object in response
            import re
            json_match = re.search(r'(\{.*\})', indicators_text, re.DOTALL)
            if json_match:
                indicators_json = json_match.group(1)
                indicators = json.loads(indicators_json)
            else:
                # Fallback: try to parse the entire response as JSON
                indicators = json.loads(indicators_text)

            return indicators

        except json.JSONDecodeError:
            logger.error(f"Failed to parse health indicators as JSON: {indicators_text}")
            # Return basic indicators in case of error
            return {
                "overall": overall_summary['sprint_health'],
                "velocity": "Unknown",
                "quality": "Unknown",
                "team_collaboration": "Unknown",
                "risk_factors": [],
                "positive_factors": []
            }

    async def _generate_recommendations(self, overall_summary, percentage, story_status, health_indicators):
        """Generate recommendations based on the sprint status.

        Args:
            overall_summary: Overall summary of the call.
            percentage: Overall completion percentage.
            story_status: Status of each story.
            health_indicators: Health indicators.

        Returns:
            list: Recommendations.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": """
            You are an AI Scrum Master assistant generating recommendations for sprint improvement.

            Based on the sprint status data provided, generate 3-5 specific, actionable recommendations to improve the sprint success.

            Each recommendation should:
            - Address a specific issue or opportunity
            - Be concrete and actionable (not vague)
            - Be realistic to implement within the sprint
            - Include who should take action (if appropriate)

            Return your recommendations as a JSON array of strings.
            """
             },
            {"role": "user", "content": f"""
            Sprint Completion: {percentage}%

            Sprint Health: 
            {json.dumps(health_indicators, indent=2)}

            Story Status:
            {json.dumps(story_status, indent=2)}

            Blockers:
            {json.dumps(overall_summary['blockers'], indent=2) if overall_summary['blockers'] else 'None identified'}

            Delays:
            {json.dumps(overall_summary['delays'], indent=2) if overall_summary['delays'] else 'None identified'}

            Action Items Already Identified:
            {json.dumps(overall_summary['action_items'], indent=2) if overall_summary['action_items'] else 'None identified'}

            Generate recommendations for improving this sprint.
            """}
        ]

        # Call OpenAI
        recommendations_text = await self.call_openai(messages, max_tokens=800)

        # Parse JSON response
        try:
            # Find JSON array in response
            import re
            json_match = re.search(r'(\[.*\])', recommendations_text, re.DOTALL)
            if json_match:
                recommendations_json = json_match.group(1)
                recommendations = json.loads(recommendations_json)
            else:
                # Fallback: try to parse the entire response as JSON
                recommendations = json.loads(recommendations_text)

            # Ensure result is a list
            if not isinstance(recommendations, list):
                recommendations = []

            return recommendations

        except json.JSONDecodeError:
            logger.error(f"Failed to parse recommendations as JSON: {recommendations_text}")
            # Extract recommendations based on line breaks and hyphens/numbers
            recommendations = []
            lines = recommendations_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line)):
                    recommendations.append(line.lstrip('-*0123456789. '))

            return recommendations
