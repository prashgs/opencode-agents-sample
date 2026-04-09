"""
agents/writer.py
Calls @web-writer. Uses absolute path for README.
"""
import json
from pathlib import Path
from agents.base_agent import BaseAgent


class WriterAgent(BaseAgent):
    opencode_agent = "web-writer"
    role = "writer"

    def run(self, plan: dict) -> str:
        print(f"\n[WriterAgent] Delegating to OpenCode @{self.opencode_agent}...")

        output_dir = plan["output_dir"]
        readme_path = f"{output_dir}/README.md"

        # List what actually got written
        existing = []
        for f in plan.get("all_files", []):
            fp = Path(output_dir) / f
            if fp.exists():
                existing.append(f)

        prompt = f"""Write a README.md for this completed web application.

## Build Plan
```json
{json.dumps(plan, indent=2)}
```

## Files that were generated
{chr(10).join(existing) or '(check output directory)'}

## CRITICAL: Write the README to this exact absolute path:
{readme_path}

Use the write tool with path: {readme_path}"""

        response = self.send(prompt)
        print(f"  [WriterAgent] README → {readme_path}")
        return response
