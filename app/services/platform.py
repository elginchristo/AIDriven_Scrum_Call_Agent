# app/services/platform.py
import logging
import asyncio
import json
import os
import tempfile
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from app.config import settings
from app.models.scheduled_call import ScheduledCallModel, PlatformType
from app.services.voice import voice_processing_service

logger = logging.getLogger(__name__)


class MeetingPlatformError(Exception):
    """Exception raised for meeting platform errors."""
    pass


class MeetingSession:
    """Session for interacting with a meeting platform."""

    def __init__(self, driver, meeting_id=None, recording_path=None):
        """Initialize the meeting session."""
        self.driver = driver
        self.meeting_id = meeting_id
        self.recording_path = recording_path
        self.is_recording = False
        self.audio_buffer = b''

    async def speak_text(self, text):
        """Convert text to speech and play in the meeting."""
        try:
            audio_content = await voice_processing_service.text_to_speech(text)

            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_content)
                temp_audio_path = temp_file.name

            # Execute JavaScript to play audio in the meeting
            play_script = f"""
            const audio = new Audio();
            audio.src = "{temp_audio_path}";
            audio.play();
            """
            self.driver.execute_script(play_script)

            # Wait for audio to complete playing
            audio_duration_script = """
            return new Promise((resolve) => {
                const audio = document.querySelector('audio');
                audio.onended = () => resolve(true);
            });
            """
            self.driver.execute_script(audio_duration_script)

            # Clean up temp file
            os.unlink(temp_audio_path)
            logger.info(f"Successfully played text: {text[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Failed to speak text: {str(e)}")
            raise MeetingPlatformError(f"Failed to speak text: {str(e)}")

    async def start_recording(self):
        """Start recording audio in the meeting."""
        try:
            # Execute JavaScript to start recording
            record_script = """
            return new Promise((resolve, reject) => {
                try {
                    const audioChunks = [];

                    navigator.mediaDevices.getUserMedia({ audio: true })
                        .then(stream => {
                            window.mediaRecorder = new MediaRecorder(stream);
                            window.mediaRecorder.start();

                            window.mediaRecorder.addEventListener("dataavailable", event => {
                                audioChunks.push(event.data);
                            });

                            window.mediaRecorder.addEventListener("stop", () => {
                                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                                const reader = new FileReader();
                                reader.readAsDataURL(audioBlob);
                                reader.onloadend = () => {
                                    resolve(reader.result);
                                };
                            });

                            resolve(true);
                        });
                } catch (error) {
                    reject(error);
                }
            });
            """
            result = self.driver.execute_script(record_script)
            self.is_recording = True
            logger.info("Started recording audio")
            return result

        except Exception as e:
            logger.error(f"Failed to start recording: {str(e)}")
            raise MeetingPlatformError(f"Failed to start recording: {str(e)}")

    async def stop_recording(self):
        """Stop recording audio and return the recorded content."""
        if not self.is_recording:
            logger.warning("Attempting to stop recording, but recording was not started")
            return None

        try:
            # Execute JavaScript to stop recording and get audio data
            stop_script = """
            return new Promise((resolve, reject) => {
                try {
                    if (!window.mediaRecorder) {
                        reject("Media recorder not found");
                        return;
                    }

                    const audioChunks = [];

                    window.mediaRecorder.addEventListener("dataavailable", event => {
                        audioChunks.push(event.data);
                    });

                    window.mediaRecorder.addEventListener("stop", () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const reader = new FileReader();
                        reader.readAsDataURL(audioBlob);
                        reader.onloadend = () => {
                            resolve(reader.result);
                        };
                    });

                    window.mediaRecorder.stop();
                } catch (error) {
                    reject(error);
                }
            });
            """
            data_url = self.driver.execute_script(stop_script)

            # Convert data URL to bytes
            audio_content = data_url.split(',')[1]
            import base64
            audio_bytes = base64.b64decode(audio_content)

            self.is_recording = False
            logger.info("Stopped recording audio")
            return audio_bytes

        except Exception as e:
            logger.error(f"Failed to stop recording: {str(e)}")
            raise MeetingPlatformError(f"Failed to stop recording: {str(e)}")

    async def close(self):
        """Close the meeting session."""
        try:
            # Stop recording if active
            if self.is_recording:
                await self.stop_recording()

            # Execute JavaScript to leave meeting (platform-specific)
            leave_script = """
            if (document.querySelector("[aria-label='Leave']")) {
                document.querySelector("[aria-label='Leave']").click();
            } else if (document.querySelector("[aria-label='End meeting']")) {
                document.querySelector("[aria-label='End meeting']").click();
            }
            """
            self.driver.execute_script(leave_script)

            # Close browser
            self.driver.quit()
            logger.info("Closed meeting session")
            return True

        except Exception as e:
            logger.error(f"Failed to close meeting session: {str(e)}")
            try:
                self.driver.quit()
            except:
                pass
            return False


async def connect_to_meeting(scheduled_call: ScheduledCallModel) -> MeetingSession:
    """Connect to a meeting platform.

    Args:
        scheduled_call: Scheduled call information.

    Returns:
        MeetingSession: Session for interacting with the meeting.
    """
    logger.info(f"Connecting to {scheduled_call.platform} meeting...")

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Auto-allow microphone/camera
    chrome_options.add_argument("--use-fake-device-for-media-stream")  # Use fake devices
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1,  # Allow microphone
        "profile.default_content_setting_values.media_stream_camera": 1,  # Allow camera
        "profile.default_content_setting_values.notifications": 1  # Allow notifications
    })

    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)

    # Connect to the platform
    if scheduled_call.platform == PlatformType.ZOOM:
        return await _connect_to_zoom(driver, scheduled_call)
    elif scheduled_call.platform == PlatformType.TEAMS:
        return await _connect_to_teams(driver, scheduled_call)
    elif scheduled_call.platform == PlatformType.MEET:
        return await _connect_to_meet(driver, scheduled_call)
    else:
        driver.quit()
        raise MeetingPlatformError(f"Unsupported platform: {scheduled_call.platform}")


async def _connect_to_zoom(driver, scheduled_call: ScheduledCallModel) -> MeetingSession:
    """Connect to a Zoom meeting.

    Args:
        driver: WebDriver instance.
        scheduled_call: Scheduled call information.

    Returns:
        MeetingSession: Session for interacting with the Zoom meeting.
    """
    try:
        # Navigate to Zoom login page
        driver.get("https://zoom.us/signin")

        # Wait for page to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "email"))
        )

        # Enter credentials
        driver.find_element(By.ID, "email").send_keys(scheduled_call.platform_credentials.username)
        driver.find_element(By.ID, "password").send_keys(scheduled_call.platform_credentials.password)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]").click()

        # Wait for login to complete
        WebDriverWait(driver, 30).until(
            EC.url_contains("zoom.us/")
        )

        # Go to personal meeting room
        driver.get("https://zoom.us/start/videomeeting")

        # Wait for meeting to load
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'join-audio-by-computer')]"))
        )

        # Join with computer audio
        join_audio_button = driver.find_element(By.XPATH, "//button[contains(@class, 'join-audio-by-computer')]")
        join_audio_button.click()

        # Wait for meeting to fully load
        await asyncio.sleep(5)

        # Get meeting ID from URL
        meeting_id = driver.current_url.split("/")[-1]

        logger.info(f"Successfully connected to Zoom meeting with ID: {meeting_id}")
        return MeetingSession(driver, meeting_id)

    except Exception as e:
        logger.error(f"Failed to connect to Zoom meeting: {str(e)}")
        driver.quit()
        raise MeetingPlatformError(f"Failed to connect to Zoom meeting: {str(e)}")
