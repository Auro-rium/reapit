from __future__ import annotations
import json, logging, os
from typing import Any
import httpx
from langsmith import traceable

log = logging.getLogger("reapit.backboard")

TOKEN_BUDGETS = {
    "planner": 1200,
    "markdown": 2400,
    "structure": 1600,
    "metadata": 1200,
    "contributors": 1000,
    "links": 1600,
    "specialist": 2400,
    "uiux": 50000,
    "ui_strategy": 1800,
    "ui_architecture": 1800,
    "ui_accessibility": 1600,
    "ui_diagrams": 1600,
    "ui_qa": 2400,
}

class Backboard:
    def __init__(self):
        key = os.getenv("BACKBOARD_API_KEY")
        self.enabled = bool(key and key not in {"your_backboard_api_key_here", "changeme"})
        self.model_name = os.getenv("BACKBOARD_MODEL", "gpt-4o")
        self.base_url = os.getenv("BACKBOARD_BASE_URL", "https://app.backboard.io/api").rstrip("/")
        self.api_key = key or "unused"

    def _post(self, client, url, **kwargs):
        last = None
        for attempt in range(3):
            try:
                return client.post(url, **kwargs)
            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
                last = exc
                if attempt < 2:
                    import time; time.sleep(2 ** attempt)
        raise last

    @traceable(name="reapit-backboard-agent")
    def text(self, system: str, user: str, role: str = "uiux") -> str:
        if not self.enabled: return ""
        budget = int(os.getenv(f"REAPIT_{role.upper()}_MAX_TOKENS", TOKEN_BUDGETS.get(role, 1500)))
        headers = {"X-API-Key": self.api_key}
        try:
            with httpx.Client(timeout=120, follow_redirects=True, headers=headers) as client:
                assistant = self._post(client, f"{self.base_url}/assistants", json={"name": f"reapit-{role}", "system_prompt": system})
                assistant.raise_for_status()
                assistant_id = assistant.json()["assistant_id"]
                thread = self._post(client, f"{self.base_url}/assistants/{assistant_id}/threads", json={})
                thread.raise_for_status()
                thread_id = thread.json()["thread_id"]
                payload = {"content": user, "stream": "false", "max_tokens": str(budget)}
                if self.model_name:
                    payload["model_name"] = self.model_name
                response = self._post(client, f"{self.base_url}/threads/{thread_id}/messages", data=payload)
                response.raise_for_status()
                return str(response.json().get("content", ""))
        except Exception as exc:
            log.exception("Backboard request failed; using deterministic fallback: %s", exc)
            return ""
    def json(self, system: str, user: str, role: str = "uiux") -> dict[str, Any]:
        raw = self.text(system, user, role=role).strip().removeprefix("```json").removesuffix("```").strip()
        try: return json.loads(raw)
        except json.JSONDecodeError: return {}
