from argus.analysis.discourse_analyzer import DiscourseAnalyzer
from argus.database import SessionLocal, create_database
from argus.services.processing import (
    DISCOURSE_METHOD_VERSION,
    DISCOURSE_STAGE,
)
from argus.storage.discourse_repository import (
    DiscourseAnalysisRepository,
)
from argus.storage.processing_repository import (
    ProcessingStateRepository,
)


def run_discourse_pipeline(
        limit: int = 10,
        retry_failed: bool = False,
) -> None:
    create_database()

    analyzer = DiscourseAnalyzer()
    session = SessionLocal()

    analysis_repository = DiscourseAnalysisRepository(session)
    state_repository = ProcessingStateRepository(session)

    analyzed_count = 0
    failed_count = 0

    try:
        articles = analysis_repository.get_pending_articles(
            method_version=DISCOURSE_METHOD_VERSION,
            limit=limit,
            retry_failed=retry_failed,
        )

        if not articles:
            print("No articles require discourse analysis.")
            return

        for article in articles:
            state = state_repository.get_or_create(
                article_id=article.id,
                stage=DISCOURSE_STAGE,
                method_version=DISCOURSE_METHOD_VERSION,
            )

            print(f"\nAnalyzing: {article.title}")
            state_repository.mark_running(state)

            try:
                metrics = analyzer.analyze(article.content)

                result = analysis_repository.save_result(
                    article_id=article.id,
                    method_version=DISCOURSE_METHOD_VERSION,
                    metrics=metrics,
                )

                state_repository.mark_done(state)
                analyzed_count += 1

                print(f"Analysis ID: {result.id}")
                print(f"Words: {result.word_count}")
                print(f"Sentences: {result.sentence_count}")
                print(
                    "Evidence spans: "
                    f"{len(metrics.evidence)}"
                )

            except Exception as error:
                session.rollback()

                state = state_repository.get_or_create(
                    article_id=article.id,
                    stage=DISCOURSE_STAGE,
                    method_version=DISCOURSE_METHOD_VERSION,
                )

                state_repository.mark_failed(
                    state,
                    error=str(error),
                )

                failed_count += 1

                print(
                    f"Analysis failed for article "
                    f"{article.id}: {error}"
                )

    finally:
        session.close()

    print("\nDiscourse pipeline finished.")
    print(f"Analyzed: {analyzed_count}")
    print(f"Failed: {failed_count}")