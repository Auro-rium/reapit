from __future__ import annotations
from typing import Annotated, Any, TypedDict
def merge_findings(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return {**(left or {}), **(right or {})}

class RepoState(TypedDict, total=False):
    run_id: str
    memory_version: int
    url: str
    repo: dict[str, Any]
    files: dict[str, str]
    plan: list[str]
    findings: Annotated[dict[str, Any], merge_findings]
    research: dict[str, Any]
    design: dict[str, Any]
    build: dict[str, Any]
    browser: dict[str, Any]
    human: dict[str, Any]
    guide: dict[str, Any]
    output_path: str
    qa: dict[str, Any]
    screen_review: dict[str, Any]
    errors: list[str]
