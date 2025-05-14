# app/agents/driving_call.py
import logging
import asyncio
import json
from datetime import datetime, timedelta
from app.agents.base_agent import BaseAgent
from app.services.voice import voice_processing_service

logger = logging.getLogger(__name__)


class DrivingCallAgent(BaseAgent):
    """Agent responsible for driving the scrum call."""

    def __init__(self, scheduled_call, meeting_session, call_id, redis_client,
                 user_stories, team_members, blockers, current_sprint, aggressiveness_level):
        """Initialize the driving call agent.

        Args:
            scheduled_call: Scheduled call information.
            meeting_session: Meeting platform session.
            call_id: Unique identifier for the call.
            redis_client: Redis client for inter-agent communication.
            user_stories: List of user stories for the current sprint.
            team_members: List of team members.
            blockers: List of current blockers.
            current_sprint: Current sprint information.
            aggressiveness_level: Level of aggressiveness for the agent (1-10).
        """
        super().__init__(call_id, redis_client)
        self.scheduled_call = scheduled_call
        self.meeting_session = meeting_session
        self.user_stories = user_stories
        self.team_members = team_members
        self.blockers = blockers
        self.current_sprint = current_sprint
        self.aggressiveness_level = aggressiveness_level
        self.user_validation_agent = None

        # Call data
        self.call_results = {
            "questions": [],
            "responses": [],
            "missing_participants": [],
            "blockers": [],
            "delays": []
        }

    def set_user_validation_agent(self, agent):
        """Set the user validation agent.

        Args:
            agent: UserValidationAgent instance.
        """
        self.user_validation_agent = agent

    async def start_call(self):
        """Start the scrum call.

        Returns:
            dict: Call results.
        """
        try:
            logger.info("Starting scrum call")

            # Introduce the agent
            intro_message = await self._generate_introduction()
            await self.meeting_session.speak_text(intro_message)
            await asyncio.sleep(3)  # Pause for effect

            # Iterate through team members
            for team_member in self.team_members:
                member_name = team_member["name"]

                # Get user stories assigned to this team member
                assigned_stories = [
                    story for story in self.user_stories
                    if story["assignee"].lower() == member_name.lower()
                ]

                # Get blockers assigned to this team member
                member_blockers = [
                    blocker for blocker in self.blockers
                    if blocker["assignee"].lower() == member_name.lower()
                ]

                # Generate questions for this team member
                questions = await self._generate_questions(member_name, assigned_stories, member_blockers)

                # Ask questions and record response
                for question in questions:
                    # Store question
                    self.call_results["questions"].append({
                        "team_member": member_name,
                        "question": question,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    # Ask the question
                    await self.meeting_session.speak_text(question)

                    # Record response
                    await self.meeting_session.start_recording()

                    # Wait for response (max 2 minutes)
                    response_complete = False
                    start_time = datetime.now()
                    silence_start = None

                    while not response_complete and (datetime.now() - start_time) < timedelta(minutes=2):
                        # Check for silence (no speech for 1 minute)
                        if silence_start and (datetime.now() - silence_start) > timedelta(minutes=1):
                            await self.meeting_session.stop_recording()

                            # Handle missing response
                            logger.warning(f"No response from {member_name} for 1 minute")

                            # Add to missing participants
                            self.call_results["missing_participants"].append(member_name)

                            # Generate a prompt to move on
                            move_on_message = await self._generate_move_on_message(member_name)
                            await self.meeting_session.speak_text(move_on_message)

                            response_complete = True
                            break

                        # TODO: In a real implementation, we would need a way to detect when the response is complete
                        # For now, we'll simulate a response after a random interval
                        await asyncio.sleep(5)

                        # Detect end phrases like "That's it from my side" or "Thank you"
                        # In a real implementation, this would be done by analyzing real-time transcription
                        # For this POC, we'll just simulate it
                        silence_start = datetime.now()

                    if not response_complete:
                        await self.meeting_session.stop_recording()

                        # Handle timeout
                        logger.warning(f"Response timeout for {member_name}")

                        # Add to missing participants
                        self.call_results["missing_participants"].append(member_name)

                        # Generate a prompt to move on
                        move_on_message = await self._generate_move_on_message(member_name)
                        await self.meeting_session.speak_text(move_on_message)

                    # Process response with user validation agent
                    if self.user_validation_agent and not response_complete:
                        # In a real implementation, we would transcribe the audio and pass to the validation agent
                        # Here we'll simulate with a generic response
                        simulated_response = {
                            "team_member": member_name,
                            "response": "I've completed the user authentication module. No blockers today.",
                            "timestamp": datetime.utcnow().isoformat()
                        }

                        self.call_results["responses"].append(simulated_response)

                        # Process with validation agent
                        validation_result = await self.user_validation_agent.process(simulated_response)

                        # Handle blockers or delays if detected
                        if validation_result.get("has_blocker"):
                            self.call_results["blockers"].append(validation_result["blocker"])

                        if validation_result.get("has_delay"):
                            self.call_results["delays"].append(validation_result["delay"])

                # Pause between team members
                await asyncio.sleep(1)

            # Conclude the call
            conclusion_message = await self._generate_conclusion()
            await self.meeting_session.speak_text(conclusion_message)

            # Close the meeting
            await self.meeting_session.close()

            # Store call results in Redis
            await self.store_data("call_results", self.call_results)

            logger.info("Scrum call completed")
            return self.call_results

        except Exception as e:
            logger.error(f"Error in scrum call: {str(e)}")
            # Attempt to close meeting on error
            try:
                await self.meeting_session.close()
            except:
                pass
            raise

    async def _generate_introduction(self):
        """Generate an introduction message for the call.

        Returns:
            str: Introduction message.
        """
        # Calculate sprint progress
        days_passed = (datetime.utcnow().date() - self.current_sprint["start_date"].date()).days
        total_days = (self.current_sprint["end_date"].date() - self.current_sprint["start_date"].date()).days
        sprint_progress = f"{days_passed}/{total_days} days"

        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": f"""
            You are an AI Scrum Master assistant conducting a daily standup meeting.
            You need to create a brief introduction for the meeting.

            Key information:
            - Team: {self.scheduled_call.team_name}
            - Project: {self.scheduled_call.project_name}
            - Sprint: {self.current_sprint['sprint_name']}
            - Sprint Progress: {sprint_progress}
            - Aggressiveness Level: {self.aggressiveness_level}/10

            Create a brief, professional introduction. Be direct but friendly.
            Adjust your tone based on the aggressiveness level (1 = very gentle, 10 = very direct and pushy).
            Don't make the introduction too long - aim for 3-4 sentences maximum.
            """
             },
            {"role": "user", "content": "Generate a scrum call introduction."}
        ]

        # Call OpenAI
        return await self.call_openai(messages, max_tokens=300)

    async def _generate_questions(self, member_name, assigned_stories, member_blockers):
        """Generate questions for a team member.

        Args:
            member_name: Name of the team member.
            assigned_stories: List of stories assigned to the team member.
            member_blockers: List of blockers assigned to the team member.

        Returns:
            list: List of questions.
        """
        # Format stories for prompt
        stories_text = ""
        for story in assigned_stories:
            stories_text += f"- {story['story_id']}: {story['story_title']} (Status: {story['status']}, Points: {story['story_points']})\n"

        if not stories_text:
            stories_text = "No stories assigned."

        # Format blockers for prompt
        blockers_text = ""
        for blocker in member_blockers:
            days_blocked = (datetime.utcnow().date() - blocker["blocker_raised_date"].date()).days
            blockers_text += f"- Blocked item: {blocker['blocked_item_id']} - {blocker['blocked_item_title']}\n"
            blockers_text += f"  Reason: {blocker['blocking_reason']}\n"
            blockers_text += f"  Days blocked: {days_blocked}\n"

        if not blockers_text:
            blockers_text = "No blockers reported."

        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": f"""
            You are an AI Scrum Master assistant conducting a daily standup meeting.
            You need to generate questions for {member_name} based on their assigned stories and blockers.

            Current sprint: {self.current_sprint['sprint_name']}
            Aggressiveness Level: {self.aggressiveness_level}/10

            Assigned Stories:
            {stories_text}

            Current Blockers:
            {blockers_text}

            Generate 1-3 questions that:
            1. Ask about progress on assigned stories
            2. Follow up on any existing blockers
            3. Inquire about any new blockers or issues

            Adjust your tone based on the aggressiveness level (1 = very gentle, 10 = very direct and pushy).
            Each question should be concise and direct.
            """
             },
            {"role": "user", "content": f"Generate questions for {member_name}'s standup update."}
        ]

        # Call OpenAI
        questions_text = await self.call_openai(messages, max_tokens=500)

        # Parse questions (assuming one per line)
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]

        # Add a personalized greeting as the first question
        greeting = f"Good morning, {member_name}. How are you today? Please provide your standup update."
        questions.insert(0, greeting)

        return questions

    async def _generate_move_on_message(self, member_name):
        """Generate a message to move on when a team member doesn't respond.

        Args:
            member_name: Name of the team member.

        Returns:
            str: Message to move on.
        """
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": f"""
            You are an AI Scrum Master assistant conducting a daily standup meeting.
            {member_name} has not responded for over a minute.

            Generate a brief, professional message to:
            1. Note that {member_name} seems to be unavailable
            2. State that you will move on to the next person
            3. Mention that this will be noted in the meeting minutes

            Keep the message concise and professional. Don't be judgmental.
            """
             },
            {"role": "user", "content": f"Generate a message to move on from {member_name} who is not responding."}
        ]

        # Call OpenAI
        return await self.call_openai(messages, max_tokens=200)

    async def _generate_conclusion(self):
        """Generate a conclusion message for the call.

        Returns:
            str: Conclusion message.
        """
        # Gather statistics for conclusion
        num_participants = len(self.team_members) - len(self.call_results["missing_participants"])
        num_blockers = len(self.call_results["blockers"])
        num_delays = len(self.call_results["delays"])

        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": f"""
            You are an AI Scrum Master assistant concluding a daily standup meeting.

            Key information:
            - Team: {self.scheduled_call.team_name}
            - Project: {self.scheduled_call.project_name}
            - Sprint: {self.current_sprint['sprint_name']}
            - Participants: {num_participants}/{len(self.team_members)}
            - Blockers identified: {num_blockers}
            - Delays identified: {num_delays}

            Create a brief, professional conclusion. Be direct but friendly.
            Mention that a meeting summary will be shared via email.
            Thank everyone for their participation.
            Keep it concise - aim for 3-4 sentences maximum.
            """
             },
            {"role": "user", "content": "Generate a scrum call conclusion."}
        ]

        # Call OpenAI
        return await self.call_openai(messages, max_tokens=300)
