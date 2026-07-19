"""
ARION — Automation Research Intelligence Operation Nexus
v0.1.0 Entry Point

This file is intentionally thin. Its only job is to wire the pipeline
together and run the main loop. Business logic lives in modules/ and tools/.

Pipeline:
    Microphone → Listener → Interpreter → Dispatcher → Tool → Speaker
"""
from __future__ import annotations

import logging
import sys

from core.config import settings
from core.dispatcher import Dispatcher
from modules.interpreter import interpret
from modules.listener import Listener
from modules.speaker import Speaker
from tools.app_tool import AppTool
from tools.browser_tool import BrowserTool
from tools.system_tool import SystemTool

# ---------------------------------------------------------------------------
# Logging setup — change level to DEBUG for verbose output during development
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def build_dispatcher() -> Dispatcher:
    """Register all tools and return a ready-to-use Dispatcher."""
    dispatcher = Dispatcher()
    dispatcher.register(SystemTool())
    dispatcher.register(BrowserTool())
    dispatcher.register(AppTool())
    # Future: dispatcher.register(LLMTool())
    logger.info(f"Registered intents: {dispatcher.registered_intents}")
    return dispatcher


def run() -> None:
    """Main ARION loop — listen, interpret, dispatch, speak, repeat."""
    listener = Listener()
    speaker = Speaker()
    dispatcher = build_dispatcher()

    speaker.speak(
        f"Hello, I am {settings.name} version {settings.version}. "
        "I am ready to assist you."
    )

    # Calibrate microphone once before entering the loop
    listener.calibrate()
    speaker.speak("Microphone calibrated. I'm listening.")

    while True:
        print("\n" + "─" * 50)
        print("Listening... (speak now, or Ctrl+C to quit)")

        text = listener.listen()

        if text is None:
            # Timed out or couldn't understand — keep looping silently
            continue

        print(f"[You] {text}")

        command = interpret(text)
        intent = command.get("intent")

        if intent == "exit":
            speaker.speak("Goodbye. Shutting down ARION.")
            logger.info("Exit command received. Shutting down.")
            sys.exit(0)

        response = dispatcher.dispatch(command)
        speaker.speak(response)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n[ARION] Session ended by user.")
        sys.exit(0)
