from __future__ import annotations
from app.state import RepoState

def selected(state: RepoState, name: str) -> bool:
    return name in state.get("plan", [])

def put(state: RepoState, name: str, value):
    findings = dict(state.get("findings", {})); findings[name] = value
    return {"findings": findings}
