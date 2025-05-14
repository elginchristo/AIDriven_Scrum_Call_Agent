# app/agents/mom.py
import logging
import json
from datetime import datetime
from app.agents.base_agent import BaseAgent
from app.services.email import email_service

logger = logging.getLogger(__name__)


class MOMAgent(BaseAgent):
    """Agent responsible for generating Minutes of Meeting (MOM)."""

    def __init__(self, team_name, project_name, call_id, redis_client, team_members):
        """Initialize the MOM agent.

        Args:
            team_name: Name of the team.
            project_name: Name of the project.
            call_id: Unique identifier for the call.
            redis_client: Redis client for inter-agent communication.
            team_members: List of team members.
        """
        super().__init__(call_id, redis_client)
        self.team_name = team_name
        self.project_name = project_name
        self.team_members = team_members

    async def generate_mom(self, overall_summary):
        """Generate Minutes of Meeting (MOM).

        Args:
            overall_summary: Overall summary of the call.

        Returns:
            dict: MOM data.
                {
                    "subject": str,
                    "body_html": str,
                    "body_text": str,
                    "recipients": list,
                    "timestamp": str (ISO format),
                    "email_sent": bool
                }
        """
        try:
            logger.info("Generating MOM")

            # Generate MOM content
            mom_html = await self._generate_mom_html(overall_summary)
            mom_text = await self._generate_mom_text(overall_summary)

            # Create email subject
            subject = f"[{self.project_name}] Daily Standup Summary - {datetime.utcnow().strftime('%Y-%m-%d')}"

            # Get team members' email addresses
            recipients = [member["email"] for member in self.team_members if "email" in member]

            # Create result dictionary
            result = {
                "subject": subject,
                "body_html": mom_html,
                "body_text": mom_text,
                "recipients": recipients,
                "timestamp": datetime.utcnow().isoformat(),
                "email_sent": False
            }

            # Send email
            if recipients:
                email_sent = await email_service.send_email(
                    to_emails=recipients,
                    subject=subject,
                    body_html=mom_html,
                    body_text=mom_text
                )
                result["email_sent"] = email_sent
                logger.info(f"MOM email sent: {email_sent}")
            else:
                logger.warning("No recipients found for MOM email")

            # Store the MOM
            await self.store_data("mom", result)

            return result

        except Exception as e:
            logger.error(f"Error generating MOM: {str(e)}")
            # Return a basic result in case of error
            return {
                "subject": f"[{self.project_name}] Daily Standup Summary - {datetime.utcnow().strftime('%Y-%m-%d')}",
                "body_html": f"<p>Error generating MOM: {str(e)}</p>",
                "body_text": f"Error generating MOM: {str(e)}",
                "recipients": [],
                "timestamp": datetime.utcnow().isoformat(),
                "email_sent": False,
                "error": str(e)
            }

    async def _generate_mom_html(self, overall_summary):
        """Generate HTML content for the MOM.

        Args:
            overall_summary: Overall summary of the call.

        Returns:
            str: HTML content.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": """
            You are an AI assistant generating a Minutes of Meeting (MOM) email in HTML format for a daily standup.

            Create a professional, well-formatted HTML email that summarizes the standup meeting.
            The email should include:

            1. A brief introduction
            2. Summary of the meeting
            3. List of participants and absentees
            4. Key updates and progress
            5. Blockers and their status
            6. Action items with assignees
            7. Sprint health assessment

            Use proper HTML formatting with headers, lists, tables, and emphasis where appropriate.
            Make the email scannable and professional.
            """
             },
            {"role": "user", "content": f"""
            Team: {self.team_name}
            Project: {self.project_name}
            Date: {datetime.utcnow().strftime('%Y-%m-%d')}

            Overall Summary:
            {overall_summary['summary']}

            Participants: {', '.join(overall_summary['participants'])}
            Missing: {', '.join(overall_summary['missing_participants']) if overall_summary['missing_participants'] else 'None'}

            Blockers:
            {json.dumps(overall_summary['blockers'], indent=2) if overall_summary['blockers'] else 'None identified'}

            Delays:
            {json.dumps(overall_summary['delays'], indent=2) if overall_summary['delays'] else 'None identified'}

            Stories Status:
            {json.dumps(overall_summary['stories_status'], indent=2)}

            Sprint Health: {overall_summary['sprint_health']}

            Action Items:
            {json.dumps(overall_summary['action_items'], indent=2) if overall_summary['action_items'] else 'None identified'}

            Generate HTML email content for the MOM.
            """}
        ]

        # Call OpenAI
        html_content = await self.call_openai(messages, max_tokens=1500)

        # Ensure content is valid HTML by wrapping in proper tags if not already
        if not html_content.strip().startswith('<!DOCTYPE') and not html_content.strip().startswith('<html'):
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Daily Standup Summary - {datetime.utcnow().strftime('%Y-%m-%d')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
                    h2 {{ color: #3498db; margin-top: 20px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                    th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    .good {{ color: green; }}
                    .moderate {{ color: orange; }}
                    .risk {{ color: #ff6600; }}
                    .critical {{ color: red; }}
                    .section {{ margin: 20px 0; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

        return html_content

    async def _generate_mom_text(self, overall_summary):
        """Generate plain text content for the MOM.

        Args:
            overall_summary: Overall summary of the call.

        Returns:
            str: Plain text content.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": """
            You are an AI assistant generating a Minutes of Meeting (MOM) email in plain text format for a daily standup.

            Create a professional plain text email that summarizes the standup meeting.
            The email should include:

            1. A brief introduction
            2. Summary of the meeting
            3. List of participants and absentees
            4. Key updates and progress
            5. Blockers and their status
            6. Action items with assignees
            7. Sprint health assessment

            Use plain text formatting with clear section headers, line breaks, and emphasis where needed.
            Make the email scannable and professional.
            """
             },
            {"role": "user", "content": f"""
            Team: {self.team_name}
            Project: {self.project_name}
            Date: {datetime.utcnow().strftime('%Y-%m-%d')}

            Overall Summary:
            {overall_summary['summary']}

            Participants: {', '.join(overall_summary['participants'])}
            Missing: {', '.join(overall_summary['missing_participants']) if overall_summary['missing_participants'] else 'None'}

            Blockers:
            {json.dumps(overall_summary['blockers'], indent=2) if overall_summary['blockers'] else 'None identified'}

            Delays:
            {json.dumps(overall_summary['delays'], indent=2) if overall_summary['delays'] else 'None identified'}

            Stories Status:
            {json.dumps(overall_summary['stories_status'], indent=2)}

            Sprint Health: {overall_summary['sprint_health']}

            Action Items:
            {json.dumps(overall_summary['action_items'], indent=2) if overall_summary['action_items'] else 'None identified'}

            Generate plain text email content for the MOM.
            """}
        ]

        # Call OpenAI
        return await self.call_openai(messages, max_tokens=1500)
