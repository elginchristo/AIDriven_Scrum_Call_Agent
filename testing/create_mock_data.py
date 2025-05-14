# create_mock_data_no_auth.py - Version without authentication requirement
import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000"


class MockDataCreator:
    def __init__(self):
        self.api_url = BASE_URL
        self.created_data = {
            "projects": [],
            "sprints": [],
            "stories": [],
            "team_members": [],
            "scheduled_calls": [],
            "blockers": [],
            "capacities": []
        }

        # Check if we need authentication
        self.check_auth_requirement()

    def check_auth_requirement(self):
        """Check if the API requires authentication."""
        # Try to access a protected endpoint
        response = requests.get(f"{self.api_url}/api/projects/")

        if response.status_code == 401:
            print("⚠️  API requires authentication")
            print("   Update app/dependencies.py to use development mode")
            print("   Or disable authentication for testing")
            return False

        return True

    def make_request(self, method, url, json_data=None):
        """Make an API request with error handling."""
        try:
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=json_data)
            elif method == "PUT":
                response = requests.put(url, json=json_data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            return response
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None

    def create_projects(self):
        """Create mock projects."""
        print("\n1. Creating Projects...")

        projects = [
            {
                "project_id": "ECOM-001",
                "project_key": "ECOM",
                "project_name": "E-Commerce Platform",
                "project_type": "Software",
                "project_lead": "Sarah Johnson",
                "project_description": "Online shopping platform with payment integration",
                "project_url": "https://github.com/company/ecommerce",
                "project_category": "Web Application"
            },
            {
                "project_id": "MOB-001",
                "project_key": "MOB",
                "project_name": "Mobile Banking App",
                "project_type": "Mobile",
                "project_lead": "Mike Chen",
                "project_description": "iOS and Android banking application",
                "project_url": "https://github.com/company/mobile-banking",
                "project_category": "Mobile Application"
            },
            {
                "project_id": "AI-001",
                "project_key": "AI",
                "project_name": "AI Analytics Dashboard",
                "project_type": "Software",
                "project_lead": "Emma Davis",
                "project_description": "Machine learning powered analytics platform",
                "project_url": "https://github.com/company/ai-analytics",
                "project_category": "Data Science"
            }
        ]

        for project in projects:
            response = self.make_request("POST", f"{self.api_url}/api/projects/", project)

            if response and response.status_code == 201:
                created_project = response.json()
                self.created_data["projects"].append(created_project)
                print(f"✓ Created project: {project['project_name']}")
            elif response and response.status_code == 401:
                print(f"✗ Authentication required. Please update dependencies.py")
                print("  Set ENV=development in .env file")
                return
            else:
                print(f"✗ Failed to create project: {project['project_name']}")
                if response:
                    print(f"  Response: {response.text}")

    # ... rest of the methods remain the same as the original create_mock_data.py ...

    def create_sprints(self):
        """Create mock sprints for each project."""
        print("\n2. Creating Sprints...")

        for project in self.created_data["projects"]:
            # Current sprint
            current_sprint = {
                "project_id": project["project_id"],
                "sprint_id": f"{project['project_key']}-SPR-001",
                "sprint_name": "Sprint 1 - Foundation",
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=14)).isoformat(),
                "total_story_points": 0
            }

            response = self.make_request("POST", f"{self.api_url}/api/sprints/", current_sprint)

            if response and response.status_code == 201:
                sprint = response.json()
                self.created_data["sprints"].append(sprint)
                print(f"✓ Created sprint: {sprint['sprint_name']} for {project['project_name']}")
            else:
                print(f"✗ Failed to create sprint for {project['project_name']}")
                if response:
                    print(f"  Response: {response.text}")

    def create_team_members(self):
        """Create mock team members."""
        print("\n3. Creating Team Members...")

        teams = {
            "E-Commerce Platform": [
                {"name": "Sarah Johnson", "email": "sarah.johnson@company.com"},
                {"name": "John Smith", "email": "john.smith@company.com"},
                {"name": "Emily Chen", "email": "emily.chen@company.com"},
                {"name": "David Brown", "email": "david.brown@company.com"},
                {"name": "Lisa Wang", "email": "lisa.wang@company.com"}
            ],
            "Mobile Banking App": [
                {"name": "Mike Chen", "email": "mike.chen@company.com"},
                {"name": "Anna Martinez", "email": "anna.martinez@company.com"},
                {"name": "Robert Taylor", "email": "robert.taylor@company.com"},
                {"name": "Sophie Lee", "email": "sophie.lee@company.com"}
            ],
            "AI Analytics Dashboard": [
                {"name": "Emma Davis", "email": "emma.davis@company.com"},
                {"name": "James Wilson", "email": "james.wilson@company.com"},
                {"name": "Maria Rodriguez", "email": "maria.rodriguez@company.com"},
                {"name": "Kevin Zhang", "email": "kevin.zhang@company.com"}
            ]
        }

        for project in self.created_data["projects"]:
            team_name = project["project_name"]
            if team_name in teams:
                for member in teams[team_name]:
                    contact_data = {
                        "team_name": team_name,
                        "name": member["name"],
                        "email": member["email"]
                    }

                    response = self.make_request("POST", f"{self.api_url}/api/contacts/", contact_data)

                    if response and response.status_code == 201:
                        contact = response.json()
                        self.created_data["team_members"].append(contact)
                        print(f"✓ Created team member: {member['name']} for {team_name}")
                    else:
                        print(f"✗ Failed to create team member: {member['name']}")
                        if response:
                            print(f"  Response: {response.text}")

    def create_user_stories(self):
        """Create mock user stories with various statuses."""
        print("\n4. Creating User Stories...")

        story_templates = {
            "E-Commerce Platform": [
                {"title": "User Authentication System", "points": 8, "priority": "High", "type": "Story"},
                {"title": "Product Catalog API", "points": 13, "priority": "High", "type": "Story"},
                {"title": "Shopping Cart Implementation", "points": 8, "priority": "High", "type": "Story"},
                {"title": "Payment Gateway Integration", "points": 13, "priority": "High", "type": "Story"},
                {"title": "Order Management System", "points": 8, "priority": "Medium", "type": "Story"},
                {"title": "User Profile Management", "points": 5, "priority": "Medium", "type": "Feature"},
                {"title": "Search Functionality", "points": 8, "priority": "Medium", "type": "Feature"},
                {"title": "Email Notifications", "points": 3, "priority": "Low", "type": "Task"},
            ],
            "Mobile Banking App": [
                {"title": "Login with Biometrics", "points": 8, "priority": "High", "type": "Story"},
                {"title": "Account Overview Screen", "points": 5, "priority": "High", "type": "Story"},
                {"title": "Fund Transfer Feature", "points": 13, "priority": "High", "type": "Story"},
                {"title": "Transaction History", "points": 5, "priority": "Medium", "type": "Feature"},
                {"title": "Bill Payment Integration", "points": 8, "priority": "Medium", "type": "Feature"},
            ],
            "AI Analytics Dashboard": [
                {"title": "Data Ingestion Pipeline", "points": 13, "priority": "High", "type": "Story"},
                {"title": "ML Model Training Module", "points": 21, "priority": "High", "type": "Story"},
                {"title": "Real-time Dashboard UI", "points": 13, "priority": "High", "type": "Story"},
                {"title": "User Management System", "points": 8, "priority": "Medium", "type": "Feature"},
                {"title": "Report Generation Engine", "points": 8, "priority": "Medium", "type": "Feature"},
            ]
        }

        statuses = ["To Do", "In Progress", "Done", "In Progress", "To Do"]

        for sprint in self.created_data["sprints"]:
            if "SPR-001" not in sprint["sprint_id"]:
                continue

            project = next((p for p in self.created_data["projects"]
                            if p["project_id"] == sprint["project_id"]), None)

            if not project:
                continue

            stories = story_templates.get(project["project_name"], [])
            team_members = [m for m in self.created_data["team_members"]
                            if m["team_name"] == project["project_name"]]

            for idx, story_template in enumerate(stories[:5]):  # Create 5 stories per sprint
                assignee = random.choice(team_members)["name"] if team_members else "Unassigned"
                status = statuses[idx % len(statuses)]

                story_data = {
                    "project_id": project["project_id"],
                    "sprint_id": sprint["sprint_id"],
                    "story_id": f"{project['project_key']}-{idx + 101}",
                    "story_title": story_template["title"],
                    "assignee": assignee,
                    "status": status,
                    "priority": story_template["priority"],
                    "story_points": story_template["points"],
                    "work_item_type": story_template["type"]
                }

                response = self.make_request("POST", f"{self.api_url}/api/stories/", story_data)

                if response and response.status_code == 201:
                    story = response.json()
                    self.created_data["stories"].append(story)
                    print(f"✓ Created story: {story['story_title']} ({status})")
                else:
                    print(f"✗ Failed to create story: {story_template['title']}")
                    if response:
                        print(f"  Response: {response.text}")

    def display_summary(self):
        """Display summary of created data."""
        print("\n" + "=" * 50)
        print("MOCK DATA CREATION SUMMARY")
        print("=" * 50)

        print(f"\n✅ Created:")
        print(f"   - {len(self.created_data['projects'])} Projects")
        print(f"   - {len(self.created_data['sprints'])} Sprints")
        print(f"   - {len(self.created_data['team_members'])} Team Members")
        print(f"   - {len(self.created_data['stories'])} User Stories")

        print("\n📊 Story Status Distribution:")
        status_counts = {}
        for story in self.created_data["stories"]:
            status = story["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        for status, count in status_counts.items():
            print(f"   - {status}: {count}")

        print("\n🚀 You can now:")
        print("   1. View all data at: http://localhost:8000/docs")
        print("   2. Run the test script: python test_run.py")
        print("   3. Check the API health: http://localhost:8000/health")

    def run_all(self):
        """Run all mock data creation steps."""
        print("🎨 Creating Mock Data for Scrum Agent")
        print("=" * 50)

        # Check if authentication is required
        if not self.check_auth_requirement():
            print("\n❌ Authentication is required but not configured for development.")
            print("\nTo fix this:")
            print("1. Update app/dependencies.py to use the development version")
            print("2. Make sure ENV=development in your .env file")
            print("3. Restart the API server")
            return

        try:
            self.create_projects()
            if self.created_data["projects"]:
                self.create_sprints()
                self.create_team_members()
                self.create_user_stories()

            self.display_summary()

            # Save created data for reference
            with open("../mock_data_ids.json", "w") as f:
                json.dump(self.created_data, f, indent=2)
            print("\n💾 Saved all created IDs to: mock_data_ids.json")

        except Exception as e:
            print(f"\n❌ Error creating mock data: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # Ensure the API is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ API is not running. Please start it first:")
            print("   uvicorn app.main:app --reload")
            exit(1)
    except:
        print("❌ Cannot connect to API. Please ensure it's running at:", BASE_URL)
        print("   Run: uvicorn app.main:app --reload")
        exit(1)

    creator = MockDataCreator()
    creator.run_all()