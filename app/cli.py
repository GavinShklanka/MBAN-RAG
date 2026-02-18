import typer
from app.rag.vanilla import run_vanilla_rag
from app.rag.agentic import run_agentic_rag

app = typer.Typer(no_args_is_help=True)

@app.command()
def vanilla(
    question: str = typer.Option(..., "--question"),
    location: str = typer.Option("", "--location"),
    radius_km: int = typer.Option(10, "--radius-km"),
    max_topics: int = typer.Option(5, "--max-topics"),
    max_pages: int = typer.Option(5, "--max-pages"),
    max_chunks: int = typer.Option(10, "--max-chunks"),
max_context_chunks: int = typer.Option(8, "--max-context-chunks"),

):
    out = run_vanilla_rag(question, max_topics=max_topics, max_pages=max_pages, max_chunks=max_chunks)
    typer.echo("\n=== VANILLA RAG ===\n")
    typer.echo("Retrieved sources:")
    for s in out["retrieved_sources"]:
        typer.echo(f"- {s}")
    typer.echo("\nAnswer:\n")
    typer.echo(out["answer"])

@app.command()
def agentic(
    question: str = typer.Option(..., "--question"),
    location: str = typer.Option("", "--location"),
    radius_km: int = typer.Option(10, "--radius-km"),
    max_topics: int = typer.Option(5, "--max-topics"),
    max_pages: int = typer.Option(5, "--max-pages"),
    max_chunks: int = typer.Option(10, "--max-chunks"),
max_context_chunks: int = typer.Option(8, "--max-context-chunks"),
):
    out = run_agentic_rag(question, location=location, max_topics=max_topics, max_pages=max_pages, max_chunks=max_chunks)
    typer.echo("\n=== AGENTIC RAG ===\n")
    typer.echo(out["answer"])

if __name__ == "__main__":
    app()
