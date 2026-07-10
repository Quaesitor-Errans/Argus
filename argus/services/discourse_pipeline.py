from argus.analysis.discourse_analyzer import DiscourseAnalyzer
from argus.database import SessionLocal, create_database
from argus.storage.discourse_repository import (
    DiscourseAnalysisRepository,
)

DISCOURSE_METHOD_VERSION = "lexical-en-v0.1"


def run_discourse_pipeline(limit: int = 10) -> None:
    create_database()

    analyzer = DiscourseAnalyzer()
    session = SessionLocal()
    repository = DiscourseAnalysisRepository(session)

    analyzed_count = 0
    failed_count = 0

    try:
        articles = repository.get_articles_without_analysis(
            method_version=DISCOURSE_METHOD_VERSION,
            limit=limit,
        )

        if not articles:
            print("No articles require discourse analysis.")
            return

        for article in articles:
            print(f"\nAnalyzing: {article.title}")

            try:
                metrics = analyzer.analyze(article.content)

                result = repository.save_result(
                    article_id=article.id,
                    method_version=DISCOURSE_METHOD_VERSION,
                    metrics=metrics,
                )

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