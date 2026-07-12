from argus.analysis.discourse_analyzer import DiscourseAnalyzer
from argus.database import SessionLocal, create_database
from argus.logging.logger import get_logger
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


logger = get_logger(__name__)


def run_discourse_pipeline(
        limit: int = 10,
        retry_failed: bool = False,
) -> None:
    create_database()

    analyzer = DiscourseAnalyzer()
    session = SessionLocal()

    analysis_repository = DiscourseAnalysisRepository(
        session
    )
    state_repository = ProcessingStateRepository(
        session
    )

    analyzed_count = 0
    failed_count = 0

    try:
        articles = (
            analysis_repository.get_pending_articles(
                method_version=DISCOURSE_METHOD_VERSION,
                limit=limit,
                retry_failed=retry_failed,
            )
        )

        if not articles:
            logger.info(
                "No articles require discourse analysis."
            )
            return

        for article in articles:
            state = state_repository.get_or_create(
                article_id=article.id,
                stage=DISCOURSE_STAGE,
                method_version=DISCOURSE_METHOD_VERSION,
            )

            logger.info(
                "Analyzing article %s: %s",
                article.id,
                article.title,
            )

            state_repository.mark_running(state)

            try:
                metrics = analyzer.analyze(
                    article.content
                )

                result = analysis_repository.save_result(
                    article_id=article.id,
                    method_version=(
                        DISCOURSE_METHOD_VERSION
                    ),
                    metrics=metrics,
                )

                state_repository.mark_done(state)
                analyzed_count += 1

                logger.info(
                    (
                        "Analysis completed: "
                        "article_id=%s; result_id=%s; "
                        "words=%s; sentences=%s; "
                        "evidence=%s"
                    ),
                    article.id,
                    result.id,
                    result.word_count,
                    result.sentence_count,
                    len(metrics.evidence),
                )

            except Exception as error:
                session.rollback()

                state = state_repository.get_or_create(
                    article_id=article.id,
                    stage=DISCOURSE_STAGE,
                    method_version=(
                        DISCOURSE_METHOD_VERSION
                    ),
                )

                state_repository.mark_failed(
                    state,
                    error=str(error),
                )

                failed_count += 1

                logger.exception(
                    "Discourse analysis failed: article_id=%s",
                    article.id,
                )

    finally:
        session.close()

    logger.info(
        (
            "Discourse analysis finished; "
            "analyzed=%s; failed=%s"
        ),
        analyzed_count,
        failed_count,
    )