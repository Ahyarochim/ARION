"""
Voice Listener module for ARION.

Handles microphone capture and speech-to-text (STT) conversion using
the SpeechRecognition library with Google's STT backend.

Design note:
  This module is intentionally narrow — it only converts audio → text.
  Intent detection is the Interpreter's responsibility. This separation
  means we can swap the STT backend (Whisper, Vosk, Azure) by changing
  only this file with zero impact on the rest of the pipeline.

v0.1.0 backend: Google Web Speech API (requires internet connection)
Planned v0.3.0: OpenAI Whisper (offline, higher accuracy)
"""
from __future__ import annotations

import logging

import speech_recognition as sr

from core.config import settings

logger = logging.getLogger(__name__)


class Listener:
    """
    Captures microphone audio and returns transcribed text.

    Typical usage:
        listener = Listener()
        listener.calibrate()         # once at startup
        text = listener.listen()     # blocks until speech or timeout
    """

    def __init__(self) -> None:
        self._recognizer = sr.Recognizer()
        self._config = settings.listener
        self._calibrated = False

    def _get_microphone(self) -> sr.Microphone:
        """Return a Microphone instance, respecting config index if set."""
        idx = self._config.microphone_index
        return sr.Microphone(device_index=idx) if idx is not None else sr.Microphone()

    def calibrate(self) -> None:
        """
        Adjust recognizer sensitivity for ambient noise.

        Should be called once at startup before the main loop begins.
        Skipping this causes false positives in noisy environments.
        """
        logger.info("Calibrating microphone for ambient noise...")
        print("[ARION] Calibrating microphone... please wait.")
        with self._get_microphone() as source:
            self._recognizer.adjust_for_ambient_noise(source, duration=1.5)
        self._calibrated = True
        logger.info("Microphone calibrated successfully.")

    def listen(self) -> str | None:
        """
        Listen for a single spoken command and return the transcribed text.

        Returns:
            str: Lowercase transcribed text on success.
            None: On timeout, unrecognized speech, or API error.
        """
        if not self._calibrated:
            logger.debug("Listener not calibrated — auto-calibrating.")
            self.calibrate()

        with self._get_microphone() as source:
            logger.info("Listening for command...")
            try:
                audio = self._recognizer.listen(
                    source,
                    timeout=self._config.timeout,
                    phrase_time_limit=self._config.phrase_limit,
                )
            except sr.WaitTimeoutError:
                logger.debug("Listening timed out — no speech detected.")
                return None

        return self._transcribe(audio)

    def _transcribe(self, audio: sr.AudioData) -> str | None:
        """Send audio to Google STT and return the result."""
        try:
            text = self._recognizer.recognize_google(audio)
            logger.info(f"Transcribed: '{text}'")
            return text.lower().strip()
        except sr.UnknownValueError:
            logger.debug("Could not understand audio.")
            return None
        except sr.RequestError as e:
            logger.error(f"STT API request failed: {e}")
            return None

    @staticmethod
    def list_microphones() -> None:
        """Utility: Print all available microphone names and their indices."""
        print("Available microphones:")
        for idx, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  [{idx}] {name}")
