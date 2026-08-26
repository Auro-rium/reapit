from __future__ import annotations
from typing import Any
from app.llm.backboard import Backboard
from app.prompts import system_prompt

def ask(section: str, role_key: str, evidence: str, fallback: Any):
    result = Backboard().json(system_prompt(section), evidence, role=role_key)
    return result or fallback
