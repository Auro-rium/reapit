"""The four reasoning agents; repository capabilities remain deterministic tools."""
from app.state import RepoState
from app.agents.readers import (markdown_reader, structure_reader, metadata_reader,
    contributors_reader, links_reader, specialist_reader)
from app.agents.ui_planning import (visual_strategy, information_architecture,
    accessibility_review, diagram_strategy)
from app.agents.uiux import write_guide

RESEARCH_TOOLS = (markdown_reader, structure_reader, metadata_reader,
                  contributors_reader, links_reader, specialist_reader)
DESIGN_WORK = (visual_strategy, information_architecture,
               accessibility_review, diagram_strategy)

def research_agent(state: RepoState):
    """One reasoning agent orchestrating deterministic repository tools."""
    updates = {}
    current = dict(state)
    for tool in RESEARCH_TOOLS:
        result = tool(current)
        updates.update(result)
        current.update(result)
    findings = updates.get("findings", current.get("findings", {}))
    return {"findings": findings, "research": findings}

def design_agent(state: RepoState):
    """One design decision agent producing a structured design brief."""
    updates = {}
    current = dict(state)
    for decision in DESIGN_WORK:
        result = decision(current)
        updates.update(result)
        current.update(result)
    findings = updates.get("findings", current.get("findings", {}))
    design = {k: v for k, v in findings.items() if k.startswith("ui_")}
    return {"findings": findings, "design": design}

def builder_agent(state: RepoState):
    result = write_guide(state)
    return {**result, "build": {"revision": state.get("build", {}).get("revision", 0) + 1, "status": "completed"}}
