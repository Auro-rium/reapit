from langgraph.graph import StateGraph, START, END
from app.state import RepoState
from app.agents.planner import planner
from app.agents.consolidated import research_agent, design_agent, builder_agent
from app.agents.qa import quality_review

def build_graph():
    """Four reasoning agents; all repository inspection is tool work."""
    g = StateGraph(RepoState)
    for name, fn in (("planner", planner), ("research", research_agent),
                     ("design", design_agent), ("builder", builder_agent),
                     ("evaluator", quality_review)):
        g.add_node(name, fn)
    g.add_edge(START, "planner")
    g.add_edge("planner", "research")
    g.add_edge("research", "design")
    g.add_edge("design", "builder")
    g.add_edge("builder", "evaluator")
    g.add_edge("evaluator", END)
    return g.compile()
