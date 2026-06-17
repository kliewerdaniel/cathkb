"""Web server — FastAPI application with full UI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
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

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

_config = load_config()
_engine = SearchEngine(_config)
_llm = LLMGenerator(_config)
_gap_detector = GapDetector(_config)


def _load_catalog() -> Any:
    catalog_path = _config.kb_index_dir / "catalog.json"
    if catalog_path.exists():
        with open(catalog_path) as f:
            return json.load(f)
    return {"total_documents": 0, "categories": {}, "documents": []}


def _load_model_info() -> Any:
    info_path = _config.embeddings_dir / "model-info.json"
    if info_path.exists():
        with open(info_path) as f:
            return json.load(f)
    return {"model": "unknown", "dimensions": 0, "total_chunks": 0}


def _dashboard_stats() -> dict:
    catalog: dict[str, Any] = _load_catalog()
    model_info: dict[str, Any] = _load_model_info()
    cat_map: dict[str, str] = {
        "scripture": "Scripture",
        "magisterium/ccc": "Catechism (CCC)",
        "canonlaw": "Canon Law",
        "liturgy/girm": "Liturgy (GIRM)",
        "liturgy/texts": "Liturgical Texts",
        "fathers": "Church Fathers",
        "doctorate": "Church Doctors",
        "magisterium/encyclicals": "Encyclicals",
        "magisterium/exhortations": "Exhortations",
        "magisterium/vatican_ii": "Vatican II",
        "social-teaching": "Social Teaching",
        "mariology": "Mariology",
    }
    categories: dict[str, Any] = catalog.get("categories", {})
    category_list: list[dict[str, Any]] = []
    for key, info in categories.items():
        info_dict: dict[str, Any] = info
        category_list.append(
            {
                "name": cat_map.get(key, key),
                "count": info_dict.get("count", 0),
            }
        )
    return {
        "total_docs": catalog.get("total_documents", 0),
        "categories": len(categories),
        "total_chunks": model_info.get("total_chunks", 0),
        "embed_model": model_info.get("model", "unknown"),
        "embed_dims": model_info.get("dimensions", 0),
        "llm_model": _config.ollama_model,
        "category_list": category_list,
    }


# ── Page Routes ───────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "request": request,
            "active_page": "home",
            "stats": _dashboard_stats(),
        },
    )


@app.get("/query", response_class=HTMLResponse)
async def query_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "query.html",
        {
            "request": request,
            "active_page": "query",
        },
    )


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "search.html",
        {
            "request": request,
            "active_page": "search",
        },
    )


@app.get("/browse", response_class=HTMLResponse)
async def browse_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "browse.html",
        {
            "request": request,
            "active_page": "browse",
        },
    )


@app.get("/artifacts", response_class=HTMLResponse)
async def artifacts_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "artifacts.html",
        {
            "request": request,
            "active_page": "artifacts",
        },
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "settings.html",
        {
            "request": request,
            "active_page": "settings",
            "config": _config,
        },
    )


# ── API Routes ────────────────────────────────────


@app.get("/api/health")
async def api_health() -> dict[str, object]:
    import httpx

    try:
        resp = httpx.get(f"{_config.ollama_base_url}/api/tags", timeout=5)
        models = [m["name"] for m in resp.json().get("models", [])]
        return {"status": "ok", "ollama": True, "models": models}
    except Exception:
        return {"status": "ok", "ollama": False, "models": []}


@app.get("/api/search")
async def api_search(q: str = Query(""), top_k: int = 10) -> dict[str, object]:
    if not q:
        return {"query": q, "results": [], "count": 0}
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
            "citations": "",
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


@app.get("/api/documents")
async def api_documents(category: str = "") -> dict[str, object]:
    catalog: dict[str, Any] = _load_catalog()
    docs: list[Any] = catalog.get("documents", [])
    if category:
        docs = [d for d in docs if d.get("category") == category]
    return {"category": category, "documents": docs, "count": len(docs)}


@app.post("/api/artifact")
async def api_artifact(request: Request) -> dict[str, object]:
    from kb_tools.reasoning.artifacts import ArtifactGenerator

    body = await request.json()
    topic = body.get("topic", "")
    artifact_type = body.get("artifact_type", "study-guide")
    if not topic:
        return {"error": "Topic is required"}

    gen = ArtifactGenerator(_config)
    try:
        path = gen.generate(topic, artifact_type)
        content = Path(path).read_text() if Path(path).exists() else ""
        return {"path": path, "content": content}
    except Exception as e:
        return {"error": str(e)}
