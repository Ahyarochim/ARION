"""
Abstract Base Tool for ARION.

All tools must inherit from BaseTool and implement get_handlers().

Design philosophy:
  - Tools are self-describing (name, description) for future LLM tool-selection.
  - Tools register their intent handlers via get_handlers() rather than
    inheriting a single execute() method — this allows one tool class to
    handle multiple related intents cleanly.
  - Each handler is a plain function: (kwargs) -> str (response message).

Future v0.2.0+ additions to this base:
  - parameter_schema: dict  (JSON Schema, for LLM function-calling)
  - requires_confirmation: bool
  - async_execute() for non-blocking operations
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable


class BaseTool(ABC):
    """Abstract base class for all ARION tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable tool name (e.g. 'BrowserTool')."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """
        What this tool does.
        Written in plain English — this will be used for LLM tool-selection
        in future versions (similar to OpenAI function descriptions).
        """
        ...

    @abstractmethod
    def get_handlers(self) -> dict[str, Callable]:
        """
        Return a mapping of intent name → handler callable.

        Each handler receives **params (keyword args extracted by the
        Interpreter) and returns a response string.

        Example:
            {
                "open_browser": self._open_browser,
                "search_google": self._search_google,
            }
        """
        ...
