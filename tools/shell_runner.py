"""
tools/shell_runner.py
Runs shell commands and optionally invokes OpenCode CLI.
"""

import subprocess
import shutil
from pathlib import Path


def run_command(cmd: list[str], cwd: str = None, timeout: int = 120) -> tuple[str, str, int]:
    """
    Run a shell command. Returns (stdout, stderr, returncode).
    """
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout, result.stderr, result.returncode


def run_opencode(instruction: str, working_dir: str) -> tuple[str, str, int]:
    """
    Invoke the OpenCode CLI with a text instruction in a working directory.
    OpenCode is expected to be on PATH.

    Returns (stdout, stderr, returncode).
    """
    if not shutil.which("opencode"):
        raise RuntimeError(
            "OpenCode CLI not found on PATH. "
            "Install it with: npm install -g opencode-ai"
        )

    Path(working_dir).mkdir(parents=True, exist_ok=True)
    return run_command(
        ["opencode", "run", instruction],
        cwd=working_dir,
    )


def opencode_available() -> bool:
    return shutil.which("opencode") is not None
