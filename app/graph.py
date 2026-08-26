from langgraph.graph import StateGraph, START, END
from app.state import RepoState
from app.agents.planner import planner
from app.agents.readers import markdown_reader, structure_reader, metadata_reader, contributors_reader, links_reader, specialist_reader
from app.agents.uiux import write_guide
from app.agents.ui_planning import visual_strategy, information_architecture, accessibility_review, diagram_strategy
from app.agents.qa import quality_review

def build_graph():
    g = StateGraph(RepoState)
    g.add_node("planner", planner); g.add_node("markdown", markdown_reader); g.add_node("structure", structure_reader); g.add_node("metadata", metadata_reader); g.add_node("contributors", contributors_reader); g.add_node("links", links_reader); g.add_node("specialist", specialist_reader)
    g.add_node("ui_visual_strategy", visual_strategy); g.add_node("ui_information_architecture", information_architecture); g.add_node("ui_accessibility", accessibility_review); g.add_node("ui_diagram_strategy", diagram_strategy); g.add_node("uiux", write_guide); g.add_node("qa", quality_review)
    g.add_edge(START, "planner")
    research_nodes = ("markdown", "structure", "metadata", "contributors", "links", "specialist")
    for node in research_nodes: g.add_edge("planner", node)
    for design_node in ("ui_visual_strategy", "ui_information_architecture", "ui_accessibility", "ui_diagram_strategy"):
        for research_node in research_nodes: g.add_edge(research_node, design_node)
        g.add_edge(design_node, "uiux")
    g.add_edge("uiux", "qa")
    g.add_edge("qa", END)
    return g.compile()
