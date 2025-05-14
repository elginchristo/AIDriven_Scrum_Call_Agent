# test_scrum_call.py - Test the complete scrum call workflow
import asyncio
import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000"


class ScrumCallTester:
    def __init__(self):
        self.api_url = BASE_URL
        self.test_data = {}

    async def setup_test_data(self):
        """Create test data needed for a scrum call."""
        print("📋 Setting up test data...")

        # 1. Create a project
        project_data = {
            "project_id": f"CALL-{int(time.time())}",
            "project_key": "CALL",
            "project_name": "Scrum Call Test Project",
            "project_type": "Software",
            "project_lead": "Test Lead"
        }

        response = requests.post(f"{self.api_url}/api/projects/", json=project_data)
        if response.status_code == 201:
            self.test_data['project'] = response.json()
            print(f"✓ Created project: {self.test_data['project']['project_name']}")
        else:
            print(f"✗ Failed to create project: {response.text}")
            return False

        # 2. Create a sprint
        sprint_data = {
            "project_id": self.test_data['project']['project_id'],
            "sprint_id": f"SPR-{int(time.time())}",
            "sprint_name": "Sprint 1",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=14)).isoformat()
        }

        response = requests.post(f"{self.api_url}/api/sprints/", json=sprint_data)
        if response.status_code == 201:
            self.test_data['sprint'] = response.json()
            print(f"✓ Created sprint: {self.test_data['sprint']['sprint_name']}")

        # 3. Add team members
        team_members = [
            {"team_name": self.test_data['project']['project_name'], "name": "John Developer",
             "email": f"john{int(time.time())}@test.com"},
            {"team_name": self.test_data['project']['project_name'], "name": "Jane Developer",
             "email": f"jane{int(time.time())}@test.com"},
            {"team_name": self.test_data['project']['project_name'], "name": "Bob Developer",
             "email": f"bob{int(time.time())}@test.com"}
        ]

        self.test_data['team_members'] = []
        for member in team_members:
            response = requests.post(f"{self.api_url}/api/contacts/", json=member)
            if response.status_code == 201:
                self.test_data['team_members'].append(response.json())
                print(f"✓ Added team member: {member['name']}")

        # 4. Create user stories
        stories = [
            {
                "project_id": self.test_data['project']['project_id'],
                "sprint_id": self.test_data['sprint']['sprint_id'],
                "story_id": f"US-{int(time.time())}-1",
                "story_title": "Complete authentication module",
                "assignee": self.test_data['team_members'][0]['name'],
                "status": "In Progress",
                "priority": "High",
                "story_points": 8
            },
            {
                "project_id": self.test_data['project']['project_id'],
                "sprint_id": self.test_data['sprint']['sprint_id'],
                "story_id": f"US-{int(time.time())}-2",
                "story_title": "Setup database schema",
                "assignee": self.test_data['team_members'][1]['name'],
                "status": "Done",
                "priority": "High",
                "story_points": 5
            },
            {
                "project_id": self.test_data['project']['project_id'],
                "sprint_id": self.test_data['sprint']['sprint_id'],
                "story_id": f"US-{int(time.time())}-3",
                "story_title": "Implement API endpoints",
                "assignee": self.test_data['team_members'][2]['name'],
                "status": "To Do",
                "priority": "Medium",
                "story_points": 13
            }
        ]

        self.test_data['stories'] = []
        for story in stories:
            response = requests.post(f"{self.api_url}/api/stories/", json=story)
            if response.status_code == 201:
                self.test_data['stories'].append(response.json())
                print(f"✓ Created story: {story['story_title']}")

        return True

    async def create_scheduled_call(self):
        """Create a scheduled call for testing."""
        print("\n📅 Creating scheduled call...")

        # Schedule a call for 1 minute from now
        scheduled_time = datetime.now() + timedelta(minutes=1)

        schedule_data = {
            "team_name": self.test_data['project']['project_name'],
            "project_name": self.test_data['project']['project_name'],
            "scheduled_time": scheduled_time.isoformat(),
            "platform": "zoom",
            "platform_credentials": {
                "username": "test@zoom.com",
                "password": "test_password"
            },
            "email_credentials": {
                "username": "test@email.com",
                "password": "email_password"
            },
            "aggressiveness_level": 5,
            "is_recurring": False,
            "recurring_pattern": "0 10 * * 1-5"
        }

        response = requests.post(f"{self.api_url}/api/schedules/", json=schedule_data)
        if response.status_code == 201:
            self.test_data['scheduled_call'] = response.json()
            print(f"✓ Scheduled call created for: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Call ID: {self.test_data['scheduled_call']['id']}")
            return True
        else:
            print(f"✗ Failed to create scheduled call: {response.text}")
            return False

    async def simulate_scrum_call(self):
        """Simulate the scrum call workflow."""
        print("\n🎙️ Simulating Scrum Call...")
        print("=" * 50)

        # In a real implementation, this would be triggered by the scheduler
        # For testing, we'll simulate the orchestrator process

        # 1. Simulate call start
        print("\n1. Starting scrum call...")
        print(f"   Team: {self.test_data['project']['project_name']}")
        print(f"   Participants: {len(self.test_data['team_members'])} members")

        # 2. Simulate DrivingCall Agent
        print("\n2. DrivingCall Agent conducting meeting...")
        for i, member in enumerate(self.test_data['team_members']):
            print(f"\n   Asking {member['name']}:")
            print(f"   - What did you complete yesterday?")
            await asyncio.sleep(1)  # Simulate response time

            # Simulate response based on assigned stories
            assigned_story = next((s for s in self.test_data['stories'] if s['assignee'] == member['name']), None)
            if assigned_story:
                if assigned_story['status'] == 'Done':
                    print(f"   Response: I completed {assigned_story['story_title']}")
                elif assigned_story['status'] == 'In Progress':
                    print(f"   Response: I'm working on {assigned_story['story_title']}, about 60% done")
                else:
                    print(f"   Response: I'm starting {assigned_story['story_title']} today")

            print(f"   - What are you working on today?")
            await asyncio.sleep(1)
            print(f"   Response: Continuing with my assigned tasks")

            print(f"   - Any blockers?")
            await asyncio.sleep(1)
            if i == 1:  # Simulate one person having a blocker
                print(f"   Response: Yes, I'm blocked on API credentials")
            else:
                print(f"   Response: No blockers")

        # 3. Simulate Overall Agent aggregation
        print("\n3. Overall Agent aggregating results...")
        await asyncio.sleep(2)

        summary = {
            "participants": [m['name'] for m in self.test_data['team_members']],
            "missing_participants": [],
            "blockers": [{"team_member": self.test_data['team_members'][1]['name'],
                          "description": "Blocked on API credentials"}],
            "stories_progress": {
                "Done": 1,
                "In Progress": 1,
                "To Do": 1
            },
            "sprint_health": "Good"
        }

        print(f"   Summary generated:")
        print(f"   - {len(summary['participants'])} participants")
        print(f"   - {len(summary['blockers'])} blockers identified")
        print(f"   - Sprint health: {summary['sprint_health']}")

        # 4. Simulate MOM Agent
        print("\n4. MOM Agent generating minutes...")
        await asyncio.sleep(1)
        print("   Meeting minutes created")
        print("   Email sent to team members")

        # 5. Simulate CurrentStatus Agent
        print("\n5. CurrentStatus Agent updating status...")
        await asyncio.sleep(1)
        sprint_progress = {
            "total_points": sum(s['story_points'] for s in self.test_data['stories']),
            "completed_points": sum(s['story_points'] for s in self.test_data['stories'] if s['status'] == 'Done'),
            "progress_percentage": 0
        }
        sprint_progress['progress_percentage'] = (
                    sprint_progress['completed_points'] / sprint_progress['total_points'] * 100)

        print(f"   Sprint progress: {sprint_progress['progress_percentage']:.1f}%")
        print(f"   Completed: {sprint_progress['completed_points']}/{sprint_progress['total_points']} points")

        return summary

    async def check_call_results(self):
        """Check the results of the scrum call."""
        print("\n📊 Checking Call Results...")

        # Get sprint progress
        response = requests.get(
            f"{self.api_url}/api/sprints/{self.test_data['sprint']['sprint_id']}",
            params={"project_id": self.test_data['project']['project_id']}
        )

        if response.status_code == 200:
            sprint_data = response.json()
            print(f"\nSprint Status:")
            print(f"  Progress: {sprint_data.get('percent_completion', 0):.1f}%")
            print(f"  Completed Points: {sprint_data['completed_story_points']}")
            print(f"  Total Points: {sprint_data['total_story_points']}")

        # Check for sprint call records (would be created by the actual agent)
        # For now, we'll just summarize what would have been created

        print("\n✅ Scrum Call Simulation Complete!")
        print("\nIn a real implementation, the following would be created:")
        print("  - Sprint call record with transcript")
        print("  - Meeting minutes (MOM) sent via email")
        print("  - Updated story statuses")
        print("  - Blocker records")
        print("  - Team capacity updates")


async def main():
    """Run the scrum call test."""
    print("🚀 SCRUM CALL TEST RUNNER")
    print("=" * 50)

    tester = ScrumCallTester()

    # Setup test data
    if await tester.setup_test_data():
        # Create scheduled call
        if await tester.create_scheduled_call():
            print("\n⏰ Waiting for scheduled time...")
            print("   (In production, the scheduler would trigger the call)")

            # Wait a moment
            await asyncio.sleep(3)

            # Simulate the scrum call
            summary = await tester.simulate_scrum_call()

            # Check results
            await tester.check_call_results()

    print("\n🎯 Test completed!")


if __name__ == "__main__":
    asyncio.run(main())