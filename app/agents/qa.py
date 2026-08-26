from __future__ import annotations
from app.state import RepoState
from app.agents.llm_helpers import ask
from app.memory import working_memory_context

def quality_review(state: RepoState):
    guide = state.get("guide", {})
    evidence = f"Proposed guide JSON:\n{guide}\n\nRepository working memory:\n{working_memory_context(state, 50000)}"
    review = ask("HTML QA reviewer", "ui_qa", evidence, {"approved": True, "issues": [], "repairs": []})
    repaired = dict(guide)
    if review.get("repaired_layout_html"):
        repaired["layout_html"] = review["repaired_layout_html"]
    if review.get("repaired_custom_css"):
        repaired["custom_css"] = review["repaired_custom_css"]
    if review.get("repaired_diagrams"):
        repaired["diagrams"] = review["repaired_diagrams"]
    return {"guide": repaired, "qa": review}
