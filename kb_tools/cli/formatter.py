"""Output formatting for CLI responses."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table


def print_search_results(results: list[dict[str, Any]], console: Console | None = None) -> None:
    """Format and print search results."""
    console = console or Console()
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return
    for i, r in enumerate(results, 1):
        score = r.get("score", 0)
        source = r.get("source_path", r.get("doc_id", "?"))
        section = r.get("section_label", "")
        preview = r.get("text_preview", r.get("text", ""))[:200]
        console.print(Panel(
            f"[bold]{source}[/bold] — {section} (score: {score:.3f})\n\n{preview}...",
            title=f"Result {i}",
        ))


def print_response(response: str, citations: str, console: Console | None = None) -> None:
    """Format and print a generated response with citations."""
    console = console or Console()
    console.print(Panel(Markdown(response), title="Response", border_style="green"))
    if citations:
        console.print(Panel(citations, title="Citations", border_style="blue"))


def print_table(headers: list[str], rows: list[list[str]], title: str = "") -> None:
    """Print a formatted table."""
    table = Table(title=title)
    for h in headers:
        table.add_column(h)
    for row in rows:
        table.add_row(*row)
    Console().print(table)
