import typer

from argus.services.article_pipeline import run_article_pipeline
from argus.services.discourse_pipeline import run_discourse_pipeline

app = typer.Typer(
    name="argus",
    help="Explainable information-space analysis platform.",
    no_args_is_help=True,
)


@app.command()
def collect(
        parse_limit: int = typer.Option(
            20,
            min=1,
            help="Maximum number of article bodies to extract.",
        ),
) -> None:
    """Collect RSS entries and extract pending article content."""

    run_article_pipeline(parse_limit=parse_limit)


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
    """Run the complete Argus pipeline."""

    run_article_pipeline(parse_limit=parse_limit)
    run_discourse_pipeline(limit=analysis_limit)


if __name__ == "__main__":
    app()