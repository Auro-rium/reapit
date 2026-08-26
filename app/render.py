from __future__ import annotations
import html
import re
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "repository.html"

def normalize_mermaid(value: object) -> str:
    code = str(value or "").strip()
    code = code.replace("\\n", "\n")
    # Preserve Mermaid statement newlines, but flatten newlines occurring inside
    # quoted node labels (some Mermaid releases reject those).
    chars, quoted = [], False
    for char in code:
        if char == '"':
            quoted = not quoted
            chars.append(char)
        elif char == '\n' and quoted:
            chars.append(' ')
        else:
            chars.append(char)
    code = ''.join(chars)
    if code.startswith("```"):
        code = code.split("\n", 1)[1] if "\n" in code else code
        code = code.removesuffix("```").strip()
    return code

def render(guide: dict, repo: dict, output: Path):
    theme = guide.get("theme", {})
    def color(name: str, default: str) -> str:
        value = str(theme.get(name, default))
        return value if re.fullmatch(r"#[0-9a-fA-F]{6}", value) else default
    radius = str(theme.get("radius", "22px"))
    if not re.fullmatch(r"\d{1,2}px", radius): radius = "22px"
    theme_vars = " ".join([
        f"--bg:{color('background', '#080b16')};",
        f"--panel:{color('panel', '#12182b')};",
        f"--accent:{color('accent', '#9b8cff')};",
        f"--cyan:{color('accent2', '#56d6e8')};",
        f"--radius:{radius};",
    ])
    section_parts = []
    for section in guide.get("sections", []):
        bullets = "".join(f'<li>{html.escape(str(item))}</li>' for item in section.get("bullets", []))
        section_parts.append(
            f'<section><h2>{html.escape(str(section.get("heading", "")))}</h2>'
            f'<p>{html.escape(str(section.get("body", "")))}</p><ul>{bullets}</ul></section>'
        )
    sections = "".join(section_parts)
    diagram_data = guide.get("diagrams") or [
        {"title": "Repository map", "code": "flowchart TD\n  A[Repository] --> B[Documentation]\n  A --> C[Source]\n  A --> D[Tests]"},
        {"title": "Reading path", "code": "flowchart LR\n  R[README] --> S[Structure] --> E[Entry point]"},
    ]
    diagrams = "".join(
        f'<section class="diagram"><h2>{html.escape(str(diagram.get("title", "Architecture")))}</h2>'
        f'<div class="mermaid">{html.escape(normalize_mermaid(diagram.get("code", "")), quote=False)}</div></section>'
        for diagram in diagram_data[:3]
    )
    title = str(guide.get("title", repo.get("name", "Repository")))
    summary = str(guide.get("summary", ""))
    source = str(repo.get("html_url", repo.get("source_url", "")))
    layout = str(guide.get("layout_html", "")).strip()
    if not layout:
        layout = '<header><div class="eyebrow">Repository guide</div><h1>{{TITLE}}</h1><p class="meta">{{SUMMARY}}</p><p><a href="{{SOURCE_URL}}">View on GitHub →</a></p></header><main>{{CONTENT}}{{DIAGRAMS}}</main>'
    layout = re.sub(r"<script\b[^>]*>.*?</script\s*>", "", layout, flags=re.I | re.S)
    layout = re.sub(r"\son[a-z]+\s*=\s*([\"']).*?\1", "", layout, flags=re.I | re.S)
    layout = layout.replace("{{TITLE}}", html.escape(title)).replace("{{SUMMARY}}", html.escape(summary)).replace("{{SOURCE_URL}}", html.escape(str(source)))
    layout = layout.replace("{{CONTENT}}", sections).replace("{{DIAGRAMS}}", diagrams)
    custom_css = str(guide.get("custom_css", ""))
    custom_css = re.sub(r"</?style\\b[^>]*>", "", custom_css, flags=re.I)
    page = TEMPLATE.read_text(encoding="utf-8")
    values = {"TITLE": title, "SUMMARY": summary, "SOURCE_URL": source, "SECTIONS": sections, "DIAGRAMS": diagrams, "THEME_VARS": theme_vars, "LLM_LAYOUT": layout, "CUSTOM_CSS": custom_css}
    for key, value in values.items():
        page = page.replace("{{" + key + "}}", value if key in {"SECTIONS", "DIAGRAMS", "LLM_LAYOUT", "CUSTOM_CSS"} else html.escape(value))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
