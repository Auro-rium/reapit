from __future__ import annotations
from pathlib import Path
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
import httpx
from app.main import run
from app.persistence import get, list_runs, decide

app = FastAPI(title="Reapit", version="0.1.0")
OUTPUTS = Path("outputs")
OUTPUTS.mkdir(exist_ok=True)
app.mount("/guides", StaticFiles(directory=OUTPUTS), name="guides")
DASHBOARD = Path(__file__).resolve().parents[1] / "templates" / "dashboard.html"

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD.read_text(encoding="utf-8")

class GenerateRequest(BaseModel):
    url: HttpUrl
    run_id: str | None = None

@app.get("/health")
def health():
    return {"status": "ok", "service": "reapit"}

@app.post("/screen/inspect")
def screen_inspect(request: GenerateRequest):
    run_id = request.run_id or uuid.uuid4().hex
    try:
        response = httpx.post("http://screen-env:8100/inspect", json={"url": str(request.url), "run_id": run_id}, timeout=90)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Screen environment unavailable: {exc}") from exc

@app.post("/screen/agent-inspect")
def screen_agent_inspect(request: GenerateRequest):
    run_id = request.run_id or uuid.uuid4().hex
    try:
        response = httpx.post("http://screen-env:8100/agent-inspect", json={"url": str(request.url), "run_id": run_id}, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Browser-use environment unavailable: {exc}") from exc

@app.get("/open/{repository}", response_class=FileResponse)
def open_guide(repository: str):
    if "/" in repository or "\\" in repository or repository in {"", ".", ".."}:
        raise HTTPException(status_code=400, detail="Invalid repository name")
    guide = OUTPUTS / repository / "index.html"
    if not guide.is_file():
        raise HTTPException(status_code=404, detail="Generated guide not found")
    return FileResponse(guide, media_type="text/html")

@app.get("/runs")
def runs():
    return {"runs": list_runs()}

@app.get("/runs/{run_id}")
def run_status(run_id: str):
    item = get(run_id)
    if not item: raise HTTPException(status_code=404, detail="Run not found")
    return item

@app.post("/runs/{run_id}/decision")
def human_decision(run_id: str, approved: bool):
    item = get(run_id)
    if not item: raise HTTPException(status_code=404, detail="Run not found")
    return decide(run_id, "approved" if approved else "rejected")

@app.post("/generate")
def generate(request: GenerateRequest):
    run_id = request.run_id or uuid.uuid4().hex
    try:
        path = run(str(request.url), run_id=run_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"run_id": run_id, "status": "completed", "approval": "pending", "repository": path.parent.name, "path": str(path), "url": f"/guides/{path.parent.name}/index.html"}
