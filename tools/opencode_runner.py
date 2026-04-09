"""
tools/opencode_runner.py

Drives OpenCode via `opencode run` CLI command.
Used when you want single-shot, non-interactive execution
without managing a persistent server.

This is the simpler alternative to OpenCodeClient (HTTP server).
The orchestrator uses this for individual agent steps.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path


class OpenCodeRunner:
    """
    Executes `opencode run` commands in a given working directory.
    Optionally attaches to a running opencode server to avoid cold-start overhead.

    Each call to run() is one complete agent turn:
        opencode run --agent <agent> "<prompt>"
    """

    def __init__(
        self,
        project_dir: str = ".",
        attach_url: str = None,
        timeout: int = 300,
    ):
        self.project_dir = str(Path(project_dir).resolve())
        self.attach_url = attach_url  # e.g. "http://localhost:4096"
        self.timeout = timeout

    def is_available(self) -> bool:
        return shutil.which("opencode") is not None

    def run(
        self,
        prompt: str,
        agent: str = None,
        model: str = None,
        session_id: str = None,
        continue_session: bool = False,
    ) -> tuple[str, int]:
        """
        Run a single opencode prompt.

        Returns (stdout_text, returncode).
        """
        if not self.is_available():
            raise RuntimeError(
                "OpenCode CLI not found on PATH.\n"
                "Install: npm install -g opencode-ai\n"
                "Or: curl -fsSL https://opencode.ai/install | bash"
            )

        cmd = ["opencode", "run"]

        if agent:
            cmd += ["--agent", agent]
        if model:
            cmd += ["--model", model]
        if session_id:
            cmd += ["--session", session_id]
        if continue_session:
            cmd += ["--continue"]
        if self.attach_url:
            cmd += ["--attach", self.attach_url]

        # Prompt goes last as positional args
        cmd += [prompt]

        result = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )

        output = result.stdout.strip()
        if result.returncode != 0 and result.stderr:
            error_preview = result.stderr[:500]
            print(f"  [OpenCodeRunner] stderr: {error_preview}")

        return output, result.returncode

    def run_and_parse_json(
        self,
        prompt: str,
        agent: str = None,
        model: str = None,
    ) -> dict | None:
        """
        Run a prompt and attempt to parse JSON from the output.
        Returns the parsed dict, or None on failure.
        """
        output, rc = self.run(prompt, agent=agent, model=model)
        if not output:
            return None
        return _extract_json(output)


def _extract_json(text: str) -> dict | None:
    """Try to extract and parse the first JSON object from text."""
    # Strip markdown fences
    clean = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()

    # Find outermost { ... }
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


# ── Module-level convenience functions ────────────────────────────────────────

def run_prompt(
    prompt: str,
    project_dir: str = ".",
    agent: str = None,
    model: str = None,
    attach_url: str = None,
    timeout: int = 300,
) -> str:
    """Run a single prompt via `opencode run`. Returns stdout."""
    if not shutil.which("opencode"):
        raise RuntimeError(
            "OpenCode CLI not found.\n"
            "Install: npm install -g opencode-ai\n"
            "Or: curl -fsSL https://opencode.ai/install | bash"
        )
    cmd = ["opencode", "run"]
    if attach_url:
        cmd += ["--attach", attach_url]
    if agent:
        cmd += ["--agent", agent]
    if model:
        cmd += ["--model", model]
    cmd.append(prompt)
    result = subprocess.run(
        cmd,
        cwd=str(Path(project_dir).resolve()),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"opencode run failed (exit {result.returncode}):\n{result.stderr[:800]}"
        )
    return result.stdout.strip()


def extract_json(text: str) -> dict | None:
    """Extract the first JSON object from a string."""
    clean = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    m = re.search(r"\{.*\}", clean, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return None


def opencode_available() -> bool:
    """Return True if opencode CLI is on PATH."""
    return shutil.which("opencode") is not None
