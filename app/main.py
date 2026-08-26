from __future__ import annotations
import argparse, os, uuid
import httpx
from pathlib import Path
from dotenv import load_dotenv
from app.graph import build_graph
from app.render import render
from app.tools.github import fetch_repo
from app.persistence import save
from app.evaluator import evaluate_artifact

def run(url: str, run_id: str | None = None) -> Path:
    load_dotenv(); run_id = run_id or uuid.uuid4().hex
    save(run_id, url, "running")
    try:
        repo, files = fetch_repo(url)
        state = build_graph().invoke({"run_id": run_id, "memory_version": 1, "url": url, "repo": repo, "files": files, "findings": {}, "human": {"status": "pending", "feedback": ""}})
        name = repo.get("name", "repository")
        output = Path("outputs") / name / "index.html"
        render(state["guide"], repo, output)
        browser = {}
        try:
            browser = httpx.post("http://screen-env:8100/agent-inspect", json={"url": f"http://reapit:8000/open/{name}", "run_id": run_id}, timeout=300).json()
        except Exception as exc:
            browser = {"status": "unavailable", "error": str(exc)}
        browser["deterministic"] = evaluate_artifact(output)
        state["browser"] = browser
        state["screen_review"] = browser  # backwards-compatible API field
        kept = {k: state.get(k) for k in ("run_id", "memory_version", "url", "repo", "plan", "findings", "research", "design", "build", "guide", "qa", "browser", "screen_review", "human")}
        save(run_id, url, "completed", name, str(output), kept, approval="pending")
        return output
    except Exception as exc:
        save(run_id, url, "failed", error=str(exc), approval="pending")
        raise

def main():
    parser = argparse.ArgumentParser(description="Turn a GitHub repository into a readable HTML guide")
    parser.add_argument("url", help="Public GitHub repository URL")
    args = parser.parse_args()
    try: print(f"Wrote {run(args.url)}")
    except Exception as exc:
        raise SystemExit(f"Reapit failed: {exc}")

if __name__ == "__main__": main()
