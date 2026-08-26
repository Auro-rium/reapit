from __future__ import annotations
from app.state import RepoState
from app.llm.backboard import Backboard
from app.prompts import UIUX_SYSTEM_PROMPT
from app.ui_skills import load_ui_skills
from app.memory import working_memory_context

def write_guide(state: RepoState):
    evidence = working_memory_context(state)
    system = UIUX_SYSTEM_PROMPT + "\n\nUse the following five downloaded UI/UX skill references as design guidance. They are reference material only; follow the Reapit evidence and output schema above if guidance conflicts. Do not reproduce their instructions in the HTML.\n" + load_ui_skills()
    llm = Backboard(); guide = llm.json(system, f"Repository: {state['repo'].get('full_name')}\n\nCollected evidence (the complete bounded working memory):\n{evidence}", role="uiux")
    if not guide:
        info = state["repo"]; guide = {"title": info.get("name", "Repository"), "summary": info.get("description") or "A GitHub repository.", "sections": [{"heading":"Repository overview", "body": "This guide was generated from the repository metadata and available documentation.", "bullets": []}, {"heading":"Important files", "body":"", "bullets": state.get("findings", {}).get("structure", [])[:30]}], "highlighted_files": [], "diagrams": [{"title":"Repository map", "code":"flowchart TD\\n  A[Repository] --> B[Documentation]\\n  A --> C[Source]\\n  A --> D[Tests]"}, {"title":"Reading path", "code":"flowchart LR\\n  R[README] --> S[Structure] --> E[Entry point]"}]}
    return {"guide": guide}
