"""
tools/ollama_client.py
Unified Ollama API wrapper used by all agents.
"""

import requests
import json
import time
from typing import Optional


class OllamaClient:
    def __init__(self, base_url: str, model: str, generation_params: dict = None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.generation_params = generation_params or {}

    def chat(self, system: str, user: str, retries: int = 3) -> str:
        """Send a chat request and return the assistant response text."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {
                "temperature": self.generation_params.get("temperature", 0.3),
                "num_predict": self.generation_params.get("num_predict", 2048),
            },
        }

        for attempt in range(retries):
            try:
                resp = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=300,
                )
                resp.raise_for_status()
                return resp.json()["message"]["content"]
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    print(f"  [OllamaClient] Retry {attempt + 1}/{retries} after error: {e}")
                    time.sleep(2)
                else:
                    raise RuntimeError(
                        f"Ollama request failed after {retries} attempts: {e}\n"
                        "Is Ollama running? Try: ollama serve"
                    )

    def is_available(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """Return list of locally available model names."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            return []
