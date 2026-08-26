from __future__ import annotations
import re
from .base import selected, put
from app.state import RepoState
from app.tools.github import fetch_contributors
from app.agents.llm_helpers import ask
from app.tools.reader_tools import select_markdown_files, select_specialist_files

def markdown_reader(state: RepoState):
    if not selected(state, "markdown"): return {}
    docs = {p: t for p, t in state.get("files", {}).items() if p.lower().endswith((".md", ".mdx"))}
    candidates = select_markdown_files.invoke({"file_paths": list(docs)})
    evidence = "Choose the five most informative Markdown files from this inventory and excerpts.\n" + "\n\n".join(f"PATH: {p}\n{docs[p][:6000]}" for p in candidates)
    result = ask("Markdown reader", "markdown", evidence, {"selected_paths": candidates[:5], "documents": {p: docs[p] for p in candidates[:5]}})
    return put(state, "markdown", result)

def structure_reader(state: RepoState):
    if not selected(state, "structure"): return {}
    files = sorted(state.get("files", {}))
    result = ask("File-structure reader", "structure", "File inventory:\n" + "\n".join(files), {"important_files": files[:40], "groups": [], "entry_points": []})
    return put(state, "structure", result)

def metadata_reader(state: RepoState):
    if not selected(state, "metadata"): return {}
    info = state.get("repo", {})
    raw = {k: info.get(k) for k in ("full_name", "description", "language", "license", "stargazers_count", "forks_count", "topics", "html_url", "created_at", "updated_at")}
    result = ask("Metadata and contributor reader", "metadata", f"GitHub metadata:\n{raw}", {"project_metadata": raw, "interpretation": [], "missing_data": []})
    return put(state, "metadata", result)

def contributors_reader(state: RepoState):
    if not selected(state, "contributors"): return {}
    contributors = fetch_contributors(state.get("repo", {}))
    result = ask("Metadata and contributor reader", "contributors", f"Contributor records from GitHub API:\n{contributors}", {"contributors": contributors, "interpretation": [], "missing_data": []})
    return put(state, "contributors", result)

def links_reader(state: RepoState):
    if not selected(state, "links"): return {}
    links = []
    for text in state.get("files", {}).values(): links += re.findall(r'https?://[^\s)\]>"]+', text)
    links = list(dict.fromkeys(links))[:8]
    result = ask("Related-links reader", "links", f"Extracted URLs:\n{links}", {"resources": links, "unavailable": [], "notable_references": []})
    return put(state, "links", result)

def specialist_reader(state: RepoState):
    if not selected(state, "specialist"): return {}
    files = state.get("files", {})
    selected_files = select_specialist_files.invoke({"file_paths": list(files)})
    important = {p: files[p] for p in selected_files}
    result = ask("Specialist reader", "specialist", "Selected artifacts:\n" + "\n\n".join(f"PATH: {p}\n{v[:8000]}" for p, v in list(important.items())[:30]), {"evidence": important, "runtime": [], "dependencies": [], "interfaces": [], "development": [], "deployment": [], "risks": []})
    return put(state, "specialist", result)
