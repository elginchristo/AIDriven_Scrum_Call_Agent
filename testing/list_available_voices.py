# list_available_voices.py - List all available Google Cloud TTS voices
import asyncio
from google.cloud import texttospeech
import os
from app.config import settings

# Set up credentials
if hasattr(settings, 'GOOGLE_CLOUD') and settings.GOOGLE_CLOUD.CREDENTIALS_FILE:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_CLOUD.CREDENTIALS_FILE


def list_voices():
    """List all available voices from Google Cloud Text-to-Speech."""
    try:
        client = texttospeech.TextToSpeechClient()

        # Request the list of available voices
        response = client.list_voices()

        # Group voices by language
        voices_by_language = {}

        for voice in response.voices:
            lang_code = voice.language_codes[0]
            if lang_code not in voices_by_language:
                voices_by_language[lang_code] = []

            voices_by_language[lang_code].append({
                "name": voice.name,
                "gender": voice.ssml_gender.name,
                "natural_sample_rate": voice.natural_sample_rate_hertz
            })

        # Print English voices (en-US)
        print("🎙️ Available English (US) Voices")
        print("=" * 50)

        if "en-US" in voices_by_language:
            for voice in sorted(voices_by_language["en-US"], key=lambda x: x["name"]):
                print(f"\nVoice: {voice['name']}")
                print(f"  Gender: {voice['gender']}")
                print(f"  Sample Rate: {voice['natural_sample_rate']} Hz")

                # Categorize voice type
                if "Neural2" in voice['name']:
                    print("  Type: Neural2 (High Quality)")
                elif "News" in voice['name']:
                    print("  Type: News (Optimized for news reading)")
                elif "Wavenet" in voice['name']:
                    print("  Type: WaveNet (Natural sounding)")
                elif "Standard" in voice['name']:
                    print("  Type: Standard")
                else:
                    print("  Type: Other")

        # Show summary
        print("\n" + "=" * 50)
        print("Summary:")
        print(f"Total languages available: {len(voices_by_language)}")
        print(f"Total English (US) voices: {len(voices_by_language.get('en-US', []))}")

        # Show recommended voices for the Scrum Agent
        print("\n🌟 Recommended Voices for Scrum Agent:")
        print("  - en-US-Neural2-D (Male, Natural)")
        print("  - en-US-Neural2-E (Female, Natural)")
        print("  - en-US-Neural2-F (Female, Natural)")
        print("  - en-US-Standard-D (Male, Standard)")
        print("  - en-US-Standard-E (Female, Standard)")

    except Exception as e:
        print(f"Error listing voices: {e}")
        print("\nMake sure you have:")
        print("1. Valid Google Cloud credentials")
        print("2. Text-to-Speech API enabled")
        print("3. Proper permissions for the service account")


if __name__ == "__main__":
    list_voices()
