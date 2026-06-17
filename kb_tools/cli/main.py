"""CLI entry point — main command group."""

from __future__ import annotations

import sys
import webbrowser
from pathlib import Path

import click

from kb_tools import __version__
from kb_tools.config import Config


def _ensure_data(config: Config) -> bool:
    """Check that knowledge base data exists. Returns True if ready."""
    catalog = config.catalog_path
    embeddings = config.embeddings_dir / "index.bin"
    chunks = config.chunks_dir
    return bool(catalog.exists() and embeddings.exists() and chunks.exists())


def _bootstrap_data(config: Config) -> None:
    """Extract bundled data archive to user data directory if needed."""
    from rich.console import Console

    console = Console()

    data_root = config.data_root

    # If data already exists, nothing to do
    if _ensure_data(config):
        console.print(f"[green]Data found at {data_root}[/green]")
        return

    # Check for bundled data archive (next to binary)
    if getattr(sys, "frozen", False):
        archive = Path(sys.executable).parent / "cathkb-data.tar.gz"
        if not archive.exists():
            archive = Path(sys.executable).parent / "cathkb-data.tar.gz"

        if archive.exists():
            console.print(f"[bold]Extracting data from {archive.name}...[/bold]")
            data_root.mkdir(parents=True, exist_ok=True)
            if archive.suffix == ".gz":
                import tarfile

                with tarfile.open(archive) as tf:
                    tf.extractall(path=data_root.parent)
            else:
                import zipfile

                with zipfile.ZipFile(archive) as zf:
                    zf.extractall(path=data_root.parent)
            console.print(f"[green]Data extracted to {data_root}[/green]")
            return

    # Data missing — give user instructions
    console.print("[bold yellow]Knowledge base data not found.[/bold yellow]")
    console.print()
    console.print("To set up the knowledge base:")
    console.print()
    console.print("  1. Clone the repository:")
    console.print("     git clone https://github.com/YOUR_USER/cathkb.git")
    console.print()
    console.print("  2. Run setup:")
    console.print("     ./setup.sh")
    console.print()
    console.print("  3. Or manually copy the data/ directory to:")
    console.print(f"     {data_root}")
    console.print()
    console.print("For more info: https://github.com/YOUR_USER/cathkb")
    sys.exit(1)


@click.group()
@click.version_option(__version__, prog_name="cathkb")
def cli() -> None:
    """Catholic Sovereign Knowledge System — Local-first doctrinal reasoning."""


@cli.command()
def setup() -> None:
    """Check and bootstrap the knowledge base data."""
    from rich.console import Console

    from kb_tools.config import load_config

    console = Console()
    config = load_config()

    console.print(f"[bold]Data directory:[/bold] {config.data_root}")
    console.print(f"[bold]Catalog:[/bold] {config.catalog_path}")

    if _ensure_data(config):
        catalog_path = config.catalog_path
        import json

        with open(catalog_path) as f:
            catalog = json.load(f)
        n_docs = catalog.get("total_documents", 0)
        console.print(f"[green]Knowledge base ready ({n_docs} documents)[/green]")
    else:
        console.print("[yellow]Knowledge base data not found.[/yellow]")
        _bootstrap_data(config)


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
            console.print(
                Panel(
                    f"[bold]{source}[/bold] — {section} (score: {score:.3f})\n\n{preview}...",
                    title=f"Result {i}",
                )
            )
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
    _bootstrap_data(config)
    gen = ArtifactGenerator(config)

    with console.status(f"[bold green]Generating {artifact_type} on '{topic}'..."):
        path = gen.generate(topic, artifact_type)
    console.print(f"[bold green]Artifact saved to:[/bold green] {path}")


@cli.command()
@click.option("-p", "--port", default=8080, help="Port for the web server")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
def serve(port: int, host: str, no_browser: bool) -> None:
    """Start the web UI server."""
    from rich.console import Console

    from kb_tools.config import load_config

    console = Console()
    config = load_config()
    _bootstrap_data(config)

    console.print(f"[bold green]Starting web server on {host}:{port}...[/bold green]")
    console.print(f"[dim]Open http://{host}:{port} in your browser[/dim]")

    if not no_browser:
        webbrowser.open(f"http://{host}:{port}")

    import uvicorn

    uvicorn.run("kb_tools.web.server:app", host=host, port=port, reload=False)


@cli.command()
def build_index() -> None:
    """Rebuild all indexes from kbmd/."""
    from rich.console import Console

    console = Console()
    console.print("[bold green]Index rebuild not yet implemented.[/bold green]")
    console.print("Indexes are pre-built in data/kb-index/. Use existing data.")


if __name__ == "__main__":
    cli()
