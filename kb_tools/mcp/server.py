"""MCP server — Model Context Protocol for agent integration."""

from __future__ import annotations

import json
import sys
from typing import Any

from kb_tools.config import load_config
from kb_tools.reasoning.gaps import GapDetector
from kb_tools.reasoning.generator import Generator
from kb_tools.search.engine import SearchEngine

_config = load_config()
_engine = SearchEngine(_config)
_generator = Generator(_config)
_gap_detector = GapDetector(_config)


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    """Handle a single MCP JSON-RPC request."""
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "cathkb", "version": "1.0.0"},
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": _tool_definitions()},
        }

    if method == "tools/call":
        return _handle_tool_call(req_id, params)

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }


def _tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "cathkb_search",
            "description": (
                "Search the Catholic knowledge base for "
                "relevant source chunks"
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "top_k": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        },
        {
            "name": "cathkb_query",
            "description": (
                "Ask a doctrinal question and receive a cited "
                "answer grounded in Catholic sources"
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Doctrinal question",
                    },
                    "top_k": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        },
        {
            "name": "cathkb_artifact",
            "description": (
                "Generate a structured study artifact "
                "(guide, timeline, comparison, brief)"
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic for the artifact",
                    },
                    "artifact_type": {
                        "type": "string",
                        "enum": [
                            "study-guide",
                            "timeline",
                            "comparison",
                            "doctrinal-brief",
                        ],
                        "default": "study-guide",
                    },
                },
                "required": ["topic"],
            },
        },
    ]


def _handle_tool_call(
    req_id: Any, params: dict[str, Any]
) -> dict[str, Any]:
    tool_name = params.get("name", "")
    arguments = params.get("arguments", {})

    if tool_name == "cathkb_search":
        results = _engine.search(
            arguments["query"],
            top_k=arguments.get("top_k", 5),
        )
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {"type": "text", "text": json.dumps(results, indent=2)}
                ]
            },
        }

    if tool_name == "cathkb_query":
        query = arguments["query"]
        if not _gap_detector.has_sufficient_sources(query):
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": _gap_detector.gap_message(query),
                        }
                    ]
                },
            }
        context = _engine.search_with_context(
            query, top_k=arguments.get("top_k", 5)
        )
        result = _generator.generate_with_citations(query, context)
        output = (
            f"{result['response']}\n\n---\n"
            f"{result['formatted_citations']}"
        )
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": output}]
            },
        }

    if tool_name == "cathkb_artifact":
        from kb_tools.reasoning.artifacts import ArtifactGenerator

        gen = ArtifactGenerator(_config)
        path = gen.generate(
            arguments["topic"],
            arguments.get("artifact_type", "study-guide"),
        )
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"Artifact saved to: {path}",
                    }
                ]
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {
            "code": -32601,
            "message": f"Unknown tool: {tool_name}",
        },
    }


def main() -> None:
    """Run the MCP server over stdio."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            continue


if __name__ == "__main__":
    main()
