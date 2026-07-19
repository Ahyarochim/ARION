"""
Tests for the Speaker module.

Uses mocking to test speaker behavior without triggering actual audio output.
This keeps CI fast and avoids requiring audio hardware in test environments.
"""
from unittest.mock import MagicMock, patch
import pytest


class TestSpeaker:
    @patch("pyttsx3.init")
    def test_speak_calls_engine(self, mock_init):
        """Speaker.speak() should call pyttsx3's say() and runAndWait()."""
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        mock_engine.getProperty.return_value = []  # no voices

        from modules.speaker import Speaker
        speaker = Speaker()
        speaker.speak("Hello ARION")

        mock_engine.say.assert_called_once_with("Hello ARION")
        mock_engine.runAndWait.assert_called_once()

    @patch("pyttsx3.init")
    def test_speak_prints_to_console(self, mock_init, capsys):
        """Speaker.speak() should print the message to stdout."""
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        mock_engine.getProperty.return_value = []

        from modules.speaker import Speaker
        speaker = Speaker()
        speaker.speak("Test message")

        captured = capsys.readouterr()
        assert "Test message" in captured.out
