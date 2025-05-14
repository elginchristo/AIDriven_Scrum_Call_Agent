# check_voice_setup.py - Check voice service setup
import os
import asyncio
from app.services.voice import voice_processing_service
from app.config import settings


def check_google_cloud_setup():
    """Check Google Cloud configuration."""
    print("🔍 Checking Google Cloud Setup")
    print("=" * 40)

    # Check environment variable
    gcloud_creds_env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    print(f"Environment GOOGLE_APPLICATION_CREDENTIALS: {gcloud_creds_env or 'Not set'}")

    # Check settings
    print(f"Settings GOOGLE_CLOUD.PROJECT_ID: {settings.GOOGLE_CLOUD.PROJECT_ID}")
    print(f"Settings GOOGLE_CLOUD.CREDENTIALS_FILE: {settings.GOOGLE_CLOUD.CREDENTIALS_FILE}")

    # Check if credentials file exists
    if settings.GOOGLE_CLOUD.CREDENTIALS_FILE:
        if os.path.exists(settings.GOOGLE_CLOUD.CREDENTIALS_FILE):
            print(f"✓ Credentials file exists: {settings.GOOGLE_CLOUD.CREDENTIALS_FILE}")
        else:
            print(f"❌ Credentials file not found: {settings.GOOGLE_CLOUD.CREDENTIALS_FILE}")

    # Check service mode
    print(f"\nVoice Service Mode: {'Mock' if voice_processing_service.mock_mode else 'Google Cloud'}")

    if voice_processing_service.mock_mode:
        print("\n⚠️  Voice service is running in MOCK mode")
        print("This means Google Cloud is not properly configured.")
        print("\nTo use Google Cloud services:")
        print("1. Create a service account in Google Cloud Console")
        print("2. Download the credentials JSON file")
        print("3. Update .env file with:")
        print("   GOOGLE_CLOUD__CREDENTIALS_FILE=/path/to/credentials.json")
        print("   GOOGLE_CLOUD__PROJECT_ID=your-project-id")
        print("4. Restart the application")
    else:
        print("\n✅ Voice service is using Google Cloud")


async def test_basic_functionality():
    """Test basic voice functionality."""
    print("\n\n🧪 Testing Basic Functionality")
    print("=" * 40)

    try:
        # Test TTS
        print("\nTesting Text-to-Speech...")
        text = "This is a test"
        audio = await voice_processing_service.text_to_speech(text)
        print(f"✓ TTS Result: {len(audio)} bytes")

        # Test STT
        print("\nTesting Speech-to-Text...")
        result = await voice_processing_service.speech_to_text(audio)
        print(f"✓ STT Result: {result['transcript']}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all checks."""
    print("🎙️ VOICE SERVICE SETUP CHECK")
    print("=" * 50)

    check_google_cloud_setup()
    await test_basic_functionality()

    print("\n" + "=" * 50)
    print("Check complete!")


if __name__ == "__main__":
    asyncio.run(main())