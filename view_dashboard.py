# view_dashboard.py - Simple dashboard to view mock data
import requests
import json
from datetime import datetime
from collections import defaultdict

BASE_URL = "http://localhost:8000"


class DashboardViewer:
    def __init__(self):
        self.api_url = BASE_URL

    def display_project_dashboard(self, project_id):
        """Display comprehensive dashboard for a project."""
        # Get project details
        project_resp = requests.get(f"{self.api_url}/api/projects/{project_id}")
        if project_resp.status_code != 200:
            print(f"❌ Failed to get project {project_id}")
            return

        project = project_resp.json()

        print(f"\n🏢 PROJECT DASHBOARD: {project['project_name']}")
        print("=" * 60)
        print(f"Project ID: {project['project_id']}")
        print(f"Lead: {project['project_lead']}")
        print(f"Type: {project['project_type']}")

        # Get current sprint
        sprints_resp = requests.get(f"{self.api_url}/api/sprints/?project_id={project_id}")
        if sprints_resp.status_code == 200:
            sprints = sprints_resp.json()
            current_sprint = next((s for s in sprints if "SPR-001" in s["sprint_id"]), None)

            if current_sprint:
                self._display_sprint_info(current_sprint)
                self._display_story_status(project_id, current_sprint["sprint_id"])
                self._display_team_capacity(project_id, current_sprint["sprint_id"])
                self._display_blockers(project_id)
                self._display_velocity_trend(project_id)

    def _display_sprint_info(self, sprint):
        """Display sprint information."""
        print(f"\n📅 CURRENT SPRINT: {sprint['sprint_name']}")
        print("-" * 40)
        print(f"Sprint ID: {sprint['sprint_id']}")
        print(f"Start Date: {sprint['start_date'][:10]}")
        print(f"End Date: {sprint['end_date'][:10]}")
        print(f"Progress: {sprint.get('percent_completion', 0):.1f}%")

        # Sprint burndown visualization (text-based)
        progress = int(sprint.get('percent_completion', 0))
        bar_length = 30
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\nProgress: [{bar}] {progress}%")

    def _display_story_status(self, project_id, sprint_id):
        """Display story status breakdown."""
        stories_resp = requests.get(
            f"{self.api_url}/api/stories/?project_id={project_id}&sprint_id={sprint_id}"
        )

        if stories_resp.status_code == 200:
            stories = stories_resp.json()

            print(f"\n📊 USER STORIES ({len(stories)} total)")
            print("-" * 40)

            # Group by status
            status_groups = defaultdict(list)
            total_points = 0
            completed_points = 0

            for story in stories:
                status_groups[story["status"]].append(story)
                total_points += story["story_points"]
                if story["status"] == "Done":
                    completed_points += story["story_points"]

            # Display status breakdown
            for status in ["To Do", "In Progress", "Done", "Blocked"]:
                if status in status_groups:
                    stories_in_status = status_groups[status]
                    points = sum(s["story_points"] for s in stories_in_status)
                    print(f"\n{status}: {len(stories_in_status)} stories ({points} points)")

                    # Show first few stories
                    for story in stories_in_status[:2]:
                        print(f"  • {story['story_title'][:40]}...")
                        print(f"    {story['assignee']} | {story['story_points']} pts | {story['priority']}")

            # Show velocity
            if total_points > 0:
                velocity_pct = (completed_points / total_points) * 100
                print(f"\n🚀 Velocity: {completed_points}/{total_points} points ({velocity_pct:.1f}%)")

    def _display_team_capacity(self, project_id, sprint_id):
        """Display team capacity."""
        capacity_resp = requests.get(
            f"{self.api_url}/api/team-capacity/?project_id={project_id}&sprint_id={sprint_id}"
        )

        if capacity_resp.status_code == 200:
            capacities = capacity_resp.json()

            print(f"\n👥 TEAM CAPACITY ({len(capacities)} members)")
            print("-" * 40)

            total_available = 0
            total_allocated = 0

            for capacity in capacities:
                available = capacity["available_hours"]
                allocated = capacity["allocated_hours"]
                total_available += available
                total_allocated += allocated

                utilization = (allocated / available * 100) if available > 0 else 0
                print(f"\n{capacity['team_member']}")
                print(f"  Available: {available}h | Allocated: {allocated}h | Utilization: {utilization:.0f}%")

                # Mini bar chart
                bar_length = 20
                filled = int(bar_length * utilization / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"  [{bar}]")

            # Team summary
            if total_available > 0:
                team_util = (total_allocated / total_available * 100)
                print(f"\n📊 Team Utilization: {team_util:.1f}%")
                print(f"Total: {total_allocated}/{total_available} hours")

    def _display_blockers(self, project_id):
        """Display active blockers."""
        blockers_resp = requests.get(f"{self.api_url}/api/blockers/?project_id={project_id}")

        if blockers_resp.status_code == 200:
            blockers = blockers_resp.json()
            open_blockers = [b for b in blockers if b["status"] == "Open"]

            if open_blockers:
                print(f"\n🚫 ACTIVE BLOCKERS ({len(open_blockers)})")
                print("-" * 40)

                for blocker in open_blockers[:3]:  # Show first 3
                    print(f"\n• {blocker['blocked_item_title']}")
                    print(f"  Reason: {blocker['blocking_reason']}")
                    print(f"  Assignee: {blocker['assignee']}")

                    # Calculate days blocked
                    raised_date = datetime.fromisoformat(blocker['blocker_raised_date'].replace('Z', '+00:00'))
                    days_blocked = (datetime.now() - raised_date.replace(tzinfo=None)).days
                    print(f"  Blocked for: {days_blocked} days")

    def _display_velocity_trend(self, project_id):
        """Display velocity trend."""
        velocity_resp = requests.get(f"{self.api_url}/api/velocity/average/{project_id}?num_sprints=5")

        if velocity_resp.status_code == 200:
            velocity_data = velocity_resp.json()

            print(f"\n📈 VELOCITY TREND")
            print("-" * 40)
            print(f"Average Velocity: {velocity_data['average_velocity']:.2f}")
            print(f"Average Deviation: {velocity_data['average_deviation']:.1f}%")
            print(f"Based on: {velocity_data['num_sprints']} sprints")

    def display_team_overview(self):
        """Display overview of all teams."""
        print("\n🏢 TEAM OVERVIEW")
        print("=" * 60)

        # Get all projects
        projects_resp = requests.get(f"{self.api_url}/api/projects/")
        if projects_resp.status_code != 200:
            print("❌ Failed to get projects")
            return

        projects = projects_resp.json()

        for project in projects:
            print(f"\n📁 {project['project_name']}")
            print(f"   Lead: {project['project_lead']}")

            # Get team members
            contacts_resp = requests.get(f"{self.api_url}/api/contacts/?team_name={project['project_name']}")
            if contacts_resp.status_code == 200:
                contacts = contacts_resp.json()
                print(f"   Team Size: {len(contacts)} members")

                # Show team members
                for contact in contacts[:3]:
                    print(f"   • {contact['name']}")
                if len(contacts) > 3:
                    print(f"   ... and {len(contacts) - 3} more")

            # Get sprint info
            sprints_resp = requests.get(f"{self.api_url}/api/sprints/?project_id={project['project_id']}")
            if sprints_resp.status_code == 200:
                sprints = sprints_resp.json()
                current_sprint = next((s for s in sprints if "SPR-001" in s["sprint_id"]), None)
                if current_sprint:
                    print(f"   Current Sprint: {current_sprint['sprint_name']}")
                    print(f"   Progress: {current_sprint.get('percent_completion', 0):.1f}%")

    def display_scheduled_meetings(self):
        """Display upcoming scheduled meetings."""
        print("\n📅 SCHEDULED MEETINGS")
        print("=" * 60)

        schedules_resp = requests.get(f"{self.api_url}/api/schedules/")
        if schedules_resp.status_code != 200:
            print("❌ Failed to get schedules")
            return

        schedules = schedules_resp.json()

        # Sort by scheduled time
        schedules.sort(key=lambda x: x['scheduled_time'])

        for schedule in schedules[:5]:  # Show next 5
            scheduled_time = datetime.fromisoformat(schedule['scheduled_time'].replace('Z', '+00:00'))

            print(f"\n🕐 {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Team: {schedule['team_name']}")
            print(f"   Platform: {schedule['platform']}")
            print(f"   Status: {schedule['status']}")
            print(f"   Recurring: {'Yes' if schedule['is_recurring'] else 'No'}")

            if schedule['is_recurring']:
                print(f"   Pattern: {schedule['recurring_pattern']}")


def main():
    """Main dashboard function."""
    viewer = DashboardViewer()

    print("🎯 SCRUM AGENT DASHBOARD")
    print("=" * 60)

    # Get all projects
    projects_resp = requests.get(f"{BASE_URL}/api/projects/")
    if projects_resp.status_code != 200:
        print("❌ Failed to get projects. Is the API running?")
        return

    projects = projects_resp.json()

    if not projects:
        print("❌ No projects found. Run create_mock_data.py first!")
        return

    while True:
        print("\nAvailable Actions:")
        print("1. View Project Dashboard")
        print("2. Team Overview")
        print("3. Scheduled Meetings")
        print("4. Exit")

        choice = input("\nSelect action (1-4): ")

        if choice == "1":
            print("\nAvailable Projects:")
            for idx, project in enumerate(projects):
                print(f"{idx + 1}. {project['project_name']} ({project['project_id']})")

            project_choice = input("\nSelect project number: ")
            try:
                project_idx = int(project_choice) - 1
                if 0 <= project_idx < len(projects):
                    viewer.display_project_dashboard(projects[project_idx]['project_id'])
                else:
                    print("❌ Invalid project number")
            except ValueError:
                print("❌ Please enter a valid number")

        elif choice == "2":
            viewer.display_team_overview()

        elif choice == "3":
            viewer.display_scheduled_meetings()

        elif choice == "4":
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please select 1-4.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    # Check if API is running
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

    main()