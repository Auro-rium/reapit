from __future__ import annotations
from app.main import run
from app.persistence import get, list_runs, decide
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("reapit", host="0.0.0.0", port=8090)

@mcp.tool()
def generate_repository_guide(github_url: str) -> dict:
    """Research a public GitHub repository and generate its HTML guide."""
    path = run(github_url)
    return {"repository": path.parent.name, "path": str(path), "url": f"/open/{path.parent.name}"}

@mcp.tool()
def list_generation_runs(limit: int = 20) -> list[dict]:
    """List persisted repository-guide generation runs."""
    return list_runs(limit)

@mcp.tool()
def get_generation_run(run_id: str) -> dict:
    """Get status, QA, screen review, and approval state for a run."""
    return get(run_id) or {"error": "run not found", "run_id": run_id}

@mcp.tool()
def approve_generation(run_id: str, approved: bool, feedback: str = "") -> dict:
    """Approve or reject a generated guide as a human reviewer."""
    result = decide(run_id, "approved" if approved else "rejected")
    if not result: return {"error": "run not found", "run_id": run_id}
    result["human_feedback"] = feedback
    return result

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
