"""
Command Interpreter for ARION v0.1.0.

Converts raw transcribed text into a structured command dict that the
Dispatcher can route to the correct tool.

v0.1.0 approach: Pattern-based matching using regex.
  - No external dependencies
  - Instant execution
  - Easy to extend (just add a row to _INTENT_PATTERNS)
  - Predictable and debuggable

Future v0.2.0 upgrade path:
  This module is the only thing that changes when adding LLM-based
  intent detection. The output schema is fixed — the rest of the
  pipeline (Dispatcher, Tools) requires zero modifications.

Output schema:
    {
        "intent": str,    # e.g. "search_google", "open_app", "get_time"
        "params": dict,   # e.g. {"query": "python tutorial"}
    }
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper extractors — called when a pattern matches to pull out parameters
# ---------------------------------------------------------------------------

def _after(trigger_pattern: str, text: str) -> str:
    """Extract text following a trigger keyword pattern."""
    match = re.search(rf"(?:{trigger_pattern})\s+(.+)", text)
    return match.group(1).strip() if match else ""


def _extract_app_name(text: str) -> str:
    """Extract the app name from 'open <app>' commands."""
    match = re.search(r"\bopen\s+(\w+)", text)
    return match.group(1).strip() if match else ""


# ---------------------------------------------------------------------------
# Intent pattern table
#
# Format: (regex_pattern, intent_name, param_extractor_fn)
# Order matters — more specific patterns must come before general ones.
# ---------------------------------------------------------------------------

_INTENT_PATTERNS: list[tuple[str, str, callable]] = [
    # --- Exit ---
    (
        r"\b(exit|quit|shutdown|stop|bye|goodbye)\b",
        "exit",
        lambda t: {},
    ),

    # --- Time & Date ---
    (
        r"\b(what(?:'?s| is) the time|current time|time (right )?now|what time)\b",
        "get_time",
        lambda t: {},
    ),
    (
        r"\b(what(?:'?s| is) (the )?date|today(?:'?s)? date|current date)\b",
        "get_date",
        lambda t: {},
    ),

    # --- YouTube (must be before generic 'open browser' to catch it first) ---
    (
        r"\b(open |go to |launch |play )?youtube\b",
        "open_youtube",
        lambda t: {},
    ),

    # --- Google Search ---
    (
        r"\b(search|google|look up|find|search for)\b",
        "search_google",
        lambda t: {"query": _after(r"search(?: for)?|google|look up|find", t)},
    ),

    # --- Open Browser / Chrome ---
    (
        r"\b(open (browser|chrome|internet)|launch (browser|chrome))\b",
        "open_browser",
        lambda t: {},
    ),

    # --- Open Desktop Application ---
    # This is intentionally last among 'open' patterns — YouTube and browser
    # are caught above before this general case runs.
    (
        r"\bopen\s+\w+\b",
        "open_app",
        lambda t: {"app": _extract_app_name(t)},
    ),
]


def interpret(text: str) -> dict:
    """
    Parse raw transcribed text and return a structured command dict.

    Args:
        text: Lowercased voice input string.

    Returns:
        dict with 'intent' and 'params'.
        Falls back to 'unknown' intent if nothing matches.
    """
    text = text.lower().strip()
    logger.debug(f"Interpreting: '{text}'")

    for pattern, intent, extractor in _INTENT_PATTERNS:
        if re.search(pattern, text):
            params = extractor(text)
            logger.info(f"Intent '{intent}' matched | params: {params}")
            return {"intent": intent, "params": params}

    logger.info(f"No intent matched for: '{text}'")
    return {"intent": "unknown", "params": {"raw": text}}
