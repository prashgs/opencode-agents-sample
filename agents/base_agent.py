"""
agents/base_agent.py

Base agent. Uses OpenCodeClient.send_message() which calls
`opencode run --attach <url> --agent <name> "<prompt>"`.

Each subclass sets:
  - opencode_agent: the .opencode/agents/<name>.md agent to invoke
  - role:           label for logging
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.opencode_client import OpenCodeClient


class BaseAgent:
    opencode_agent: str = "build"
    role: str = "base"

    def __init__(self, client: OpenCodeClient, session_id: str):
        self.client = client
        self.session_id = session_id
        # Project dir used so opencode run resolves relative paths correctly
        self._project_dir = getattr(client, "project_dir", ".")

    def send(self, prompt: str) -> str:
        """Send a prompt to this agent via `opencode run --attach`. Returns response."""
        print(f"  [{self.__class__.__name__}] → agent: {self.opencode_agent}")
        response = self.client.send_message(
            session_id=self.session_id,
            text=prompt,
            agent=self.opencode_agent,
        )
        return response

    def run(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement run()")
