from __future__ import annotations
import json
from typing import Any
from app.state import RepoState

def working_memory_context(state: RepoState, limit: int = 90000) -> str:
    """Serialize bounded shared memory deterministically for an LLM call."""
    payload = {
        "repository": state.get("repo", {}),
        "plan": state.get("plan", []),
        "findings": state.get("findings", {}),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    if len(raw) <= limit:
        return raw
    return raw[:limit] + '\n[WORKING MEMORY TRUNCATED: prioritize retained evidence and report unknowns]'
