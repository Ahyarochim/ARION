"""
Speaker (Text-to-Speech) module for ARION.

Wraps pyttsx3 for offline TTS output. Voice, rate, and volume are
configured via config.yaml so the user never needs to touch this file.

Design note:
  pyttsx3's runAndWait() is synchronous — speak() blocks until audio
  finishes. This is acceptable for v0.1.0 (one action at a time).
  For v0.3.0 (streaming LLM responses), this should be refactored into
  a separate thread with a queue.Queue() for non-blocking playback.
"""
from __future__ import annotations

import logging

import pyttsx3

from core.config import settings

logger = logging.getLogger(__name__)


class Speaker:
    """
    Converts text to speech using the pyttsx3 offline TTS engine.

    Typical usage:
        speaker = Speaker()
        speaker.speak("Hello, I am ARION.")
    """

    def __init__(self) -> None:
        self._engine = pyttsx3.init()
        self._apply_settings()

    def _apply_settings(self) -> None:
        """Apply voice configuration from config.yaml."""
        cfg = settings.speaker
        self._engine.setProperty("rate", cfg.rate)
        self._engine.setProperty("volume", cfg.volume)

        voices = self._engine.getProperty("voices")
        if voices:
            idx = min(cfg.voice_index, len(voices) - 1)
            self._engine.setProperty("voice", voices[idx].id)
            logger.debug(f"Using voice: {voices[idx].name}")
        else:
            logger.warning("No TTS voices found on this system.")

    def speak(self, text: str) -> None:
        """
        Speak the given text aloud and print it to the console.

        Args:
            text: The message for ARION to speak.
        """
        logger.info(f"Speaking: '{text}'")
        print(f"\n[ARION] {text}\n")
        self._engine.say(text)
        self._engine.runAndWait()

    def list_voices(self) -> None:
        """Utility: Print all available TTS voices and their indices."""
        voices = self._engine.getProperty("voices")
        print("Available TTS voices:")
        for idx, voice in enumerate(voices or []):
            print(f"  [{idx}] {voice.name}  (id: {voice.id})")
