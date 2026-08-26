"""Central prompt registry. prompts.md remains the editable source of truth."""
from pathlib import Path

PROMPTS_FILE = Path(__file__).resolve().parents[1] / "prompts.md"

def system_prompt(section: str) -> str:
    text = PROMPTS_FILE.read_text(encoding="utf-8")
    marker = f"## {section} system prompt"
    if marker not in text:
        raise KeyError(f"Prompt section not found: {section}")
    body = text.split(marker, 1)[1]
    body = body.split("\n## ", 1)[0]
    shared = text.split("## Shared operating rules", 1)[1].split("\n## ", 1)[0]
    return ("You are operating under the following shared rules:\n" + shared.strip() + "\n\n" + body.strip())

UIUX_SYSTEM_PROMPT = system_prompt("UI/UX writer")
PLANNER_SYSTEM_PROMPT = system_prompt("Planner")
