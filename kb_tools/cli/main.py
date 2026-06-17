"""CLI entry point — main command group."""

from __future__ import annotations

import click

from kb_tools import __version__


@click.group()
@click.version_option(__version__, prog_name="cathkb")
def cli() -> None:
    """Catholic Sovereign Knowledge System — Local-first doctrinal reasoning."""


@cli.command()
@click.argument("query")
@click.option("-k", "--top-k", default=5, help="Number of source chunks to retrieve")
@click.option("--no-context", is_flag=True, help="Show search results only, no LLM")
def query(query: str, top_k: int, no_context: bool) -> None:
    """Ask a doctrinal question and receive a cited answer."""
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel

    from kb_tools.config import load_config
    from kb_tools.search.engine import SearchEngine

    console = Console()
    config = load_config()
    engine = SearchEngine(config)

    if no_context:
        results = engine.search(query, top_k=top_k)
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
        return

    from kb_tools.reasoning.gaps import GapDetector
    from kb_tools.reasoning.generator import Generator

    gap_detector = GapDetector(config)
    if not gap_detector.has_sufficient_sources(query):
        console.print(f"[yellow]{gap_detector.gap_message(query)}[/yellow]")
        return

    context = engine.search_with_context(query, top_k=top_k)
    generator = Generator(config)
    with console.status("[bold green]Generating response via Ollama..."):
        result = generator.generate_with_citations(query, context)

    console.print(Panel(Markdown(result["response"]), title="Response", border_style="green"))
    if result["citations"]:
        console.print(Panel(result["formatted_citations"], title="Citations", border_style="blue"))


@cli.command()
@click.option("-t", "--topic", required=True, help="Topic for the artifact")
@click.option(
    "-t",
    "--type",
    "artifact_type",
    type=click.Choice(["study-guide", "timeline", "comparison", "doctrinal-brief"]),
    default="study-guide",
    help="Type of artifact to generate",
)
def build(topic: str, artifact_type: str) -> None:
    """Generate a study artifact (study guide, timeline, comparison, brief)."""
    from rich.console import Console

    from kb_tools.config import load_config
    from kb_tools.reasoning.artifacts import ArtifactGenerator

    console = Console()
    config = load_config()
    gen = ArtifactGenerator(config)

    with console.status(f"[bold green]Generating {artifact_type} on '{topic}'..."):
        path = gen.generate(topic, artifact_type)
    console.print(f"[bold green]Artifact saved to:[/bold green] {path}")


@cli.command()
@click.option("-p", "--port", default=8080, help="Port for the web server")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
def serve(port: int, host: str) -> None:
    """Start the web UI server."""
    from rich.console import Console

    console = Console()
    console.print(f"[bold green]Starting web server on {host}:{port}...[/bold green]")
    console.print(f"[dim]Open http://{host}:{port} in your browser[/dim]")

    import uvicorn

    uvicorn.run("kb_tools.web.server:app", host=host, port=port, reload=False)


@cli.command()
def build_index() -> None:
    """Rebuild all indexes from kbmd/."""
    from rich.console import Console

    from kb_tools.config import load_config

    console = Console()
    load_config()
    console.print("[bold green]Index rebuild not yet implemented.[/bold green]")
    console.print("Indexes are pre-built in data/kb-index/. Use existing data.")


if __name__ == "__main__":
    cli()
