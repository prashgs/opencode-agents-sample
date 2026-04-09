"""
agents/planner.py
Calls @web-planner subagent. Returns a parsed build plan dict with absolute output paths.
"""
import json
import re
import os
from pathlib import Path
from agents.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    opencode_agent = "web-planner"
    role = "planner"

    def run(self, user_prompt: str) -> dict:
        print(f"\n[PlannerAgent] Delegating to OpenCode @{self.opencode_agent}...")

        # Compute the absolute output root so OpenCode writes to the right place
        project_root = Path(self._project_dir).resolve()
        output_root = project_root / "output"

        prompt = (
            "Analyze this web app description and return a JSON build plan.\n\n"
            f"IMPORTANT: Use this absolute path as the output_dir in your plan:\n"
            f"  {output_root}/<app-name>\n\n"
            f"App description:\n---\n{user_prompt}\n---\n\n"
            "Return ONLY valid JSON — no markdown fences, no explanation, no extra text."
        )
        raw = self.send(prompt)
        return self._parse(raw, output_root, user_prompt)

    def _parse(self, raw: str, output_root: Path, original_prompt: str) -> dict:
        # Strip ANSI, markdown fences, leading noise
        clean = re.sub(r'\x1b\[[0-9;]*[mGKHF]', '', raw)
        clean = re.sub(r"```(?:json)?", "", clean).strip().rstrip("`").strip()

        # Find the first { ... } block
        m = re.search(r"\{.*\}", clean, re.DOTALL)
        if m:
            clean = m.group(0)

        plan = None
        try:
            plan = json.loads(clean)
        except json.JSONDecodeError as e:
            print(f"  [PlannerAgent] JSON parse failed ({e})")
            if raw:
                print(f"  [PlannerAgent] Raw output (first 300 chars): {raw[:300]!r}")

        if not plan:
            # Derive app name from prompt keywords
            words = re.findall(r'\b[a-z]+\b', original_prompt.lower())
            stopwords = {'a','an','the','and','or','with','for','to','in','of','build','create','make'}
            name_words = [w for w in words if w not in stopwords][:3]
            app_name = "-".join(name_words) if name_words else "web-app"

            plan = {
                "app_name": app_name,
                "description": original_prompt[:100],
                "has_backend": False,
                "backend_framework": None,
                "features": [original_prompt[:200]],
                "style_notes": "Clean modern design with good UX",
                "data_storage": "localStorage",
                "frontend_files": ["index.html", "style.css", "app.js"],
                "backend_files": [],
            }

        # Always set output_dir to absolute path
        app_name = plan.get("app_name", "web-app")
        # Sanitise: lowercase, hyphens only
        app_name = re.sub(r'[^a-z0-9-]', '-', app_name.lower()).strip('-')
        app_name = re.sub(r'-+', '-', app_name) or "web-app"
        plan["app_name"] = app_name

        abs_output_dir = str(output_root / app_name)
        plan["output_dir"] = abs_output_dir

        # Ensure file lists exist
        if "frontend_files" not in plan:
            plan["frontend_files"] = ["index.html", "style.css", "app.js"]
        if "backend_files" not in plan:
            plan["backend_files"] = []
        plan["all_files"] = plan["frontend_files"] + plan["backend_files"]

        return plan
