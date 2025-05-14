# test_run.py - Complete system test
import asyncio
import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000"


class ScrumAgentTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None

    def test_health_check(self):
        """Test if the API is running."""
        print("\n1. Testing API health check...")
        response = self.session.get(f"{BASE_URL}/health")

        if response.status_code == 200:
            print("✓ API is healthy:", response.json())
            return True
        else:
            print("✗ API health check failed:", response.status_code)
            return False

    def test_documentation(self):
        """Test if API documentation is accessible."""
        print("\n2. Testing API documentation...")
        response = self.session.get(f"{BASE_URL}/docs")

        if response.status_code == 200:
            print("✓ API documentation is accessible")
            return True
        else:
            print("✗ API documentation not accessible:", response.status_code)
            return False

    def test_create_project(self):
        """Test creating a project without authentication (simplified for dev)."""
        print("\n3. Testing Projects API...")

        # Create a project
        project_data = {
            "project_id": f"TEST-{int(time.time())}",
            "project_key": "TEST",
            "project_name": "Test Project",
            "project_type": "Software",
            "project_lead": "Test Lead",
            "project_description": "Test project for API testing"
        }

        response = self.session.post(
            f"{BASE_URL}/api/projects/",
            json=project_data
        )

        if response.status_code == 201:
            project = response.json()
            print("✓ Project created:", project["project_id"])
            self.project_id = project["project_id"]
            return True
        else:
            print("✗ Project creation failed:", response.status_code)
            print("  Response:", response.text)
            return False

    def test_create_sprint(self):
        """Test creating a sprint."""
        print("\n4. Testing Sprints API...")

        if not hasattr(self, 'project_id'):
            print("✗ No project ID available, skipping sprint creation")
            return False

        # Create a sprint
        sprint_data = {
            "project_id": self.project_id,
            "sprint_id": f"SPR-{int(time.time())}",
            "sprint_name": "Test Sprint",
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "total_story_points": 0
        }

        response = self.session.post(
            f"{BASE_URL}/api/sprints/",
            json=sprint_data
        )

        if response.status_code == 201:
            sprint = response.json()
            print("✓ Sprint created:", sprint["sprint_id"])
            self.sprint_id = sprint["sprint_id"]
            return True
        else:
            print("✗ Sprint creation failed:", response.status_code)
            print("  Response:", response.text)
            return False

    def test_create_contacts(self):
        """Test creating team contacts."""
        print("\n5. Testing Contacts API...")

        # Create team members
        team_members = [
            {
                "team_name": "Test Team",
                "name": "John Doe",
                "email": f"john{int(time.time())}@example.com"
            },
            {
                "team_name": "Test Team",
                "name": "Jane Smith",
                "email": f"jane{int(time.time())}@example.com"
            }
        ]

        created_count = 0
        self.team_members = []

        for member in team_members:
            response = self.session.post(
                f"{BASE_URL}/api/contacts/",
                json=member
            )

            if response.status_code == 201:
                created_count += 1
                contact = response.json()
                self.team_members.append(contact)
                print(f"✓ Created contact: {member['name']}")
            else:
                print(f"✗ Failed to create contact: {member['name']}")
                print("  Response:", response.text)

        return created_count > 0

    def test_create_user_stories(self):
        """Test creating user stories."""
        print("\n6. Testing User Stories API...")

        if not hasattr(self, 'project_id') or not hasattr(self, 'sprint_id'):
            print("✗ No project/sprint ID available, skipping story creation")
            return False

        # Create user stories
        stories = [
            {
                "project_id": self.project_id,
                "sprint_id": self.sprint_id,
                "story_id": f"STORY-{int(time.time())}-1",
                "story_title": "Implement login functionality",
                "assignee": "John Doe",
                "status": "To Do",
                "priority": "High",
                "story_points": 5,
                "work_item_type": "Story"
            },
            {
                "project_id": self.project_id,
                "sprint_id": self.sprint_id,
                "story_id": f"STORY-{int(time.time())}-2",
                "story_title": "Setup database",
                "assignee": "Jane Smith",
                "status": "In Progress",
                "priority": "High",
                "story_points": 3,
                "work_item_type": "Task"
            },
            {
                "project_id": self.project_id,
                "sprint_id": self.sprint_id,
                "story_id": f"STORY-{int(time.time())}-3",
                "story_title": "Write unit tests",
                "assignee": "John Doe",
                "status": "Done",
                "priority": "Medium",
                "story_points": 2,
                "work_item_type": "Task"
            }
        ]

        created_count = 0
        self.stories = []

        for story in stories:
            response = self.session.post(
                f"{BASE_URL}/api/stories/",
                json=story
            )

            if response.status_code == 201:
                created_count += 1
                created_story = response.json()
                self.stories.append(created_story)
                print(f"✓ Created story: {story['story_title']}")
            else:
                print(f"✗ Failed to create story: {story['story_title']}")
                print("  Response:", response.text)

        return created_count > 0

    def test_create_team_capacity(self):
        """Test creating team capacity entries."""
        print("\n7. Testing Team Capacity API...")

        if not hasattr(self, 'project_id') or not hasattr(self, 'sprint_id'):
            print("✗ No project/sprint ID available, skipping capacity creation")
            return False

        # Create team capacity entries
        capacities = [
            {
                "project_id": self.project_id,
                "sprint_id": self.sprint_id,
                "team_member": "John Doe",
                "available_hours": 80,
                "allocated_hours": 75,
                "days_off": 0
            },
            {
                "project_id": self.project_id,
                "sprint_id": self.sprint_id,
                "team_member": "Jane Smith",
                "available_hours": 72,
                "allocated_hours": 70,
                "days_off": 1
            }
        ]

        created_count = 0

        for capacity in capacities:
            response = self.session.post(
                f"{BASE_URL}/api/team-capacity/",
                json=capacity
            )

            if response.status_code == 201:
                created_count += 1
                print(f"✓ Created capacity for: {capacity['team_member']}")
            else:
                print(f"✗ Failed to create capacity for: {capacity['team_member']}")
                print("  Response:", response.text)

        return created_count > 0

    def test_create_blocker(self):
        """Test creating a blocker."""
        print("\n8. Testing Blocker Creation...")

        if not hasattr(self, 'project_id') or not hasattr(self, 'stories'):
            print("✗ No project/stories available, skipping blocker creation")
            return False

        # Create a blocker for one of the stories
        blocker_data = {
            "project_id": self.project_id,
            "blocked_item_id": self.stories[0]["story_id"],
            "blocked_item_title": self.stories[0]["story_title"],
            "assignee": "John Doe",
            "blocker_description": "Waiting for API credentials",
            "blocking_reason": "External dependency"
        }

        response = self.session.post(
            f"{BASE_URL}/api/blockers/",
            json=blocker_data
        )

        if response.status_code == 201:
            blocker = response.json()
            print("✓ Created blocker:", blocker["blocked_item_id"])
            return True
        else:
            print("✗ Blocker creation failed:", response.status_code)
            print("  Response:", response.text)
            # Check if endpoint exists
            if response.status_code == 404:
                print("  Note: Blocker endpoint might not be implemented yet")
            return False

    def test_create_scheduled_call(self):
        """Test creating a scheduled call."""
        print("\n9. Testing Scheduled Calls API...")

        # Create a scheduled call
        scheduled_call = {
            "team_name": "Test Team",
            "project_name": "Test Project",
            "scheduled_time": (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
            "platform": "zoom",
            "platform_credentials": {
                "username": "test@example.com",
                "password": "test_password"
            },
            "email_credentials": {
                "username": "email@example.com",
                "password": "email_password"
            },
            "aggressiveness_level": 5,
            "is_recurring": False,
            "recurring_pattern": "0 10 * * 1-5"
        }

        response = self.session.post(
            f"{BASE_URL}/api/schedules/",
            json=scheduled_call
        )

        if response.status_code == 201:
            call = response.json()
            print("✓ Scheduled call created:", call.get("id", "No ID returned"))
            self.scheduled_call_id = call.get("id")
            return True
        else:
            print("✗ Scheduled call creation failed:", response.status_code)
            print("  Response:", response.text)
            return False

    def test_reports_api(self):
        """Test reports API endpoints."""
        print("\n10. Testing Reports API...")

        # Get sprint calls (might be empty)
        response = self.session.get(f"{BASE_URL}/api/reports/sprint-calls/")

        if response.status_code == 200:
            calls = response.json()
            print(f"✓ Retrieved {len(calls)} sprint calls")
            return True
        else:
            print("✗ Failed to retrieve sprint calls:", response.status_code)
            return False

    def test_velocity_api(self):
        """Test velocity history API."""
        print("\n11. Testing Velocity API...")

        if not hasattr(self, 'project_id') or not hasattr(self, 'sprint_id'):
            print("✗ No project/sprint ID available, skipping velocity test")
            return False

        # Create velocity entry
        velocity_data = {
            "project_id": self.project_id,
            "sprint_id": self.sprint_id,
            "story_points_committed": 30,
            "story_points_completed": 25,
            "velocity": 0.83,
            "deviation": -16.7
        }

        response = self.session.post(
            f"{BASE_URL}/api/velocity/",
            json=velocity_data
        )

        if response.status_code == 201:
            print("✓ Created velocity entry")
            return True
        else:
            print("✗ Velocity creation failed:", response.status_code)
            print("  Response:", response.text)
            return False

    def test_database_connectivity(self):
        """Test database connectivity through the API."""
        print("\n12. Testing Database Connectivity...")

        # Try to get projects (should work if DB is connected)
        response = self.session.get(f"{BASE_URL}/api/projects/")

        if response.status_code == 200:
            projects = response.json()
            print(f"✓ Database is connected - found {len(projects)} projects")
            return True
        else:
            print("✗ Database connectivity issue:", response.status_code)
            return False

    def run_all_tests(self):
        """Run all tests in sequence."""
        print("=== Starting Scrum Agent API Tests ===")
        print(f"Testing against: {BASE_URL}")
        print("=" * 40)

        tests = [
            ("Health Check", self.test_health_check),
            ("API Documentation", self.test_documentation),
            ("Database Connectivity", self.test_database_connectivity),
            ("Create Project", self.test_create_project),
            ("Create Sprint", self.test_create_sprint),
            ("Create Contacts", self.test_create_contacts),
            ("Create User Stories", self.test_create_user_stories),
            ("Create Team Capacity", self.test_create_team_capacity),
            ("Create Blocker", self.test_create_blocker),
            ("Create Scheduled Call", self.test_create_scheduled_call),
            ("Reports API", self.test_reports_api),
            ("Velocity API", self.test_velocity_api)
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            try:
                print(f"\n{'=' * 40}")
                print(f"Running: {test_name}")
                print('=' * 40)

                if test_func():
                    passed += 1
                    print(f"\n✅ {test_name} - PASSED")
                else:
                    failed += 1
                    print(f"\n❌ {test_name} - FAILED")
            except Exception as e:
                print(f"\n❌ {test_name} - FAILED with exception: {e}")
                import traceback
                traceback.print_exc()
                failed += 1

        print("\n" + "=" * 40)
        print("=== Test Summary ===")
        print(f"✓ Passed: {passed}")
        print(f"✗ Failed: {failed}")
        print(f"Total: {passed + failed}")
        print("=" * 40)

        if failed == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {failed} tests failed")

        # Print created resources for reference
        if hasattr(self, 'project_id'):
            print(f"\n📁 Created Project ID: {self.project_id}")
        if hasattr(self, 'sprint_id'):
            print(f"🏃 Created Sprint ID: {self.sprint_id}")
        if hasattr(self, 'scheduled_call_id'):
            print(f"📅 Created Scheduled Call ID: {self.scheduled_call_id}")


if __name__ == "__main__":
    # Make sure the API is running
    print("🚀 Scrum Agent Test Runner")
    print("=" * 40)
    print("Make sure the API is running at http://localhost:8000")
    print("Run: uvicorn app.main:app --reload")
    print("=" * 40)

    input("Press Enter to start tests...")

    tester = ScrumAgentTester()
    tester.run_all_tests()