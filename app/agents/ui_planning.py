from __future__ import annotations
from app.state import RepoState
from app.agents.base import put
from app.agents.llm_helpers import ask

def _evidence(state: RepoState) -> str:
    return f"Repository: {state.get('repo', {}).get('full_name')}\nResearch findings:\n{str(state.get('findings', {}))[:90000]}"

def visual_strategy(state: RepoState):
    result = ask("UI/UX writer", "ui_strategy", _evidence(state) + "\nDefine a visual direction, palette, typography mood, density, and responsive composition. Return JSON with visual_direction, palette, layout_principles, risks.", {})
    return put(state, "ui_visual_strategy", result)

def information_architecture(state: RepoState):
    result = ask("UI/UX writer", "ui_architecture", _evidence(state) + "\nPlan the information architecture and reading sequence. Return JSON with navigation, section_order, hierarchy, progressive_disclosure.", {})
    return put(state, "ui_information_architecture", result)

def accessibility_review(state: RepoState):
    result = ask("UI/UX writer", "ui_accessibility", _evidence(state) + "\nAct as an accessibility and readability reviewer. Return JSON with contrast, typography, responsive, semantics, and risks.", {})
    return put(state, "ui_accessibility", result)

def diagram_strategy(state: RepoState):
    result = ask("UI/UX writer", "ui_diagrams", _evidence(state) + "\nPlan 2–3 useful Mermaid diagrams grounded in the findings. Return JSON with diagrams, relationships, and validation_notes.", {})
    return put(state, "ui_diagram_strategy", result)
