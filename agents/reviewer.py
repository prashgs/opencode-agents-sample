"""
agents/reviewer.py
Calls @web-reviewer. Passes absolute file paths for it to cat-read.
"""
import json
import re
from pathlib import Path
from agents.base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    opencode_agent = "web-reviewer"
    role = "reviewer"

    def run(self, plan: dict) -> dict:
        print(f"\n[ReviewerAgent] Delegating to OpenCode @{self.opencode_agent}...")

        output_dir = plan["output_dir"]

        # List which files actually exist on disk
        existing = []
        for f in plan.get("all_files", []):
            fp = Path(output_dir) / f
            if fp.exists():
                existing.append(str(fp))

        if existing:
            file_list = "\n".join(f"  cat {p}" for p in existing)
            read_instruction = (
                f"Read each file using bash:\n{file_list}"
            )
        else:
            read_instruction = (
                f"WARNING: No files found in {output_dir}/\n"
                f"Try: ls {output_dir}\n"
                "If the directory is empty, report approved:false with issue 'No files were generated'."
            )

        prompt = f"""Review this web application against its build plan.

## Build Plan
```json
{json.dumps(plan, indent=2)}
```

## Reading the Files
{read_instruction}

## Your Task
Check that all features are implemented and the code is functional.
Return ONLY a JSON verdict — no explanation, no markdown:
{{
  "approved": true or false,
  "score": 0-10,
  "issues": ["issue1", "issue2"],
  "missing_features": ["feature1"],
  "suggestions": []
}}"""

        raw = self.send(prompt)
        return self._parse(raw)

    def _parse(self, raw: str) -> dict:
        clean = re.sub(r'\x1b\[[0-9;]*[mGKHF]', '', raw)
        clean = re.sub(r"```(?:json)?", "", clean).strip().rstrip("`").strip()
        m = re.search(r"\{.*\}", clean, re.DOTALL)
        if m:
            clean = m.group(0)
        try:
            review = json.loads(clean)
        except json.JSONDecodeError:
            print("  [ReviewerAgent] JSON parse failed — defaulting to approved")
            review = {"approved": True, "score": 7, "issues": [], "missing_features": [], "suggestions": []}

        approved = review.get("approved", False)
        score = review.get("score", "?")
        print(f"  [ReviewerAgent] {'✅ APPROVED' if approved else '❌ NEEDS REVISION'} | Score: {score}/10")
        for issue in review.get("issues", []):
            print(f"    ⚠  {issue}")
        for feat in review.get("missing_features", []):
            print(f"    ✗  Missing: {feat}")
        return review
