from __future__ import annotations
from app.state import RepoState
from app.agents.llm_helpers import ask

def planner(state: RepoState):
    files = state.get("files", {})
    names = sorted(files)
    fallback = ["markdown", "structure", "metadata", "contributors"]
    if any(p.lower().endswith(('.md', '.mdx')) for p in names): fallback.append("links")
    if any(x in p.lower() for p in names for x in ("docker", "config", "example", "api", "main", "index")): fallback.append("specialist")
    evidence = f"Repository metadata:\n{state.get('repo', {})}\n\nFile inventory:\n" + "\n".join(names[:10000])
    result = ask("Planner", "planner", evidence, {"readers": fallback, "reasoning": "Fallback plan", "priority_files": names[:20]})
    allowed = {"markdown", "structure", "metadata", "contributors", "links", "specialist"}
    plan = [x for x in result.get("readers", fallback) if x in allowed]
    return {"plan": list(dict.fromkeys(plan or fallback))}
