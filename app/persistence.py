from __future__ import annotations
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("outputs") / "reapit.db"

def _now(): return datetime.now(timezone.utc).isoformat()
def init():
    DB_PATH.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS runs (
          run_id TEXT PRIMARY KEY, url TEXT NOT NULL, repository TEXT,
          status TEXT NOT NULL, approval TEXT NOT NULL DEFAULT 'pending',
          output_path TEXT, state_json TEXT, error TEXT, created_at TEXT, updated_at TEXT)""")

def save(run_id, url, status, repository=None, output_path=None, state=None, error=None, approval="pending"):
    init()
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?,?,?,?,?,?)""", (run_id,url,repository,status,approval,output_path,json.dumps(state or {},default=str),error,_now(),_now()))

def get(run_id):
    init()
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        row = db.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
    return dict(row) if row else None

def list_runs(limit=50):
    init()
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        return [dict(x) for x in db.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()]

def decide(run_id, approval):
    init()
    with sqlite3.connect(DB_PATH) as db:
        db.execute("UPDATE runs SET approval=?, updated_at=? WHERE run_id=?", (approval,_now(),run_id))
    return get(run_id)

def request_repair(run_id, feedback=""):
    """Persist human repair feedback without destroying the current artifact."""
    init()
    with sqlite3.connect(DB_PATH) as db:
        row = db.execute("SELECT state_json FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if not row: return None
        state = json.loads(row[0] or "{}")
        state["human"] = {"status": "repair_requested", "feedback": feedback}
        db.execute("UPDATE runs SET approval=?, state_json=?, updated_at=? WHERE run_id=?",
                   ("repair_requested", json.dumps(state, default=str), _now(), run_id))
    return get(run_id)
