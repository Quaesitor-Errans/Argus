from argus.database import SessionLocal, create_database
from argus.logging.logger import get_logger
from argus.parsers.article_parser import extract_article_text
from argus.services.processing import (
    PARSING_METHOD_VERSION,
    PARSING_STAGE,
)
from argus.storage.article_repository import ArticleRepository
from argus.storage.processing_repository import (
    ProcessingStateRepository,
)


logger = get_logger(__name__)


def parse_articles(
        limit: int = 20,
        retry_failed: bool = False,
) -> None:
    create_database()

    session = SessionLocal()
    article_repository = ArticleRepository(session)
    state_repository = ProcessingStateRepository(session)

    parsed_count = 0
    failed_count = 0

    try:
        articles = article_repository.get_pending_parsing(
            limit=limit,
            retry_failed=retry_failed,
        )

        if not articles:
            logger.info(
                "No articles require parsing."
            )
            return

        for article in articles:
            state = state_repository.get_or_create(
                article_id=article.id,
                stage=PARSING_STAGE,
                method_version=PARSING_METHOD_VERSION,
            )

            logger.info(
                "Parsing article %s: %s",
                article.id,
                article.title,
            )

            state_repository.mark_running(state)

            try:
                content = extract_article_text(
                    article.url
                )

                if not content:
                    raise RuntimeError(
                        "Article parser returned no content."
                    )

                article_repository.update_content(
                    article,
                    content,
                )

                state_repository.mark_done(state)

                parsed_count += 1

                logger.info(
                    "Article parsed: id=%s; characters=%s",
                    article.id,
                    len(content),
                )

            except Exception as error:
                session.rollback()

                state = state_repository.get_or_create(
                    article_id=article.id,
                    stage=PARSING_STAGE,
                    method_version=PARSING_METHOD_VERSION,
                )

                state_repository.mark_failed(
                    state,
                    error=str(error),
                )

                failed_count += 1

                logger.exception(
                    "Article parsing failed: id=%s; url=%s",
                    article.id,
                    article.url,
                )

    finally:
        session.close()

    logger.info(
        "Parsing finished; parsed=%s; failed=%s",
        parsed_count,
        failed_count,
    )