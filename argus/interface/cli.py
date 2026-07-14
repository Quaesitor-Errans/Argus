import typer

from argus.services.collection_service import collect_articles
from argus.services.discourse_pipeline import run_discourse_pipeline
from argus.services.parsing_service import parse_articles
from argus.storage.migrations import upgrade_database

app = typer.Typer(
    name="argus",
    help="Explainable information-space analysis platform.",
    no_args_is_help=True,
)

@app.callback()
def initialize_database() -> None:
    """Apply pending database migrations before running a command."""

    upgrade_database()

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
        retry_failed: bool = typer.Option(
            False,
            "--retry-failed",
            help="Retry articles whose previous parsing attempt failed.",
        ),
) -> None:
    """Extract full text for stored articles."""

    parse_articles(
        limit=limit,
        retry_failed=retry_failed,
    )


@app.command()
def analyze(
        limit: int = typer.Option(
            20,
            min=1,
            help="Maximum number of articles to analyze.",
        ),
        retry_failed: bool = typer.Option(
            False,
            "--retry-failed",
            help="Retry articles whose previous analysis attempt failed.",
        ),
) -> None:
    """Run discourse analysis on stored articles."""

    run_discourse_pipeline(
        limit=limit,
        retry_failed=retry_failed,
    )


@app.command()
def run(
        parse_limit: int = typer.Option(
            20,
            min=1,
            help="Maximum number of article bodies to extract.",
        ),
        analysis_limit: int = typer.Option(
            20,
            min=1,
            help="Maximum number of articles to analyze.",
        ),
        retry_failed: bool = typer.Option(
            False,
            "--retry-failed",
            help="Retry failed parsing and analysis operations.",
        ),
) -> None:
    """Run collection, parsing and discourse analysis."""

    collect_articles()

    parse_articles(
        limit=parse_limit,
        retry_failed=retry_failed,
    )

    run_discourse_pipeline(
        limit=analysis_limit,
        retry_failed=retry_failed,
    )


if __name__ == "__main__":
    app()