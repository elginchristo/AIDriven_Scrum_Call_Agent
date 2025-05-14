# run_mock_scrum_call.py - Simple mock scrum call runner
import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000"


def run_mock_scrum_call():
    """Run a simple mock scrum call."""
    print("🎙️ MOCK SCRUM CALL RUNNER")
    print("=" * 50)

    # 1. Get existing project and sprint
    print("\n1. Getting existing data...")

    # Get projects
    response = requests.get(f"{BASE_URL}/api/projects/")
    if response.status_code != 200:
        print("Error: Could not fetch projects")
        return

    projects = response.json()
    if not projects:
        print("No projects found. Please run create_mock_data.py first")
        return

    project = projects[0]
    print(f"Using project: {project['project_name']}")

    # Get sprint
    response = requests.get(f"{BASE_URL}/api/sprints/", params={"project_id": project['project_id']})
    sprints = response.json()
    if not sprints:
        print("No sprints found")
        return

    sprint = sprints[0]
    print(f"Using sprint: {sprint['sprint_name']}")

    # Get team members
    response = requests.get(f"{BASE_URL}/api/contacts/", params={"team_name": project['project_name']})
    team_members = response.json()
    print(f"Found {len(team_members)} team members")

    # Get stories
    response = requests.get(f"{BASE_URL}/api/stories/",
                            params={
                                "project_id": project['project_id'],
                                "sprint_id": sprint['sprint_id']
                            })
    stories = response.json()
    print(f"Found {len(stories)} stories")

    # 2. Create a scheduled call
    print("\n2. Creating scheduled call...")

    schedule_data = {
        "team_name": project['project_name'],
        "project_name": project['project_name'],
        "scheduled_time": (datetime.now() + timedelta(seconds=10)).isoformat(),
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

    response = requests.post(f"{BASE_URL}/api/schedules/", json=schedule_data)
    if response.status_code == 201:
        scheduled_call = response.json()
        print(f"✓ Created scheduled call: {scheduled_call['id']}")
    else:
        print(f"Error creating schedule: {response.text}")
        return

    # 3. Simulate the scrum call
    print("\n3. Simulating scrum call in 10 seconds...")
    time.sleep(10)

    print("\n🎤 SCRUM CALL IN PROGRESS")
    print("-" * 30)

    call_transcript = []

    print("\nAI Scrum Master: Good morning team! Let's start our daily standup.")
    call_transcript.append({
        "speaker": "AI Scrum Master",
        "text": "Good morning team! Let's start our daily standup.",
        "timestamp": datetime.now().isoformat()
    })

    time.sleep(2)

    # Go through each team member
    for member in team_members[:3]:  # Limit to first 3 for demo
        print(f"\nAI Scrum Master: {member['name']}, what did you complete yesterday?")
        call_transcript.append({
            "speaker": "AI Scrum Master",
            "text": f"{member['name']}, what did you complete yesterday?",
            "timestamp": datetime.now().isoformat()
        })

        time.sleep(2)

        # Find assigned stories
        assigned_stories = [s for s in stories if s['assignee'] == member['name']]

        if assigned_stories and assigned_stories[0]['status'] == 'Done':
            response_text = f"I completed {assigned_stories[0]['story_title']}"
        elif assigned_stories and assigned_stories[0]['status'] == 'In Progress':
            response_text = f"I made progress on {assigned_stories[0]['story_title']}, it's about 70% done"
        else:
            response_text = "I was working on some setup tasks"

        print(f"{member['name']}: {response_text}")
        call_transcript.append({
            "speaker": member['name'],
            "text": response_text,
            "timestamp": datetime.now().isoformat()
        })

        time.sleep(2)

        print(f"AI Scrum Master: What are you working on today?")
        call_transcript.append({
            "speaker": "AI Scrum Master",
            "text": "What are you working on today?",
            "timestamp": datetime.now().isoformat()
        })

        time.sleep(2)

        if assigned_stories:
            if assigned_stories[0]['status'] == 'To Do':
                today_response = f"I'll start working on {assigned_stories[0]['story_title']}"
            elif assigned_stories[0]['status'] == 'In Progress':
                today_response = f"I'll continue with {assigned_stories[0]['story_title']} and try to complete it"
            else:
                today_response = "I'll pick up the next task from the backlog"
        else:
            today_response = "I'll check with the team lead for my next assignment"

        print(f"{member['name']}: {today_response}")
        call_transcript.append({
            "speaker": member['name'],
            "text": today_response,
            "timestamp": datetime.now().isoformat()
        })

        time.sleep(2)

        print(f"AI Scrum Master: Any blockers?")
        call_transcript.append({
            "speaker": "AI Scrum Master",
            "text": "Any blockers?",
            "timestamp": datetime.now().isoformat()
        })

        time.sleep(2)

        # Simulate one blocker
        if member['name'] == team_members[1]['name']:
            blocker_response = "Yes, I'm waiting for API credentials from the DevOps team"
            print(f"{member['name']}: {blocker_response}")
            call_transcript.append({
                "speaker": member['name'],
                "text": blocker_response,
                "timestamp": datetime.now().isoformat()
            })
        else:
            print(f"{member['name']}: No blockers")
            call_transcript.append({
                "speaker": member['name'],
                "text": "No blockers",
                "timestamp": datetime.now().isoformat()
            })

        time.sleep(1)

    print("\nAI Scrum Master: Thank you everyone. I'll send out the meeting minutes shortly.")
    call_transcript.append({
        "speaker": "AI Scrum Master",
        "text": "Thank you everyone. I'll send out the meeting minutes shortly.",
        "timestamp": datetime.now().isoformat()
    })

    # 4. Generate summary
    print("\n" + "=" * 50)
    print("📋 SCRUM CALL SUMMARY")
    print("=" * 50)

    summary = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "participants": [m['name'] for m in team_members[:3]],
        "blockers": [
            {
                "team_member": team_members[1]['name'],
                "description": "Waiting for API credentials from DevOps team"
            }
        ],
        "progress_updates": [],
        "sprint_health": "Good"
    }

    print(f"\nDate: {summary['date']}")
    print(f"Participants: {', '.join(summary['participants'])}")
    print(f"\nBlockers:")
    for blocker in summary['blockers']:
        print(f"  - {blocker['team_member']}: {blocker['description']}")

    print(f"\nSprint Health: {summary['sprint_health']}")

    # 5. Update sprint progress
    print("\n📈 Sprint Progress:")
    total_points = sum(s['story_points'] for s in stories)
    completed_points = sum(s['story_points'] for s in stories if s['status'] == 'Done')
    progress = (completed_points / total_points * 100) if total_points > 0 else 0

    print(f"  Total Points: {total_points}")
    print(f"  Completed Points: {completed_points}")
    print(f"  Progress: {progress:.1f}%")

    # 6. Mock email notification
    print("\n📧 Email Notification (Mock):")
    print(f"  To: {', '.join([m['email'] for m in team_members[:3]])}")
    print(f"  Subject: Daily Standup Summary - {project['project_name']}")
    print("  Body: Meeting minutes attached")

    print("\n✅ Mock scrum call completed!")

    # Save the transcript to a file
    with open("scrum_call_transcript.json", "w") as f:
        json.dump({
            "call_id": scheduled_call['id'],
            "project": project['project_name'],
            "sprint": sprint['sprint_name'],
            "transcript": call_transcript,
            "summary": summary
        }, f, indent=2)

    print("\n💾 Transcript saved to: scrum_call_transcript.json")


if __name__ == "__main__":
    run_mock_scrum_call()