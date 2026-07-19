"""
Tests for the Command Interpreter.

Tests the pattern-matching logic without needing a microphone or TTS.
This is the most important test file — the Interpreter is the only
component that can silently break in unexpected ways.
"""
import pytest
from modules.interpreter import interpret


class TestInterpretExit:
    def test_exit_keyword(self):
        result = interpret("exit")
        assert result["intent"] == "exit"

    def test_quit_keyword(self):
        result = interpret("quit now")
        assert result["intent"] == "exit"

    def test_goodbye(self):
        result = interpret("goodbye arion")
        assert result["intent"] == "exit"


class TestInterpretTime:
    def test_what_time(self):
        result = interpret("what time is it")
        assert result["intent"] == "get_time"

    def test_current_time(self):
        result = interpret("current time")
        assert result["intent"] == "get_time"


class TestInterpretDate:
    def test_what_is_the_date(self):
        result = interpret("what is the date today")
        assert result["intent"] == "get_date"

    def test_todays_date(self):
        result = interpret("today's date")
        assert result["intent"] == "get_date"


class TestInterpretBrowser:
    def test_open_chrome(self):
        result = interpret("open chrome")
        assert result["intent"] == "open_browser"

    def test_open_browser(self):
        result = interpret("open browser")
        assert result["intent"] == "open_browser"

    def test_open_youtube(self):
        result = interpret("open youtube")
        assert result["intent"] == "open_youtube"

    def test_youtube_alone(self):
        result = interpret("youtube")
        assert result["intent"] == "open_youtube"


class TestInterpretSearch:
    def test_search_google(self):
        result = interpret("search python tutorial")
        assert result["intent"] == "search_google"
        assert "python tutorial" in result["params"]["query"]

    def test_google_keyword(self):
        result = interpret("google machine learning")
        assert result["intent"] == "search_google"

    def test_look_up(self):
        result = interpret("look up how to use pandas")
        assert result["intent"] == "search_google"

    def test_empty_search_query(self):
        result = interpret("search")
        assert result["intent"] == "search_google"


class TestInterpretApp:
    def test_open_notepad(self):
        result = interpret("open notepad")
        assert result["intent"] == "open_app"
        assert result["params"]["app"] == "notepad"

    def test_open_calculator(self):
        result = interpret("open calculator")
        assert result["intent"] == "open_app"
        assert result["params"]["app"] == "calculator"


class TestInterpretUnknown:
    def test_unknown_input(self):
        result = interpret("the quick brown fox")
        assert result["intent"] == "unknown"
        assert "raw" in result["params"]

    def test_empty_string(self):
        result = interpret("")
        assert result["intent"] == "unknown"
