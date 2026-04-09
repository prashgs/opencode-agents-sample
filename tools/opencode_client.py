"""
tools/opencode_client.py

Correct API shapes for OpenCode 1.4.0 (confirmed by probe):
  POST /session/:id/message  body: { "parts": [{"type":"text","text":"..."}], "agent":"..." }
  GET  /session/:id/message  returns list of messages with parts
  GET  /global/event         SSE stream for global events (session/:id/event returns HTML)

Strategy:
  1. POST message with parts array
  2. Poll GET /session/:id/message until we see a new completed assistant message
     (SSE stream at /session/:id/event returns web UI HTML, not events)
"""

import json
import re
import time
import requests


class OpenCodeClient:
    def __init__(self, base_url: str = "http://localhost:4096", password: str = None):
        self.base_url = base_url.rstrip("/")
        self.auth = ("opencode", password) if password else None
        self.project_dir = "."

    # ── Health ────────────────────────────────────────────────────

    def is_healthy(self, timeout: int = 5) -> bool:
        try:
            r = requests.get(f"{self.base_url}/global/health", timeout=timeout, auth=self.auth)
            return r.status_code == 200 and r.json().get("healthy", False)
        except Exception:
            return False

    def wait_until_healthy(self, timeout: int = 30) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.is_healthy():
                return True
            time.sleep(1)
        return False

    # ── Sessions ──────────────────────────────────────────────────

    def create_session(self, title: str = None) -> dict:
        payload = {"title": title} if title else {}
        r = requests.post(f"{self.base_url}/session", json=payload, auth=self.auth, timeout=30)
        r.raise_for_status()
        return r.json()

    def list_messages(self, session_id: str) -> list:
        r = requests.get(
            f"{self.base_url}/session/{session_id}/message",
            auth=self.auth, timeout=15
        )
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []

    # ── Send message ──────────────────────────────────────────────

    def send_message(
        self,
        session_id: str,
        text: str,
        agent: str = None,
        timeout: int = 600,
    ) -> str:
        """
        POST /session/:id/message with correct parts-array body (OpenCode 1.4.0).
        Then poll GET /session/:id/message until we get a completed assistant reply.
        """
        # Count current messages so we know what's "new"
        try:
            before = self.list_messages(session_id)
            msg_count_before = len([m for m in before if m.get("role") == "assistant"])
        except Exception:
            msg_count_before = 0

        # POST the message — correct shape: { parts: [{type,text}], agent? }
        payload: dict = {
            "parts": [{"type": "text", "text": text}]
        }
        if agent:
            payload["agent"] = agent

        url = f"{self.base_url}/session/{session_id}/message"
        r = requests.post(url, json=payload, auth=self.auth, timeout=30)

        if not r.ok:
            raise RuntimeError(
                f"POST /session/:id/message failed: {r.status_code}\n"
                f"body sent: {json.dumps(payload)[:200]}\n"
                f"response:  {r.text[:400]}"
            )

        # Poll for completed assistant response
        return self._poll(session_id, msg_count_before, timeout)

    def _poll(self, session_id: str, count_before: int, timeout: int = 600) -> str:
        """
        Poll GET /session/:id/message every 4s.
        Return text when we see a new assistant message that looks complete.
        """
        deadline = time.time() + timeout
        last_text = ""
        stable_count = 0  # how many polls in a row with the same text

        print(f"  [OpenCodeClient] Waiting for response", end="", flush=True)

        while time.time() < deadline:
            time.sleep(4)
            print(".", end="", flush=True)

            try:
                msgs = self.list_messages(session_id)
            except Exception:
                continue

            assistant_msgs = [m for m in msgs if m.get("role") == "assistant"]

            # We need more assistant messages than before
            if len(assistant_msgs) <= count_before:
                continue

            # Get the latest one
            latest = assistant_msgs[-1]
            parts = latest.get("parts", [])

            # Extract all text parts
            text_parts = [
                p.get("text", "") for p in parts
                if isinstance(p, dict) and p.get("type") == "text"
            ]
            current_text = "\n".join(t for t in text_parts if t).strip()

            # Check completion status
            info = latest.get("info", {})
            if not isinstance(info, dict):
                info = {}
            status = info.get("status", "")

            # Also check if any tool parts are still running
            tool_parts = [p for p in parts if isinstance(p, dict) and p.get("type") == "tool"]
            running_tools = [
                p for p in tool_parts
                if p.get("state", {}).get("status", "") not in ("completed", "error", "")
            ]

            is_complete = (
                status in ("completed", "done", "complete") or
                (status == "" and current_text and not running_tools)
            )

            if current_text == last_text and current_text:
                stable_count += 1
            else:
                stable_count = 0
                last_text = current_text

            # Consider done if: explicitly completed, OR text stable for 2 polls with no running tools
            if is_complete or (stable_count >= 2 and not running_tools):
                print()  # newline after dots
                return self._clean(current_text)

        print()  # newline after dots
        return self._clean(last_text)

    def _clean(self, text: str) -> str:
        text = re.sub(r'\x1b\[[0-9;]*[mGKHFABCDJK]', '', text)
        return text.strip()
