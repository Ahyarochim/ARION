"""
Command Dispatcher for ARION.

Receives a structured command dict from the Interpreter and routes it
to the correct tool handler. This is the central hub of the pipeline.

Architecture note:
  Tools register themselves with the dispatcher via register().
  The dispatcher stores a flat map of {intent: handler_fn}.
  Dispatching an intent is an O(1) dict lookup — no if-else chains.

This design scales cleanly:
  - v0.1.0: keyword-based Interpreter → Dispatcher
  - v0.2.0: LLM classifies intent → same Dispatcher (zero changes here)
  - v0.3.0: Planner decomposes multi-step goals → Dispatcher handles each step
"""
from __future__ import annotations

import logging
from typing import Callable

from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class Dispatcher:
    """
    Routes parsed commands to registered tool handlers.

    Usage:
        dispatcher = Dispatcher()
        dispatcher.register(BrowserTool())
        dispatcher.register(SystemTool())

        response = dispatcher.dispatch({"intent": "get_time", "params": {}})
    """

    def __init__(self) -> None:
        # Maps intent_name → handler callable
        self._handlers: dict[str, Callable] = {}

    def register(self, tool: BaseTool) -> None:
        """Register all handlers from a tool into the intent map."""
        for intent, handler in tool.get_handlers().items():
            if intent in self._handlers:
                logger.warning(
                    f"Intent '{intent}' is already registered. "
                    f"Overwriting with '{tool.name}'."
                )
            self._handlers[intent] = handler
            logger.debug(f"Registered intent '{intent}' → {tool.name}")

    def dispatch(self, command: dict) -> str:
        """
        Look up the handler for the command's intent and invoke it.

        Args:
            command: dict with keys:
                - 'intent' (str): the classified intent name
                - 'params' (dict): kwargs passed to the handler

        Returns:
            str: Human-readable response to be spoken back to the user.
                 Returns a fallback message if no handler is found.
        """
        intent: str = command.get("intent", "unknown")
        params: dict = command.get("params", {})

        handler = self._handlers.get(intent)

        if handler is None:
            logger.warning(f"No handler registered for intent: '{intent}'")
            return "I'm not sure how to help with that. Could you rephrase?"

        logger.info(f"Dispatching intent '{intent}' with params: {params}")

        try:
            return handler(**params)
        except Exception as e:
            logger.exception(f"Error executing handler for intent '{intent}': {e}")
            return f"Something went wrong while handling '{intent}'."

    @property
    def registered_intents(self) -> list[str]:
        """Return a list of all registered intent names (useful for debugging)."""
        return list(self._handlers.keys())
