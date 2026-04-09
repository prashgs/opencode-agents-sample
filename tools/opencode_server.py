"""
tools/opencode_server.py

Manages the `opencode serve` process as a subprocess.
All prompting goes via HTTP REST API — no CLI subprocess calls per-message.
"""

import os
import time
import signal
import shutil
import subprocess
from pathlib import Path

from tools.opencode_client import OpenCodeClient


class OpenCodeServer:
    def __init__(
        self,
        project_dir: str = ".",
        port: int = 4096,
        hostname: str = "127.0.0.1",
        password: str = None,
        startup_timeout: int = 30,
    ):
        self.project_dir = str(Path(project_dir).resolve())
        self.port = port
        self.hostname = hostname
        self.password = password
        self.startup_timeout = startup_timeout
        self.base_url = f"http://{hostname}:{port}"
        self._process: subprocess.Popen = None
        self.client = OpenCodeClient(self.base_url, password=password)
        self.client.project_dir = self.project_dir

    def start(self) -> "OpenCodeServer":
        if not shutil.which("opencode"):
            raise RuntimeError(
                "OpenCode CLI not found on PATH.\n"
                "Install: npm install -g opencode-ai\n"
                "Or:      curl -fsSL https://opencode.ai/install | bash"
            )

        # Print version for debugging
        try:
            ver = subprocess.check_output(
                ["opencode", "--version"], stderr=subprocess.STDOUT, text=True
            ).strip()
            print(f"  [OpenCodeServer] OpenCode version: {ver}")
        except Exception:
            pass

        if self.client.is_healthy(timeout=2):
            print(f"  [OpenCodeServer] Reusing server at {self.base_url}")
            return self

        env = os.environ.copy()
        if self.password:
            env["OPENCODE_SERVER_PASSWORD"] = self.password

        cmd = [
            "opencode", "serve",
            "--port", str(self.port),
            "--hostname", self.hostname,
        ]

        print(f"  [OpenCodeServer] Starting: {' '.join(cmd)}")
        print(f"  [OpenCodeServer] Working dir: {self.project_dir}")

        self._process = subprocess.Popen(
            cmd,
            cwd=self.project_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if not self.client.wait_until_healthy(timeout=self.startup_timeout):
            stderr_out = b""
            try:
                stderr_out = self._process.stderr.read(3000)
            except Exception:
                pass
            self.stop()
            raise RuntimeError(
                f"OpenCode server did not become healthy within {self.startup_timeout}s.\n"
                f"stderr:\n{stderr_out.decode('utf-8', errors='replace')}"
            )

        print(f"  [OpenCodeServer] ✅ Server ready at {self.base_url}")

        # Print available agents for debugging
        try:
            import requests
            r = requests.get(f"{self.base_url}/config", timeout=5)
            if r.status_code == 200:
                agents = list(r.json().get("agent", {}).keys())
                print(f"  [OpenCodeServer] Agents configured: {agents}")
        except Exception:
            pass

        return self

    def stop(self):
        if self._process and self._process.poll() is None:
            print(f"  [OpenCodeServer] Stopping server (pid {self._process.pid})")
            try:
                self._process.send_signal(signal.SIGTERM)
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    def __enter__(self) -> "OpenCodeServer":
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
