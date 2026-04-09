"""
agents/orchestrator.py
Master coordinator. Manages the full agentic build loop.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.opencode_server import OpenCodeServer
from tools.opencode_client import OpenCodeClient
from agents.planner import PlannerAgent
from agents.frontend_agent import FrontendAgent
from agents.backend_agent import BackendAgent
from agents.reviewer import ReviewerAgent
from agents.writer import WriterAgent


class Orchestrator:
    def __init__(self, config: dict):
        self.config = config
        self.max_iterations = config.get("max_loop_iterations", 4)
        self.project_dir = str(Path(__file__).parent.parent.resolve())
        self.server_port = config.get("opencode_server_port", 4096)
        self.server_host = config.get("opencode_server_host", "127.0.0.1")

    def run(self, user_prompt: str) -> dict:
        print("\n" + "=" * 62)
        print("  🤖  WEBGEN AGENT  (powered by OpenCode)")
        print("=" * 62)
        print(f"  Prompt: {user_prompt[:100]}{'...' if len(user_prompt) > 100 else ''}")
        print(f"  Project dir: {self.project_dir}")

        with OpenCodeServer(
            project_dir=self.project_dir,
            port=self.server_port,
            hostname=self.server_host,
            startup_timeout=30,
        ) as server:
            client: OpenCodeClient = server.client
            # Ensure client knows the project dir for cwd in subprocesses
            client.project_dir = self.project_dir

            session = client.create_session(title=f"webgen: {user_prompt[:50]}")
            session_id = session["id"]
            print(f"\n  OpenCode session: {session_id}")

            # Phase 1: Plan
            print("\n📋  Phase 1: Planning")
            planner = PlannerAgent(client, session_id)
            plan = planner.run(user_prompt)

            print(f"  App:        {plan['app_name']}")
            print(f"  Output dir: {plan['output_dir']}")
            print(f"  Backend:    {plan['has_backend']}")
            print(f"  Features:   {', '.join(plan['features'])}")
            print(f"  Files:      {', '.join(plan['all_files'])}")

            # Ensure output dir exists
            Path(plan["output_dir"]).mkdir(parents=True, exist_ok=True)

            # Phase 2: Generate + Review loop
            print(f"\n⚙️   Phase 2: Generation Loop (max {self.max_iterations} iterations)")

            frontend_agent = FrontendAgent(client, session_id)
            backend_agent = BackendAgent(client, session_id)
            reviewer = ReviewerAgent(client, session_id)

            feedback: list = []
            final_review = {}
            iteration = 1

            for iteration in range(1, self.max_iterations + 1):
                print(f"\n--- Iteration {iteration}/{self.max_iterations} ---")

                frontend_agent.run(plan, feedback if feedback else None)

                if plan.get("has_backend"):
                    backend_agent.run(plan, feedback if feedback else None)

                # Show what was actually written after each iteration
                written_now = self._list_files(plan["output_dir"])
                print(f"  Files on disk after iteration {iteration}: {len(written_now)}")
                for f in written_now:
                    print(f"    ✓ {f}")

                print(f"\n🔍  Review")
                review = reviewer.run(plan)
                final_review = review

                if review.get("approved"):
                    print(f"\n  ✅ Approved on iteration {iteration}")
                    break

                if iteration < self.max_iterations:
                    feedback = (
                        review.get("issues", []) +
                        review.get("missing_features", [])
                    )
                    print(f"  🔁 Revising with {len(feedback)} issue(s)")
                else:
                    print("  ⚠️  Max iterations reached — writing best result")

            # Phase 3: README
            print(f"\n📝  Phase 3: Writing README")
            WriterAgent(client, session_id).run(plan)

        output_dir = plan["output_dir"]
        written = self._list_files(output_dir)

        print("\n" + "=" * 62)
        print(f"  ✅  DONE!")
        print(f"  App written to: {output_dir}/")
        print(f"  Files written: {len(written)}")
        print("=" * 62)

        return {
            "plan": plan,
            "output_dir": output_dir,
            "files_written": written,
            "iterations": iteration,
            "review": final_review,
            "session_id": session_id,
        }

    def _list_files(self, output_dir: str) -> list:
        p = Path(output_dir)
        if not p.exists():
            return []
        return sorted(str(f) for f in p.rglob("*") if f.is_file())
