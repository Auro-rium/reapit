from __future__ import annotations
import base64, os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import AnyHttpUrl, BaseModel
from playwright.async_api import async_playwright

app = FastAPI(title="Reapit Screen Environment")
SCREENSHOTS = Path("/screenshots")
SCREENSHOTS.mkdir(exist_ok=True)

class InspectRequest(BaseModel):
    url: AnyHttpUrl
    run_id: str

@app.get("/health")
def health(): return {"status": "ok", "service": "screen-env"}

@app.get("/tools")
def tools():
    return {"tools": [
      {"name":"navigate","purpose":"Open the generated guide and wait for network idle"},
      {"name":"screenshot","purpose":"Capture the full rendered screen"},
      {"name":"dom","purpose":"Read headings, links, visible content, and semantic structure"},
      {"name":"mermaid","purpose":"Verify diagrams have rendered SVG output"},
      {"name":"computed_styles","purpose":"Inspect colors and presentation styles"},
      {"name":"layout_metrics","purpose":"Measure viewport, overflow, section dimensions, and spacing"},
      {"name":"console","purpose":"Capture browser runtime errors"}
    ]}

@app.post("/agent-inspect")
async def agent_inspect(request: InspectRequest):
    """Run the actual browser-use visual agent; requires a browser-use LLM key."""
    key = os.getenv("BACKBOARD_API_KEY") or os.getenv("BROWSER_USE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key or key in {"your_backboard_api_key_here", "changeme"}:
        raise HTTPException(status_code=503, detail="Set BACKBOARD_API_KEY for visual browser-use analysis")
    try:
        from browser_use import Agent, BrowserSession
        from backboard_llm import BackboardBrowserLLM
        llm = BackboardBrowserLLM()
        session = BrowserSession(headless=os.getenv("BROWSER_HEADLESS", "false").lower() == "true", user_data_dir="/tmp/browser-profile", downloads_path="/tmp/downloads")
        agent = Agent(task=f"Open {request.url}. Analyze the screen visually and through the DOM. Evaluate orientation, hierarchy, spacing, typography, contrast, responsive layout, and Mermaid diagrams. Return concise JSON with strengths, issues, and concrete CSS/layout recommendations. Do not click external links or submit data.", llm=llm, browser_session=session, use_vision=True, max_actions_per_step=3, max_failures=3)
        history = await agent.run(max_steps=8)
        errors = history.errors()
        return {"run_id": request.run_id, "status": "analyzed" if not errors and history.final_result() else "failed", "result": history.final_result(), "errors": errors}
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/inspect")
async def inspect(request: InspectRequest):
    # This container is the only place allowed to launch a browser.
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=os.getenv("BROWSER_HEADLESS", "false").lower() == "true", args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = await browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        try:
            response = await page.goto(str(request.url), wait_until="networkidle", timeout=60000)
            await page.screenshot(path=str(SCREENSHOTS / f"{request.run_id}.png"), full_page=True)
            evidence = await page.evaluate("""() => ({
              headings: [...document.querySelectorAll('h1,h2,h3')].slice(0,40).map(x => ({tag:x.tagName,text:x.innerText.slice(0,160)})),
              links: [...document.querySelectorAll('a')].slice(0,40).map(x => ({text:x.innerText.slice(0,100),href:x.href})),
              mermaid: [...document.querySelectorAll('.mermaid')].map(x => ({text:x.innerText.slice(0,500), rendered: !!x.querySelector('svg')})),
              body: {width:document.body.scrollWidth,height:document.body.scrollHeight},
              colors: [...new Set([...document.querySelectorAll('body,header,main,section,button,a')].slice(0,80).map(x => getComputedStyle(x).color))].slice(0,20),
              layout: [...document.querySelectorAll('header,main,section')].slice(0,30).map(x => { const r=x.getBoundingClientRect(); return {tag:x.tagName,width:Math.round(r.width),height:Math.round(r.height),top:Math.round(r.top)}; })
            })""")
            result = {"run_id": request.run_id, "status": "captured", "http_status": response.status if response else None, "title": await page.title(), "console_errors": console_errors, "screenshot": f"/screenshots/{request.run_id}.png", "viewport": {"width": 1440, "height": 1100}, "visual_evidence": evidence, "tools_used": ["navigate", "screenshot", "dom", "mermaid", "computed_styles", "layout_metrics", "console"]}
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        finally:
            await browser.close()
        return result
