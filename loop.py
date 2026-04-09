"""
loop.py
Thin wrapper around Orchestrator. Loads config and runs the pipeline.
"""
import yaml
from pathlib import Path
from agents.orchestrator import Orchestrator


def load_config(config_path: str = "config.yaml") -> dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(path) as f:
        return yaml.safe_load(f)


def run(user_prompt: str, config: dict = None, config_path: str = "config.yaml") -> dict:
    """Run the full pipeline. Returns summary dict."""
    if config is None:
        config = load_config(config_path)
    return Orchestrator(config).run(user_prompt)
