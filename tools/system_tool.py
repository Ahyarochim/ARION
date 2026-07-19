"""
System Tool for ARION.

Handles general system information queries: time, date, and other
lightweight OS-level commands that don't belong in a domain-specific tool.

This tool intentionally stays simple — it's a catch-all for things
ARION knows without needing to call external services or APIs.
"""
from __future__ import annotations

import logging
import platform
from datetime import datetime

from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class SystemTool(BaseTool):
    """Provides system information: time, date, and OS info."""

    @property
    def name(self) -> str:
        return "SystemTool"

    @property
    def description(self) -> str:
        return "Returns system information such as the current time, date, and OS details."

    def get_handlers(self) -> dict:
        return {
            "get_time": self._get_time,
            "get_date": self._get_date,
        }

    def _get_time(self) -> str:
        """Return the current local time as a spoken string."""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")      # e.g. "09:45 AM"
        logger.info(f"Reporting time: {time_str}")
        return f"The current time is {time_str}."

    def _get_date(self) -> str:
        """Return today's date as a spoken string."""
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")  # e.g. "Saturday, July 19, 2026"
        logger.info(f"Reporting date: {date_str}")
        return f"Today is {date_str}."
