# app/services/jira.py
import logging
import aiohttp
import base64
import json
from app.config import settings

logger = logging.getLogger(__name__)


class JiraService:
    """Service for interacting with JIRA."""

    def __init__(self):
        """Initialize the JIRA service."""
        self.base_url = settings.JIRA.BASE_URL
        self.username = settings.JIRA.USERNAME
        self.api_token = settings.JIRA.API_TOKEN

        # Create basic auth header
        auth_str = f"{self.username}:{self.api_token}"
        base64_auth = base64.b64encode(auth_str.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {base64_auth}",
            "Content-Type": "application/json"
        }

    async def get_issue(self, issue_key):
        """Get a JIRA issue.

        Args:
            issue_key: JIRA issue key.

        Returns:
            dict: Issue data.
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        issue_data = await response.json()
                        logger.info(f"Retrieved issue: {issue_key}")
                        return issue_data
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get issue {issue_key}: {response.status} - {error_text}")
                        return None

        except Exception as e:
            logger.error(f"JIRA API error getting issue {issue_key}: {str(e)}")
            return None

    async def update_issue_status(self, issue_key, transition_id):
        """Update a JIRA issue status.

        Args:
            issue_key: JIRA issue key.
            transition_id: Transition ID to apply.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"
                payload = {
                    "transition": {
                        "id": transition_id
                    }
                }

                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 204:
                        logger.info(f"Updated issue status: {issue_key} with transition: {transition_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to update issue {issue_key}: {response.status} - {error_text}")
                        return False

        except Exception as e:
            logger.error(f"JIRA API error updating issue {issue_key}: {str(e)}")
            return False

    async def add_comment(self, issue_key, comment_text):
        """Add a comment to a JIRA issue.

        Args:
            issue_key: JIRA issue key.
            comment_text: Comment text.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
                payload = {
                    "body": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": comment_text
                                    }
                                ]
                            }
                        ]
                    }
                }

                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status in (200, 201):
                        logger.info(f"Added comment to issue: {issue_key}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to add comment to issue {issue_key}: {response.status} - {error_text}")
                        return False

        except Exception as e:
            logger.error(f"JIRA API error adding comment to issue {issue_key}: {str(e)}")
            return False


jira_service = JiraService()
