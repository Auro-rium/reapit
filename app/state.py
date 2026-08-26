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
    guide: dict[str, Any]
    output_path: str
    qa: dict[str, Any]
    screen_review: dict[str, Any]
    errors: list[str]
