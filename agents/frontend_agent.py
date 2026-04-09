"""
agents/frontend_agent.py
Calls @web-app-builder. Passes absolute output_dir so OpenCode writes to the right place.
"""
import json
import os
from pathlib import Path
from agents.base_agent import BaseAgent


class FrontendAgent(BaseAgent):
    opencode_agent = "web-app-builder"
    role = "frontend"

    def run(self, plan: dict, feedback: list = None) -> str:
        print(f"\n[FrontendAgent] Delegating to OpenCode @{self.opencode_agent}...")

        output_dir = plan["output_dir"]   # absolute path
        # Ensure directory exists so OpenCode can write into it
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        feedback_section = ""
        if feedback:
            issues = "\n".join(f"- {i}" for i in feedback)
            feedback_section = f"\n\n## Revision Required\nFix ONLY these issues:\n{issues}"

        # List the exact absolute file paths to write
        file_paths = "\n".join(
            f"  {output_dir}/{f}" for f in plan.get("frontend_files", ["index.html","style.css","app.js"])
        )

        prompt = f"""Build the frontend for this web application.

## Build Plan
```json
{json.dumps(plan, indent=2)}
```

## CRITICAL: File Writing Instructions
Write each file using its EXACT absolute path. Do NOT use relative paths.
Write these files now:
{file_paths}

Use the write tool with the absolute path for each file.
For example, to write index.html use path: {output_dir}/index.html

## Requirements
- Implement ALL features listed in the plan
- Follow the style_notes for design direction
- Use localStorage if data_storage is "localStorage"
- No placeholder content, no TODO comments
- Every button and form must be functional{feedback_section}"""

        response = self.send(prompt)
        print(f"  [FrontendAgent] Done. Expected files in: {output_dir}/")
        return response
