# app/services/voice.py - Updated with proper Google Cloud handling
import logging
import os
import tempfile
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech
from google.cloud import storage
from app.config import settings

logger = logging.getLogger(__name__)


class VoiceProcessingService:
    """Service for handling text-to-speech and speech-to-text operations."""

    def __init__(self):
        """Initialize the voice processing service."""
        self.mock_mode = False

        try:
            # Set credentials if provided
            if hasattr(settings, 'GOOGLE_CLOUD') and settings.GOOGLE_CLOUD.CREDENTIALS_FILE:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_CLOUD.CREDENTIALS_FILE

            # Initialize clients
            self.text_to_speech_client = texttospeech.TextToSpeechClient()
            self.speech_client = speech.SpeechClient()
            self.storage_client = storage.Client()

            # Try to create/access bucket
            self.bucket_name = f"{settings.GOOGLE_CLOUD.PROJECT_ID}-temp-audio"
            self._ensure_bucket_exists()

            logger.info("Voice processing service initialized with Google Cloud")

        except Exception as e:
            logger.warning(f"Failed to initialize Google Cloud services: {e}")
            logger.warning("Falling back to mock mode")
            self.mock_mode = True

    def _ensure_bucket_exists(self):
        """Ensure GCS bucket exists."""
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            if not bucket.exists():
                bucket = self.storage_client.create_bucket(self.bucket_name, location="US")
                logger.info(f"Created GCS bucket: {self.bucket_name}")
            else:
                logger.info(f"GCS bucket already exists: {self.bucket_name}")
        except Exception as e:
            logger.warning(f"Failed to ensure bucket exists: {e}")
            raise

    async def text_to_speech(self, text, voice_params=None):
        """Convert text to speech."""
        if self.mock_mode:
            logger.info(f"Mock TTS: {text[:50]}...")
            return b"mock_audio_content"

        try:
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
                name=voice_params.get("name")
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

            logger.info(f"Text-to-speech conversion successful")
            return response.audio_content

        except Exception as e:
            logger.error(f"Text-to-speech error: {str(e)}")
            # Fall back to mock mode
            return b"mock_audio_content"

    async def speech_to_text(self, audio_content, config_params=None):
        """Convert speech to text with speaker diarization."""
        if self.mock_mode:
            logger.info("Mock STT: Converting audio to text")
            return {
                "transcript": "This is a mock transcription.",
                "segments": [
                    {
                        "speaker": "speaker_1",
                        "text": "This is a mock transcription."
                    }
                ]
            }

        try:
            # Upload audio to GCS
            filename = f"speech-{os.urandom(8).hex()}.wav"
            blob = self.storage_client.bucket(self.bucket_name).blob(filename)
            blob.upload_from_string(audio_content)
            gcs_uri = f"gs://{self.bucket_name}/{filename}"

            # Configure recognition request
            if config_params is None:
                config_params = {
                    "language_code": "en-US",
                    "enable_speaker_diarization": True,
                    "diarization_speaker_count": 10,
                    "model": "phone_call",
                    "use_enhanced": True,
                    "enable_automatic_punctuation": True
                }

            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=config_params["language_code"],
                enable_speaker_diarization=config_params["enable_speaker_diarization"],
                diarization_speaker_count=config_params["diarization_speaker_count"],
                model=config_params["model"],
                use_enhanced=config_params["use_enhanced"],
                enable_automatic_punctuation=config_params["enable_automatic_punctuation"]
            )

            audio = speech.RecognitionAudio(uri=gcs_uri)

            # Perform recognition
            operation = self.speech_client.long_running_recognize(config=config, audio=audio)
            logger.info("Waiting for speech recognition to complete...")
            response = operation.result()

            # Process results
            result = self._process_diarization(response)

            # Clean up
            blob.delete()

            return result

        except Exception as e:
            logger.error(f"Speech-to-text error: {str(e)}")
            # Fall back to mock mode
            return {
                "transcript": "Mock transcription due to error.",
                "segments": [{"speaker": "speaker_1", "text": "Mock transcription due to error."}]
            }

    def _process_diarization(self, response):
        """Process diarization results from speech recognition."""
        result = {
            "transcript": "",
            "segments": []
        }

        # Extract complete transcript
        for res in response.results:
            if not res.alternatives:
                continue
            result["transcript"] += res.alternatives[0].transcript + " "

        # Process speaker diarization if available
        last_result = response.results[-1] if response.results else None
        if last_result and last_result.alternatives:
            words_info = last_result.alternatives[0].words

            current_speaker = None
            current_text = ""

            for word_info in words_info:
                speaker_tag = word_info.speaker_tag
                word = word_info.word

                if current_speaker != speaker_tag:
                    # Add previous segment
                    if current_speaker is not None and current_text:
                        result["segments"].append({
                            "speaker": f"speaker_{current_speaker}",
                            "text": current_text.strip()
                        })

                    # Start new segment
                    current_speaker = speaker_tag
                    current_text = word + " "
                else:
                    current_text += word + " "

            # Add final segment
            if current_text:
                result["segments"].append({
                    "speaker": f"speaker_{current_speaker}",
                    "text": current_text.strip()
                })

        return result


# Initialize voice processing service
voice_processing_service = VoiceProcessingService()