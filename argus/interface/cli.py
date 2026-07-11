import typer

from argus.services.collection_service import collect_articles
from argus.services.discourse_pipeline import run_discourse_pipeline
from argus.services.parsing_service import parse_articles

app = typer.Typer(
    name="argus",
    help="Explainable information-space analysis platform.",
    no_args_is_help=True,
)


@app.command()
def collect() -> None:
    """Collect new article metadata from configured sources."""

    collect_articles()


@app.command()
def parse(
        limit: int = typer.Option(
            20,
            min=1,
            help="Maximum number of article bodies to extract.",
        ),
) -> None:
    """Extract full text for stored articles."""

    parse_articles(limit=limit)


@app.command()
def analyze(
        limit: int = typer.Option(
            20,
            min=1,
            help="Maximum number of articles to analyze.",
        ),
) -> None:
    """Run discourse analysis on stored articles."""

    run_discourse_pipeline(limit=limit)


@app.command()
def run(
        parse_limit: int = typer.Option(20, min=1),
        analysis_limit: int = typer.Option(20, min=1),
) -> None:
    """Run collection, parsing and discourse analysis."""

    collect_articles()
    parse_articles(limit=parse_limit)
    run_discourse_pipeline(limit=analysis_limit)


if __name__ == "__main__":
    app()