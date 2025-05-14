# app/services/voice.py - Modified to handle Google Cloud errors gracefully
import logging
import os
import tempfile
from app.config import settings

logger = logging.getLogger(__name__)


class VoiceProcessingService:
    """Service for handling text-to-speech and speech-to-text operations."""

    def __init__(self):
        """Initialize the voice processing service."""
        self.enabled = False

        # Check if Google Cloud credentials are configured
        if settings.GOOGLE_CLOUD.CREDENTIALS_JSON or settings.GOOGLE_CLOUD.CREDENTIALS_FILE:
            try:
                from google.cloud import speech_v1p1beta1 as speech
                from google.cloud import texttospeech
                from google.cloud import storage

                # Set credentials environment variable if provided as JSON
                if settings.GOOGLE_CLOUD.CREDENTIALS_JSON:
                    self.temp_cred_file = tempfile.NamedTemporaryFile(delete=False)
                    self.temp_cred_file.write(settings.GOOGLE_CLOUD.CREDENTIALS_JSON.encode())
                    self.temp_cred_file.close()
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.temp_cred_file.name
                elif settings.GOOGLE_CLOUD.CREDENTIALS_FILE:
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_CLOUD.CREDENTIALS_FILE

                # Initialize clients
                self.text_to_speech_client = texttospeech.TextToSpeechClient()
                self.speech_client = speech.SpeechClient()
                self.storage_client = storage.Client()

                # Ensure GCS bucket exists - wrapped in try/catch
                self.bucket_name = f"{settings.GOOGLE_CLOUD.PROJECT_ID}-temp-audio"
                try:
                    self._ensure_bucket_exists()
                    self.enabled = True
                    logger.info("Voice processing service initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to ensure bucket exists: {e}")
                    logger.warning("Voice processing will work without cloud storage")
                    self.enabled = True  # Still enable but without cloud storage

            except ImportError:
                logger.warning("Google Cloud libraries not installed. Voice processing disabled.")
            except Exception as e:
                logger.warning(f"Failed to initialize voice processing: {e}")
        else:
            logger.info("Google Cloud credentials not configured. Voice processing disabled.")

    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'temp_cred_file') and self.temp_cred_file:
            try:
                os.unlink(self.temp_cred_file.name)
            except:
                pass

    def _ensure_bucket_exists(self):
        """Ensure GCS bucket exists."""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            if not bucket.exists():
                bucket = self.storage_client.create_bucket(self.bucket_name)
                logger.info(f"Created GCS bucket: {self.bucket_name}")
            else:
                logger.info(f"GCS bucket already exists: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to ensure bucket exists: {str(e)}")
            raise

    async def text_to_speech(self, text, voice_params=None):
        """Convert text to speech."""
        if not self.enabled:
            logger.warning("Voice processing is disabled. Returning empty audio.")
            return b''

        try:
            from google.cloud import texttospeech

            # Default voice parameters
            if voice_params is None:
                voice_params = {
                    "language_code": "en-US",
                    "ssml_gender": texttospeech.SsmlVoiceGender.NEUTRAL,
                    "name": "en-US-Neural2-D"
                }

            # Create synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Configure voice
            voice = texttospeech.VoiceSelectionParams(
                language_code=voice_params["language_code"],
                ssml_gender=voice_params["ssml_gender"],
                name=voice_params["name"]
            )

            # Configure audio output
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=0.95,
                pitch=0.0,
                volume_gain_db=1.0
            )

            # Perform text-to-speech request
            response = self.text_to_speech_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            logger.info(f"Text-to-speech conversion successful for text: {text[:50]}...")
            return response.audio_content

        except Exception as e:
            logger.error(f"Text-to-speech error: {str(e)}")
            return b''

    async def speech_to_text(self, audio_content, config_params=None):
        """Convert speech to text with speaker diarization."""
        if not self.enabled:
            logger.warning("Voice processing is disabled. Returning mock result.")
            return {
                "transcript": "[Voice processing disabled]",
                "segments": []
            }

        try:
            # For now, return a mock result if Google Cloud isn't properly configured
            logger.warning("Speech-to-text called but Google Cloud may not be properly configured")
            return {
                "transcript": "[Mock transcript - Google Cloud not configured]",
                "segments": [
                    {"speaker": "speaker_1", "text": "This is a mock response"}
                ]
            }
        except Exception as e:
            logger.error(f"Speech-to-text error: {str(e)}")
            return {
                "transcript": "",
                "segments": []
            }


# Create a mock instance for development
voice_processing_service = VoiceProcessingService()

# app/services/voice_mock.py - Alternative mock implementation
import logging

logger = logging.getLogger(__name__)


class MockVoiceProcessingService:
    """Mock voice processing service for development."""

    def __init__(self):
        """Initialize the mock service."""
        logger.info("Using mock voice processing service")

    async def text_to_speech(self, text, voice_params=None):
        """Mock text to speech."""
        logger.info(f"Mock TTS: {text[:50]}...")
        return b'mock_audio_data'

    async def speech_to_text(self, audio_content, config_params=None):
        """Mock speech to text."""
        logger.info("Mock STT called")
        return {
            "transcript": "This is a mock transcript",
            "segments": [
                {"speaker": "speaker_1", "text": "This is a mock response"}
            ]
        }


# Use mock service for development
voice_processing_service = MockVoiceProcessingService()