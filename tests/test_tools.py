"""
Tests for the Tool layer.

Tests tool handlers in isolation. Browser and App tools are tested
with mocked system calls to avoid side effects (opening real browsers).
"""
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytest

from tools.system_tool import SystemTool
from tools.browser_tool import BrowserTool
from tools.app_tool import AppTool
from core.dispatcher import Dispatcher


# ---------------------------------------------------------------------------
# SystemTool tests
# ---------------------------------------------------------------------------

class TestSystemTool:
    def setup_method(self):
        self.tool = SystemTool()

    def test_get_time_returns_string(self):
        result = self.tool.get_handlers()["get_time"]()
        assert isinstance(result, str)
        assert "time" in result.lower()

    def test_get_date_returns_string(self):
        result = self.tool.get_handlers()["get_date"]()
        assert isinstance(result, str)
        assert str(datetime.now().year) in result

    def test_registers_correct_intents(self):
        handlers = self.tool.get_handlers()
        assert "get_time" in handlers
        assert "get_date" in handlers


# ---------------------------------------------------------------------------
# BrowserTool tests
# ---------------------------------------------------------------------------

class TestBrowserTool:
    def setup_method(self):
        self.tool = BrowserTool()

    @patch("webbrowser.open")
    def test_open_youtube(self, mock_open):
        result = self.tool.get_handlers()["open_youtube"]()
        mock_open.assert_called_once_with("https://www.youtube.com")
        assert "youtube" in result.lower()

    @patch("webbrowser.open")
    def test_search_google(self, mock_open):
        result = self.tool.get_handlers()["search_google"](query="python tutorial")
        assert mock_open.called
        assert "python tutorial" in result.lower()

    def test_search_google_empty_query(self):
        result = self.tool.get_handlers()["search_google"](query="")
        assert "what" in result.lower()  # should ask for query

    def test_registers_correct_intents(self):
        handlers = self.tool.get_handlers()
        assert "open_browser" in handlers
        assert "search_google" in handlers
        assert "open_youtube" in handlers


# ---------------------------------------------------------------------------
# Dispatcher integration tests
# ---------------------------------------------------------------------------

class TestDispatcher:
    def setup_method(self):
        self.dispatcher = Dispatcher()
        self.dispatcher.register(SystemTool())
        self.dispatcher.register(BrowserTool())

    def test_dispatch_get_time(self):
        result = self.dispatcher.dispatch({"intent": "get_time", "params": {}})
        assert "time" in result.lower()

    def test_dispatch_unknown_intent(self):
        result = self.dispatcher.dispatch({"intent": "fly_to_moon", "params": {}})
        assert result  # should return a non-empty fallback string

    def test_registered_intents_list(self):
        intents = self.dispatcher.registered_intents
        assert "get_time" in intents
        assert "get_date" in intents
        assert "open_browser" in intents
