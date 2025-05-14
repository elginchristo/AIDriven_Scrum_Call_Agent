# test_voice.py - Test voice processing
import asyncio
from app.services.voice import voice_processing_service


async def test_voice_service():
    """Test the voice processing service."""
    print("🎤 Testing Voice Processing Service")
    print("=" * 40)

    # Check service status
    status = voice_processing_service.get_service_status()
    print(f"\nService Status:")
    print(f"  Mode: {status['mode']}")
    print(f"  Google Cloud: {'Enabled' if status['google_cloud_enabled'] else 'Disabled'}")

    # Test text-to-speech
    print("\n1. Testing Text-to-Speech...")
    text = "Hello team, let's start our daily standup meeting."
    audio = await voice_processing_service.text_to_speech(text)
    print(f"✓ Generated audio: {len(audio)} bytes")

    # Test speech-to-text
    print("\n2. Testing Speech-to-Text...")
    result = await voice_processing_service.speech_to_text(audio)
    print(f"✓ Transcript: {result['transcript']}")
    print(f"✓ Segments: {len(result['segments'])}")

    # Test team member response simulation
    if hasattr(voice_processing_service, 'simulate_team_member_response'):
        print("\n3. Testing Team Member Simulation...")
        response = await voice_processing_service.simulate_team_member_response(
            "John Doe",
            "blockers"
        )
        print(f"✓ Simulated response: {response}")

    print("\n✅ Voice service test complete!")


if __name__ == "__main__":
    asyncio.run(test_voice_service())