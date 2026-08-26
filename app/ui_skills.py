from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"

def load_ui_skills() -> str:
    files = sorted(p for p in SKILLS_DIR.glob("*.md") if p.name != "SOURCES.md")[:5]
    blocks = []
    for path in files:
        blocks.append(f"\n--- UI/UX skill reference: {path.name} ---\n{path.read_text(encoding='utf-8')[:14000]}")
    return "\n".join(blocks)
