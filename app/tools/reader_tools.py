"""Evidence tools used by the research graph. They collect facts; interpretation stays LLM-backed."""
from __future__ import annotations
from langchain_core.tools import tool

@tool
def select_markdown_files(file_paths: list[str]) -> list[str]:
    """Return Markdown candidates for the documentation tool."""
    docs = [p for p in file_paths if p.lower().endswith((".md", ".mdx"))]
    priority = [p for p in docs if p.lower().split("/")[-1] in {"readme.md", "technical.md", "contributing.md"}]
    return list(dict.fromkeys(priority + docs))[:40]

@tool
def select_specialist_files(file_paths: list[str]) -> list[str]:
    """Return high-value entry point, config, API, deployment, and example files."""
    keys = ("docker", "config", "example", "api", "main", "index", "workflow")
    return [p for p in file_paths if any(key in p.lower() for key in keys)][:40]

RESEARCH_TOOLS = [select_markdown_files, select_specialist_files]
