from __future__ import annotations
from pathlib import Path
from html.parser import HTMLParser

class _Parser(HTMLParser):
    def __init__(self): super().__init__(); self.ids=set(); self.errors=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if "id" in attrs: self.ids.add(attrs["id"])

def evaluate_artifact(path: Path) -> dict:
    """Cheap, deterministic checks kept separate from subjective visual review."""
    result = {"html_valid": False, "required_sections": [], "console_errors": [], "issues": []}
    try:
        text = path.read_text(encoding="utf-8")
        parser = _Parser(); parser.feed(text); parser.close()
        result["html_valid"] = True
        required = ["header", "main"]
        result["required_sections"] = [{"name": x, "present": f"<{x}" in text.lower()} for x in required]
        result["issues"] = [f"Missing <{x}>" for x in required if f"<{x}" not in text.lower()]
    except Exception as exc:
        result["issues"].append(str(exc))
    result["passed"] = result["html_valid"] and not result["issues"]
    return result
