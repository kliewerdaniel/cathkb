"""Web server — FastAPI application."""

from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from kb_tools.config import load_config
from kb_tools.reasoning.gaps import GapDetector
from kb_tools.reasoning.generator import Generator as LLMGenerator
from kb_tools.search.engine import SearchEngine

app = FastAPI(title="Catholic Knowledge System", version="1.0.0")

templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"
templates_dir.mkdir(exist_ok=True)
static_dir.mkdir(exist_ok=True)

app.mount(
    "/static", StaticFiles(directory=str(static_dir)), name="static"
)
templates = Jinja2Templates(directory=str(templates_dir))

_config = load_config()
_engine = SearchEngine(_config)
_llm = LLMGenerator(_config)
_gap_detector = GapDetector(_config)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "index.html", {"request": request}
    )


@app.get("/api/search")
async def api_search(q: str, top_k: int = 10) -> dict[str, object]:
    results = _engine.search(q, top_k=top_k)
    return {"query": q, "results": results, "count": len(results)}


@app.post("/api/query")
async def api_query(request: Request) -> dict[str, object]:
    body = await request.json()
    query = body.get("query", "")
    top_k = body.get("top_k", 5)

    if not _gap_detector.has_sufficient_sources(query):
        return {
            "query": query,
            "response": _gap_detector.gap_message(query),
            "citations": [],
            "is_gap": True,
        }

    context = _engine.search_with_context(query, top_k=top_k)
    result = _llm.generate_with_citations(query, context)
    return {
        "query": query,
        "response": result["response"],
        "citations": result["formatted_citations"],
        "is_gap": False,
    }


@app.post("/api/query/stream")
async def api_query_stream(request: Request) -> StreamingResponse:
    body = await request.json()
    query = body.get("query", "")
    top_k = body.get("top_k", 5)

    context = _engine.search_with_context(query, top_k=top_k)

    def sse_generate() -> Generator[str, None, None]:
        import httpx

        messages = [
            {
                "role": "user",
                "content": (
                    f"Based on the sources below, answer: "
                    f"{query}\n\nSources:\n{context}"
                ),
            }
        ]
        with httpx.stream(
            "POST",
            f"{_config.ollama_base_url}/api/chat",
            json={
                "model": _config.ollama_model,
                "messages": messages,
                "stream": True,
            },
            timeout=120,
        ) as resp:
            for line in resp.iter_lines():
                if line:
                    data = json.loads(line)
                    token = data.get("message", {}).get(
                        "content", ""
                    )
                    if token:
                        payload = json.dumps({"token": token})
                        yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_generate(), media_type="text/event-stream"
    )
