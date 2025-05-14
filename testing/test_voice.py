# test_voice_proper.py - Test voice processing with proper Google Cloud settings
import asyncio
from app.services.voice import voice_processing_service


async def test_voice_service():
    """Test the voice processing service."""
    print("🎤 Testing Voice Processing Service")
    print("=" * 40)

    # Check service mode
    print(f"\nService Status:")
    print(f"  Mode: {'Mock' if voice_processing_service.mock_mode else 'Google Cloud'}")

    # Test text-to-speech with various voices
    print("\n1. Testing Text-to-Speech with different voices...")

    test_voices = [
        {
            "name": "Standard Male Voice",
            "params": {
                "language_code": "en-US",
                "name": "en-US-Standard-D"  # Male voice
            }
        },
        {
            "name": "Standard Female Voice",
            "params": {
                "language_code": "en-US",
                "name": "en-US-Standard-E"  # Female voice
            }
        },
        {
            "name": "Neural2 Male Voice",
            "params": {
                "language_code": "en-US",
                "name": "en-US-Neural2-D"  # Neural male voice
            }
        },
        {
            "name": "Neural2 Female Voice",
            "params": {
                "language_code": "en-US",
                "name": "en-US-Neural2-F"  # Neural female voice
            }
        }
    ]

    text = "Hello team, let's start our daily standup meeting."

    for voice_config in test_voices:
        print(f"\nTesting {voice_config['name']}...")
        try:
            audio = await voice_processing_service.text_to_speech(text, voice_config['params'])
            print(f"✓ Generated audio: {len(audio)} bytes")

            # Test the first voice with speech-to-text
            if voice_config['name'] == "Standard Male Voice":
                print("\n2. Testing Speech-to-Text...")
                result = await voice_processing_service.speech_to_text(audio)
                print(f"✓ Transcript: {result['transcript'][:100]}...")
                print(f"✓ Segments: {len(result['segments'])}")

                if result['segments']:
                    print("\nSegments:")
                    for i, segment in enumerate(result['segments'][:3]):  # Show first 3 segments
                        print(f"  {segment['speaker']}: {segment['text'][:50]}...")

        except Exception as e:
            print(f"❌ Error with {voice_config['name']}: {e}")

    print("\n✅ Voice service test complete!")


async def test_conversation_simulation():
    """Test simulating a conversation between multiple speakers."""
    print("\n\n🗣️ Testing Conversation Simulation")
    print("=" * 40)

    # Simulate different team members speaking
    team_responses = [
        ("John", "I completed the authentication module yesterday.", "en-US-Standard-D"),
        ("Sarah", "I'm working on the API endpoints, about 70% done.", "en-US-Standard-E"),
        ("Mike", "I have a blocker with the database connection.", "en-US-Standard-B"),
    ]

    all_audio = []

    for name, text, voice in team_responses:
        print(f"\n{name}: {text}")
        try:
            audio = await voice_processing_service.text_to_speech(text, {
                "language_code": "en-US",
                "name": voice
            })
            all_audio.append(audio)
            print(f"✓ Generated {len(audio)} bytes")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\nConversation simulation complete!")


if __name__ == "__main__":
    print("🚀 Google Cloud Voice Service Test")
    print("=" * 50)

    # Run basic tests
    asyncio.run(test_voice_service())

    # Run conversation simulation
    asyncio.run(test_conversation_simulation())