import unittest
from unittest.mock import Mock

from sqlalchemy import Integer
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
)

from argus.storage.base_repository import BaseRepository


class TestBase(DeclarativeBase):
    pass


class TestModel(TestBase):
    __tablename__ = "test_models"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )


class BaseRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = Mock(spec=Session)

        self.repository = BaseRepository(
            session=self.session,
            model_type=TestModel,
        )

    def test_get_by_id_uses_configured_model(self) -> None:
        expected = TestModel()
        self.session.get.return_value = expected

        result = self.repository.get_by_id(42)

        self.assertIs(result, expected)
        self.session.get.assert_called_once_with(
            TestModel,
            42,
        )

    def test_add_returns_model_without_commit(self) -> None:
        model = TestModel()

        result = self.repository.add(model)

        self.assertIs(result, model)
        self.session.add.assert_called_once_with(model)
        self.session.commit.assert_not_called()

    def test_add_all_accepts_iterable(self) -> None:
        models = [
            TestModel(),
            TestModel(),
        ]

        self.repository.add_all(
            model for model in models
        )

        self.session.add_all.assert_called_once_with(
            models
        )

    def test_delete_does_not_commit(self) -> None:
        model = TestModel()

        self.repository.delete(model)

        self.session.delete.assert_called_once_with(model)
        self.session.commit.assert_not_called()

    def test_flush_delegates_to_session(self) -> None:
        self.repository.flush()

        self.session.flush.assert_called_once_with()

    def test_refresh_delegates_to_session(self) -> None:
        model = TestModel()

        self.repository.refresh(model)

        self.session.refresh.assert_called_once_with(model)


if __name__ == "__main__":
    unittest.main()