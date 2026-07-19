"""
Configuration loader for ARION.

Reads config.yaml from the project root and exposes a typed settings
object. Every module imports from here — never hardcode values.

Design note: Using dataclasses instead of a raw dict gives us
autocomplete, type hints, and a clear schema. Adding a new setting
requires only adding a field here and a key in config.yaml.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

# Resolve config.yaml relative to the project root (two levels up from this file)
_PROJECT_ROOT = Path(__file__).parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "config.yaml"


@dataclass
class ListenerConfig:
    microphone_index: Optional[int] = None
    timeout: int = 5
    phrase_limit: int = 10


@dataclass
class SpeakerConfig:
    engine: str = "pyttsx3"
    rate: int = 170
    volume: float = 1.0
    voice_index: int = 0


@dataclass
class BrowserConfig:
    chrome_path: Optional[str] = None
    search_url: str = "https://www.google.com/search?q={query}"


@dataclass
class ArionConfig:
    name: str = "ARION"
    version: str = "0.1.0"
    listener: ListenerConfig = field(default_factory=ListenerConfig)
    speaker: SpeakerConfig = field(default_factory=SpeakerConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    apps: dict = field(default_factory=dict)


def load_config(path: Path = _CONFIG_PATH) -> ArionConfig:
    """
    Load and parse config.yaml into an ArionConfig object.

    Falls back to defaults gracefully if config.yaml is missing,
    so the project can still run during testing.
    """
    if not path.exists():
        logger.warning(f"config.yaml not found at '{path}'. Using defaults.")
        return ArionConfig()

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    arion_raw = raw.get("arion", {})
    listener_raw = raw.get("listener", {})
    speaker_raw = raw.get("speaker", {})
    browser_raw = raw.get("browser", {})
    apps_raw = raw.get("apps", {})

    return ArionConfig(
        name=arion_raw.get("name", "ARION"),
        version=arion_raw.get("version", "0.1.0"),
        listener=ListenerConfig(**{k: v for k, v in listener_raw.items() if v is not None or k == "microphone_index"}),
        speaker=SpeakerConfig(**speaker_raw),
        browser=BrowserConfig(**{k: v for k, v in browser_raw.items()}),
        apps={k: v for k, v in apps_raw.items()},
    )


# Module-level singleton — import `settings` everywhere instead of calling load_config().
# This ensures config is parsed once at startup, not on every import.
settings = load_config()
