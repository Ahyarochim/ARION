"""
Browser Tool for ARION.

Handles all browser-related actions:
  - Opening Chrome (or default browser)
  - Performing Google searches
  - Opening YouTube

Uses Python's built-in webbrowser module as the primary mechanism —
no external dependencies needed for v0.1.0. Chrome path auto-detection
is a fallback for when the user wants explicit Chrome control.
"""
from __future__ import annotations

import logging
import os
import webbrowser
from urllib.parse import quote_plus

from core.config import settings
from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

# Common Chrome installation paths on Windows, tried in order
_CHROME_CANDIDATE_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]


def _find_chrome() -> str | None:
    """Auto-detect Chrome executable. Returns path or None if not found."""
    # Check config override first
    configured = settings.browser.chrome_path
    if configured and os.path.exists(configured):
        return configured

    for path in _CHROME_CANDIDATE_PATHS:
        if os.path.exists(path):
            logger.debug(f"Chrome found at: {path}")
            return path

    logger.warning("Chrome not found. Falling back to default system browser.")
    return None


class BrowserTool(BaseTool):
    """Opens the browser and performs web searches."""

    @property
    def name(self) -> str:
        return "BrowserTool"

    @property
    def description(self) -> str:
        return (
            "Opens Chrome or the default browser. "
            "Performs Google searches. Opens YouTube."
        )

    def get_handlers(self) -> dict:
        return {
            "open_browser": self._open_browser,
            "search_google": self._search_google,
            "open_youtube": self._open_youtube,
        }

    # --- Handlers ---

    def _open_browser(self) -> str:
        """Open Chrome or the default browser."""
        chrome = _find_chrome()
        if chrome:
            webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome))
            webbrowser.get("chrome").open("https://www.google.com")
        else:
            webbrowser.open("https://www.google.com")
        return "Opening browser."

    def _search_google(self, query: str = "") -> str:
        """Perform a Google search for the given query."""
        if not query:
            return "What would you like me to search for?"

        search_url = settings.browser.search_url.format(query=quote_plus(query))
        webbrowser.open(search_url)
        logger.info(f"Searching Google: '{query}'")
        return f"Searching Google for: {query}"

    def _open_youtube(self) -> str:
        """Navigate to YouTube."""
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."
