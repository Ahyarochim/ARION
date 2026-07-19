"""
App Launcher Tool for ARION.

Handles opening desktop applications by spoken name.

Design note:
  App names from the Interpreter (e.g. "notepad", "vscode") are
  looked up in config.yaml's 'apps' section. This avoids hardcoding
  paths — users can extend the app list without touching code.

  Windows-only for v0.1.0. Cross-platform support (macOS/Linux) can
  be added in v0.2.0 by detecting os.name and branching paths.
"""
from __future__ import annotations

import logging
import subprocess

from core.config import settings
from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

# Apps that are known by Windows 'start' and don't need explicit paths
_WINDOWS_ALIASES = {"notepad", "calculator", "calc", "paint", "mspaint"}


class AppTool(BaseTool):
    """Opens desktop applications by name."""

    @property
    def name(self) -> str:
        return "AppTool"

    @property
    def description(self) -> str:
        return "Launches desktop applications such as Notepad, Calculator, VS Code, etc."

    def get_handlers(self) -> dict:
        return {
            "open_app": self._open_app,
        }

    def _open_app(self, app: str = "") -> str:
        """
        Open a desktop application by name.

        Lookup order:
          1. config.yaml 'apps' section
          2. Windows built-in alias (notepad, calc, mspaint)
          3. Try the name directly as a command

        Args:
            app: App name as spoken (e.g. "notepad", "vscode", "calculator")
        """
        if not app:
            return "Which application would you like me to open?"

        app = app.lower().strip()

        # Normalize common spoken variations
        _aliases = {
            "calculator": "calc",
            "paint": "mspaint",
            "word": "winword",
            "excel": "excel",
        }
        app = _aliases.get(app, app)

        # Check config.yaml for an explicit path
        executable = settings.apps.get(app)

        if executable is None:
            # Fall back to trying the app name directly
            executable = app

        logger.info(f"Launching app: '{executable}'")

        try:
            # Use 'start' on Windows for apps without full paths
            subprocess.Popen(
                ["start", "", executable],
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return f"Opening {app}."
        except Exception as e:
            logger.error(f"Failed to open '{executable}': {e}")
            return f"I couldn't open {app}. Please check the app path in config.yaml."
