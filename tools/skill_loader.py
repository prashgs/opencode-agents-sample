"""
tools/skill_loader.py
Reads .opencode/skills/<name>/SKILL.md files from the project.
Used by Python agents that need skill content directly
(e.g. when feeding it as a system prompt to Ollama).
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / ".opencode" / "skills"


def load_skill(skill_name: str) -> str:
    """Load a skill by name. Raises FileNotFoundError if missing."""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(
            f"Skill not found: {skill_path}\nAvailable: {list_skills()}"
        )
    return skill_path.read_text(encoding="utf-8")


def list_skills() -> list[str]:
    """List available skill names."""
    if not SKILLS_DIR.exists():
        return []
    return [p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")]
