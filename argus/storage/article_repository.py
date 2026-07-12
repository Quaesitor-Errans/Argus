from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sqlalchemy import exists

from argus.models import Article, ProcessingState
from argus.services.processing import (
    FAILED,
    PARSING_METHOD_VERSION,
    PARSING_STAGE,
)


class ArticleRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, article: Article) -> Article:
        self.session.add(article)

        try:
            self.session.commit()
            self.session.refresh(article)
            return article
        except IntegrityError:
            self.session.rollback()
            existing_article = self.get_by_url(article.url)
            if existing_article is None:
                raise
            return existing_article

    def get_by_url(self, url: str) -> Article | None:
        return (
            self.session
            .query(Article)
            .filter(Article.url == url)
            .first()
        )

    def get_latest(self, limit: int = 20) -> list[Article]:
        return (
            self.session
            .query(Article)
            .order_by(Article.fetched_at.desc())
            .limit(limit)
            .all()
        )

    def update_content(self, article: Article, content: str) -> Article:
        article.content = content
        self.session.commit()
        self.session.refresh(article)
        return article

    def get_pending_parsing(
            self,
            limit: int = 20,
            retry_failed: bool = False,
    ) -> list[Article]:
        blocked_statuses = ["running", "done"]

        if not retry_failed:
            blocked_statuses.append("failed")

        blocking_state_exists = exists().where(
            ProcessingState.article_id == Article.id,
            ProcessingState.stage == PARSING_STAGE,
            ProcessingState.method_version == PARSING_METHOD_VERSION,
            ProcessingState.status.in_(blocked_statuses),
            )

        return (
            self.session
            .query(Article)
            .filter(Article.content.is_(None))
            .filter(~blocking_state_exists)
            .order_by(Article.fetched_at.asc())
            .limit(limit)
            .all()
        )

    def get_latest_with_content(self, limit: int = 1) -> list[Article]:
        return (
            self.session
            .query(Article)
            .filter(Article.content.is_not(None))
            .filter(Article.content != "")
            .order_by(Article.fetched_at.desc())
            .limit(limit)
            .all()
        )