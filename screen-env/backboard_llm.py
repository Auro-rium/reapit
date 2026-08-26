from __future__ import annotations
import json, os, httpx
from typing import Any
from browser_use.llm.views import ChatInvokeCompletion

class BackboardBrowserLLM:
    """Browser Use chat-model adapter backed by Backboard's native API."""
    def __init__(self):
        self.model = os.getenv("BACKBOARD_MODEL", "google/gemini-3.1-flash-lite-image")
        self.base_url = os.getenv("BACKBOARD_BASE_URL", "https://app.backboard.io/api").rstrip("/")
        self.api_key = os.environ["BACKBOARD_API_KEY"]

    @property
    def provider(self): return "backboard"
    @property
    def name(self): return self.model
    @property
    def model_name(self): return self.model

    async def ainvoke(self, messages, output_format=None, **kwargs: Any):
        parts = []
        for message in messages:
            role = getattr(message, "role", "user")
            content = getattr(message, "content", "")
            if isinstance(content, list):
                content = "\n".join(getattr(part, "text", "[visual observation]") for part in content)
            parts.append(f"{role.upper()}:\n{content}")
        prompt = "\n\n".join(parts)
        headers = {"X-API-Key": self.api_key}
        async with httpx.AsyncClient(timeout=180, headers=headers) as client:
            schema = output_format.model_json_schema() if output_format is not None else None
            assistant_prompt = "You are a browser-use visual UI reviewer. Follow the client messages exactly. Return only the requested action JSON; do not put an object inside done.text, which must be a string."
            if schema: assistant_prompt += "\nRequired JSON schema:\n" + json.dumps(schema)
            assistant = await client.post(f"{self.base_url}/assistants", json={"name":"reapit-browser-agent", "system_prompt":assistant_prompt})
            assistant.raise_for_status()
            assistant_id = assistant.json()["assistant_id"]
            thread = await client.post(f"{self.base_url}/assistants/{assistant_id}/threads", json={})
            thread.raise_for_status()
            thread_id = thread.json()["thread_id"]
            response = await client.post(f"{self.base_url}/threads/{thread_id}/messages", data={"content": prompt, "model_name": self.model, "stream":"false", "max_tokens":str(kwargs.get("max_tokens", 2400))})
            response.raise_for_status()
            text = str(response.json().get("content", ""))
        if output_format is not None:
            raw = text.strip().removeprefix("```json").removesuffix("```").strip()
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = json.JSONDecoder().raw_decode(raw)[0]
            # Backboard may return a valid Browser Use action without the
            # outer AgentOutput envelope; normalize that envelope here.
            if "action" not in parsed:
                if "done" in parsed:
                    parsed = {"action": [parsed]}
                else:
                    parsed = {"action": [{"done": {"text": json.dumps(parsed)}}]}
            completion = output_format.model_validate(parsed)
        else:
            completion = text
        return ChatInvokeCompletion(completion=completion, usage=None)
