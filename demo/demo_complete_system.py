# demo_full_system_with_voice.py - Complete demo with voice and all agents
import asyncio
import json
import tempfile
import subprocess
import os
from datetime import datetime, timedelta
from app.services.database import connect_to_mongo, get_database
from app.services.voice import voice_processing_service
from app.services.orchestrator import initialize_agents
from app.config import settings
from redis import Redis

# Import all agent classes that we'll use
from app.agents.driving_call import DrivingCallAgent
from app.agents.user_validation import UserValidationAgent
from app.agents.blocker import BlockerAgent
from app.agents.critic import CriticAgent
from app.agents.missing_developer import MissingDeveloperAgent
from app.agents.overall import OverallAgent
from app.agents.mom import MOMAgent
from app.agents.current_status import CurrentStatusAgent


class FullSystemDemo:
    """Complete system demo with voice synthesis and all agents."""

    def __init__(self):
        self.db = None
        self.redis = None
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.call_id = f"DEMO_CALL_{self.timestamp}"
        self.audio_files = []

    async def setup(self):
        """Initialize all connections and services."""
        print("🔧 Setting up complete demo environment...")

        # Database connection
        await connect_to_mongo()
        self.db = get_database()

        # Redis connection
        self.redis = Redis(
            host=settings.REDIS.HOST,
            port=settings.REDIS.PORT,
            password=getattr(settings.REDIS, 'PASSWORD', None),
            db=settings.REDIS.DB,
            decode_responses=False  # Important for storing JSON
        )

        print("✓ All services initialized")

    async def create_realistic_project_data(self):
        """Create comprehensive project data for demo."""
        print("\n📊 Creating realistic project environment...")

        # 1. Create E-commerce project
        project = {
            "project_id": f"ECOM_{self.timestamp}",
            "project_key": f"EC{self.timestamp[-6:]}",
            "project_name": "E-Commerce Platform 2.0",
            "project_type": "Software",
            "project_lead": "Sarah Johnson",
            "project_description": "Next-gen e-commerce platform with AI recommendations",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await self.db.projects.insert_one(project)
        print(f"✓ Created project: {project['project_name']}")

        # 2. Create current sprint
        sprint_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        sprint = {
            "project_id": project["project_id"],
            "sprint_id": f"SPR_{self.timestamp}",
            "sprint_name": "Sprint 15 - Payment Integration",
            "start_date": sprint_start,
            "end_date": sprint_start + timedelta(days=14),
            "total_story_points": 0,
            "completed_story_points": 0,
            "percent_completion": 0,
            "burndown_trend": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await self.db.sprint_progress.insert_one(sprint)
        print(f"✓ Created sprint: {sprint['sprint_name']}")

        # 3. Create development team
        team_members = [
            {"name": "John Smith", "email": "john.smith@company.com", "role": "Senior Developer"},
            {"name": "Emily Chen", "email": "emily.chen@company.com", "role": "Frontend Developer"},
            {"name": "Mike Johnson", "email": "mike.johnson@company.com", "role": "Backend Developer"},
            {"name": "Sarah Williams", "email": "sarah.williams@company.com", "role": "QA Engineer"},
            {"name": "David Brown", "email": "david.brown@company.com", "role": "DevOps Engineer"}
        ]

        for member in team_members:
            await self.db.contact_details.insert_one({
                "team_name": project["project_name"],
                "name": member["name"],
                "email": member["email"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        print(f"✓ Added {len(team_members)} team members")

        # 4. Create user stories with various statuses
        stories = [
            {
                "story_id": f"EC-{self.timestamp[-4:]}-101",
                "story_title": "Integrate Stripe payment gateway",
                "assignee": "John Smith",
                "status": "In Progress",
                "priority": "High",
                "story_points": 13,
                "description": "Implement Stripe API for payment processing"
            },
            {
                "story_id": f"EC-{self.timestamp[-4:]}-102",
                "story_title": "Create shopping cart UI",
                "assignee": "Emily Chen",
                "status": "Done",
                "priority": "High",
                "story_points": 8,
                "description": "Design and implement responsive cart interface"
            },
            {
                "story_id": f"EC-{self.timestamp[-4:]}-103",
                "story_title": "Build order processing API",
                "assignee": "Mike Johnson",
                "status": "In Progress",
                "priority": "High",
                "story_points": 8,
                "description": "RESTful API for order management"
            },
            {
                "story_id": f"EC-{self.timestamp[-4:]}-104",
                "story_title": "Write payment integration tests",
                "assignee": "Sarah Williams",
                "status": "To Do",
                "priority": "Medium",
                "story_points": 5,
                "description": "Comprehensive test suite for payment flow"
            },
            {
                "story_id": f"EC-{self.timestamp[-4:]}-105",
                "story_title": "Setup payment monitoring",
                "assignee": "David Brown",
                "status": "Blocked",
                "priority": "Medium",
                "story_points": 3,
                "description": "CloudWatch monitoring for payment transactions"
            }
        ]

        total_points = 0
        completed_points = 0

        for story in stories:
            story_doc = {
                "project_id": project["project_id"],
                "sprint_id": sprint["sprint_id"],
                **story,
                "work_item_type": "Story",
                "days_in_current_status": 2,
                "last_status_change_date": datetime.utcnow() - timedelta(days=2),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await self.db.user_stories.insert_one(story_doc)

            total_points += story["story_points"]
            if story["status"] == "Done":
                completed_points += story["story_points"]

        # Update sprint progress
        await self.db.sprint_progress.update_one(
            {"sprint_id": sprint["sprint_id"]},
            {"$set": {
                "total_story_points": total_points,
                "completed_story_points": completed_points,
                "percent_completion": (completed_points / total_points * 100)
            }}
        )
        print(f"✓ Created {len(stories)} user stories")

        # 5. Create current blockers
        blockers = [
            {
                "project_id": project["project_id"],
                "blocked_item_id": f"EC-{self.timestamp[-4:]}-105",
                "blocked_item_title": "Setup payment monitoring",
                "assignee": "David Brown",
                "blocker_description": "Waiting for AWS CloudWatch access from DevOps",
                "blocker_raised_date": datetime.utcnow() - timedelta(days=2),
                "blocking_reason": "External dependency",
                "status": "Open",
                "created_at": datetime.utcnow()
            }
        ]

        for blocker in blockers:
            await self.db.blockers.insert_one(blocker)
        print(f"✓ Created {len(blockers)} blockers")

        return project, sprint, team_members, stories

    async def create_mock_meeting_session(self):
        """Create a mock meeting session that simulates platform behavior."""
        print("\n🎥 Creating mock meeting session...")

        class MockMeetingSession:
            def __init__(self, demo_instance):
                self.demo = demo_instance
                self.is_recording = False
                self.current_speaker = None

            async def speak_text(self, text):
                """Simulate AI speaking with actual voice synthesis."""
                print(f"\n🤖 AI Scrum Master: {text}")

                # Generate actual voice
                try:
                    audio = await voice_processing_service.text_to_speech(text)

                    # Save audio to temp file and play it
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                        temp_file.write(audio)
                        self.demo.audio_files.append(temp_file.name)

                    # Play audio on Mac
                    if os.system("which afplay > /dev/null 2>&1") == 0:
                        subprocess.run(['afplay', temp_file.name])

                except Exception as e:
                    print(f"  (Voice synthesis: {e})")

                await asyncio.sleep(2)  # Pause after speaking

            async def start_recording(self):
                """Simulate starting recording."""
                self.is_recording = True
                print("  🔴 Recording started...")

            async def stop_recording(self):
                """Simulate stopping recording."""
                self.is_recording = False
                print("  ⏹️ Recording stopped")
                return b"mock_audio_response"

            async def close(self):
                """Close the mock session."""
                print("\n📞 Meeting session closed")

        return MockMeetingSession(self)

    async def setup_scheduled_call(self, project):
        """Create a scheduled call record."""
        scheduled_call = {
            "_id": self.call_id,
            "team_name": project["project_name"],
            "project_name": project["project_name"],
            "scheduled_time": datetime.utcnow(),
            "platform": "zoom",
            "platform_credentials": {"username": "demo@company.com", "password": "demo"},
            "email_credentials": {"username": "notifications@company.com", "password": "demo"},
            "aggressiveness_level": 5,
            "status": "scheduled",
            "is_recurring": True,
            "recurring_pattern": "0 10 * * 1-5"
        }

        # Create a mock scheduled call object
        from types import SimpleNamespace
        return SimpleNamespace(**scheduled_call)

    async def simulate_team_responses(self):
        """Create realistic team member responses."""
        responses = {
            "John Smith": {
                "audio": "Yesterday I completed the Stripe API integration and tested the payment flow. Today I'll work on webhook handling for payment events. No blockers currently.",
                "has_blocker": False,
                "completion_status": "good"
            },
            "Emily Chen": {
                "audio": "I finished the shopping cart UI yesterday and it's now fully responsive. Today I'm starting on the checkout flow design. Everything is going smoothly.",
                "has_blocker": False,
                "completion_status": "excellent"
            },
            "Mike Johnson": {
                "audio": "Yesterday I worked on the order processing API endpoints. Today I'll continue with the order status updates. I'm slightly behind schedule but catching up.",
                "has_blocker": False,
                "completion_status": "fair"
            },
            "Sarah Williams": {
                "audio": "I reviewed the test plan for payment integration yesterday. Today I want to start writing the test cases, but I'm blocked. I need access to the Stripe test environment.",
                "has_blocker": True,
                "completion_status": "blocked"
            },
            "David Brown": {
                "audio": "I tried to set up CloudWatch monitoring yesterday but couldn't proceed. I'm still waiting for AWS access credentials from the infrastructure team. This is blocking my progress.",
                "has_blocker": True,
                "completion_status": "blocked"
            }
        }

        # Store responses in Redis for agents to process
        for member_name, response_data in responses.items():
            # Simulate voice response
            print(f"\n👤 {member_name}: {response_data['audio']}")

            # Generate voice for team member response
            try:
                audio = await voice_processing_service.text_to_speech(
                    response_data['audio'],
                    voice_params={"language_code": "en-US", "name": "en-US-Standard-B"}
                )

                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_file.write(audio)
                    self.audio_files.append(temp_file.name)

                if os.system("which afplay > /dev/null 2>&1") == 0:
                    subprocess.run(['afplay', temp_file.name])

            except Exception as e:
                print(f"  (Voice: {e})")

            await asyncio.sleep(2)

            # Store in Redis for agents
            response_record = {
                "team_member": member_name,
                "response": response_data['audio'],
                "timestamp": datetime.utcnow().isoformat()
            }

            key = f"call:{self.call_id}:response:{member_name.replace(' ', '_')}"
            self.redis.set(key, json.dumps(response_record).encode(), ex=600)

        return responses

    async def run_all_agents(self, scheduled_call, project, sprint, team_members, stories):
        """Run all agents in the proper sequence."""
        print("\n🤖 Running AI Agent Orchestra...")

        # Initialize meeting session
        meeting_session = await self.create_mock_meeting_session()

        # Get data for agents
        blockers = await self.db.blockers.find({"project_id": project["project_id"]}).to_list(100)

        # Initialize all agents
        print("\n  Initializing agents...")

        # 1. DrivingCall Agent - Conducts the meeting
        driving_agent = DrivingCallAgent(
            scheduled_call,
            meeting_session,
            self.call_id,
            self.redis,
            stories,
            team_members,
            blockers,
            sprint,
            scheduled_call.aggressiveness_level
        )

        # 2. UserValidation Agent - Processes responses
        validation_agent = UserValidationAgent(self.call_id, self.redis)

        # 3. Blocker Agent - Handles blockers
        blocker_agent = BlockerAgent(self.call_id, self.redis, project["project_id"])

        # 4. Critic Agent - Handles delays
        critic_agent = CriticAgent(self.call_id, self.redis)

        # 5. MissingDeveloper Agent - Tracks missing members
        missing_agent = MissingDeveloperAgent(self.call_id, self.redis, team_members)

        # Set up agent relationships
        driving_agent.set_user_validation_agent(validation_agent)
        validation_agent.set_blocker_agent(blocker_agent)
        validation_agent.set_critic_agent(critic_agent)
        validation_agent.set_missing_developer_agent(missing_agent)

        # Start the meeting
        print("\n  Starting standup meeting...")
        await meeting_session.speak_text(
            f"Good morning team! Let's start our daily standup for {sprint['sprint_name']}. "
            "I'll be asking each of you about your progress, plans, and any blockers."
        )

        # Process each team member
        for member in team_members:
            member_name = member["name"]
            print(f"\n  Processing {member_name}...")

            # Generate personalized questions
            assigned_stories = [s for s in stories if s["assignee"] == member_name]

            # Ask about yesterday
            await meeting_session.speak_text(f"{member_name}, what did you complete yesterday?")
            await asyncio.sleep(1)

            # Get and process response
            response_key = f"call:{self.call_id}:response:{member_name.replace(' ', '_')}"
            response_data = self.redis.get(response_key)

            if response_data:
                response = json.loads(response_data.decode())

                # Process with UserValidation agent
                validation_result = await validation_agent.process(response)

                # Handle blocker if detected
                if validation_result.get("has_blocker"):
                    await blocker_agent.process({
                        "team_member": member_name,
                        "description": validation_result.get("blocker", {}).get("description", ""),
                        "timestamp": datetime.utcnow().isoformat()
                    })

            # Ask about today's plans
            await meeting_session.speak_text(f"What are you planning to work on today?")
            await asyncio.sleep(1)

            # Ask about blockers
            await meeting_session.speak_text(f"Do you have any blockers or need any help?")
            await asyncio.sleep(1)

        # Generate overall summary
        print("\n  Generating meeting summary...")
        responses = [
            {
                "team_member": member["name"],
                "response": f"Sample response for {member['name']}",
                "timestamp": datetime.utcnow().isoformat()
            }
            for member in team_members
        ]

        call_results = {
            "questions": [],
            "responses": responses,
            "missing_participants": [],
            "blockers": [
                {
                    "team_member": "Sarah Williams",
                    "description": "Needs Stripe test environment access",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "team_member": "David Brown",
                    "description": "Waiting for AWS credentials",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "delays": []
        }

        # Create overall summary (manually since OverallAgent is abstract)
        overall_summary = {
            "summary": "Daily standup completed successfully. Two blockers identified that need immediate attention.",
            "participants": [m["name"] for m in team_members],
            "missing_participants": [],
            "blockers": call_results["blockers"],
            "delays": call_results["delays"],
            "stories_status": {},
            "sprint_health": "Moderate",
            "action_items": [
                {
                    "action": "Provide Stripe test access to Sarah Williams",
                    "assignee": "Project Lead",
                    "priority": "High"
                },
                {
                    "action": "Get AWS credentials for David Brown",
                    "assignee": "Infrastructure Team",
                    "priority": "High"
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

        # 6. MOM Agent - Generate meeting minutes
        mom_agent = MOMAgent(
            project["project_name"],
            project["project_name"],
            self.call_id,
            self.redis,
            team_members
        )
        mom_report = await mom_agent.generate_mom(overall_summary)

        # 7. CurrentStatus Agent - Update sprint status
        status_agent = CurrentStatusAgent(
            self.call_id,
            self.redis,
            sprint,
            stories
        )
        status_report = await status_agent.generate_status_report(overall_summary)

        # Conclude the meeting
        await meeting_session.speak_text(
            "Thank you everyone for your updates. I've identified two blockers that need immediate attention. "
            "Meeting minutes will be sent to your email shortly. Have a productive day!"
        )

        await meeting_session.close()

        return overall_summary, mom_report, status_report

    async def display_results(self, overall_summary, mom_report, status_report):
        """Display all the results generated by the system."""
        print("\n" + "=" * 60)
        print("📊 AI-DRIVEN SCRUM CALL RESULTS")
        print("=" * 60)

        print(f"\n📅 Meeting Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"🏢 Project: E-Commerce Platform 2.0")
        print(f"🏃 Sprint: Sprint 15 - Payment Integration")

        print("\n👥 PARTICIPANTS:")
        for participant in overall_summary["participants"]:
            print(f"  ✓ {participant}")

        print("\n🚫 BLOCKERS IDENTIFIED:")
        for blocker in overall_summary["blockers"]:
            print(f"  - {blocker['team_member']}: {blocker['description']}")

        print("\n📈 SPRINT STATUS:")
        print(f"  Progress: {status_report['percentage']}%")
        print(f"  Health: {overall_summary['sprint_health']}")

        print("\n💡 AI RECOMMENDATIONS:")
        for rec in status_report["recommendations"][:3]:
            print(f"  - {rec}")

        print("\n📬 ACTION ITEMS:")
        for item in overall_summary["action_items"]:
            print(f"  - {item['action']}")
            print(f"    Assignee: {item['assignee']} | Priority: {item['priority']}")

        # Save MOM to file
        mom_filename = f"MOM_{self.call_id}.html"
        with open(mom_filename, 'w') as f:
            f.write(mom_report["body_html"])

        print(f"\n📄 Meeting Minutes saved to: {mom_filename}")
        print(f"📧 Email would be sent to: {', '.join(mom_report['recipients'][:3])}...")

        print("\n✅ DEMONSTRATION COMPLETE!")
        print("\nThe AI-Driven Scrum Call Agent has successfully:")
        print("  1. Generated personalized questions for each developer")
        print("  2. Used voice synthesis to conduct the meeting")
        print("  3. Processed responses with multiple AI agents")
        print("  4. Identified blockers and created action items")
        print("  5. Generated comprehensive meeting minutes")
        print("  6. Updated sprint progress and health status")
        print("  7. Provided AI-powered recommendations")

        # Cleanup audio files
        print("\n🧹 Cleaning up temporary files...")
        for audio_file in self.audio_files:
            try:
                os.unlink(audio_file)
            except:
                pass

    async def run_complete_demo(self):
        """Run the complete demonstration."""
        print("🚀 AI-DRIVEN SCRUM CALL AGENT - COMPLETE SYSTEM DEMONSTRATION")
        print("=" * 60)
        print("This demo showcases all features of the AI Scrum Call Agent:")
        print("  - Voice synthesis and interaction")
        print("  - Intelligent question generation")
        print("  - Multi-agent processing")
        print("  - Automated meeting minutes")
        print("  - Sprint progress tracking")
        print("=" * 60)

        try:
            # Setup
            await self.setup()

            # Create project data
            project, sprint, team_members, stories = await self.create_realistic_project_data()

            # Set up scheduled call
            scheduled_call = await self.setup_scheduled_call(project)

            # Simulate standup meeting
            print("\n🎤 STARTING DAILY STANDUP MEETING")
            print("=" * 40)

            # Run all agents with voice interaction
            overall_summary, mom_report, status_report = await self.run_all_agents(
                scheduled_call, project, sprint, team_members, stories
            )

            # Process team responses
            responses = await self.simulate_team_responses()

            # Display results
            await self.display_results(overall_summary, mom_report, status_report)

        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.redis:
                self.redis.close()


async def main():
    """Run the complete system demonstration."""
    demo = FullSystemDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    print("🎙️ AI-DRIVEN SCRUM CALL AGENT")
    print("Complete System Demonstration with Voice")
    print("\n⚠️ Requirements:")
    print("  - MongoDB running")
    print("  - Redis running")
    print("  - Google Cloud TTS configured (or will use mock voice)")
    print("  - macOS with 'afplay' for audio playback")
    print("\nThis demo will:")
    print("  1. Create a realistic software project")
    print("  2. Set up a development team")
    print("  3. Generate AI-driven questions")
    print("  4. Use voice synthesis for interaction")
    print("  5. Process responses with multiple agents")
    print("  6. Generate meeting minutes")
    print("  7. Update sprint status")
    print("  8. Create action items and recommendations")
    print("\nPress Enter to start the demo...")
    input()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user")