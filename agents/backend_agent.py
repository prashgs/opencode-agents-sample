"""
agents/backend_agent.py
Calls @web-app-builder for Python backend. Uses absolute paths.
"""
import json
from pathlib import Path
from agents.base_agent import BaseAgent


class BackendAgent(BaseAgent):
    opencode_agent = "web-app-builder"
    role = "backend"

    def run(self, plan: dict, feedback: list = None) -> str:
        print(f"\n[BackendAgent] Delegating to OpenCode @{self.opencode_agent}...")

        output_dir = plan["output_dir"]
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        feedback_section = ""
        if feedback:
            issues = "\n".join(f"- {i}" for i in feedback)
            feedback_section = f"\n\n## Revision Required\nFix ONLY these issues:\n{issues}"

        backend_files = plan.get("backend_files", ["app.py","models.py","database.py","requirements.txt","run.sh"])
        file_paths = "\n".join(f"  {output_dir}/{f}" for f in backend_files)

        prompt = f"""Build the Python backend for this web application.

## Build Plan
```json
{json.dumps(plan, indent=2)}
```

## CRITICAL: File Writing Instructions
Write each file using its EXACT absolute path:
{file_paths}

Framework: {plan.get('backend_framework') or 'FastAPI'}
- Enable CORS for all origins
- Use SQLite at {output_dir}/data/app.db
- Include run.sh: uvicorn app:app --reload --port 8000
- No placeholder content, no TODO comments{feedback_section}"""

        response = self.send(prompt)
        print(f"  [BackendAgent] Done. Expected files in: {output_dir}/")
        return response
