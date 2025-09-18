"""SQLAlchemy-powered database utilities for synchronous access."""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterable, Mapping, Sequence, Type, TypeVar
from venv import logger

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Result
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import ClauseElement
from pydantic import BaseModel

load_dotenv()

TModel = TypeVar("TModel", bound=BaseModel)


class DatabaseError(RuntimeError):
    """Raised when a database operation fails."""


def _replace_placeholders(query: str, params: Sequence[Any]) -> tuple[str, dict[str, Any]]:
    new_query = query
    bound_params: dict[str, Any] = {}
    for index, value in enumerate(params):
        key = f"param_{index}"
        if "?" not in new_query:
            raise DatabaseError("Mismatch between placeholders and parameters in query: %s" % query)
        new_query = new_query.replace("?", f":{key}", 1)
        bound_params[key] = value
    return new_query, bound_params


def _prepare(
    query: str | ClauseElement,
    params: Sequence[Any] | Mapping[str, Any] | None,
) -> tuple[str | ClauseElement, dict[str, Any]]:
    if isinstance(query, ClauseElement):
        if params is None:
            return query, {}
        if isinstance(params, Mapping):
            return query, dict(params)
        raise DatabaseError("SQLAlchemy expressions only accept mapping-style parameters")
    if params is None:
        return query, {}
    if isinstance(params, Mapping):
        return query, dict(params)
    if isinstance(params, (list, tuple)):
        return _replace_placeholders(query, list(params))
    raise DatabaseError(f"Unsupported parameter type: {type(params)!r}")


class Database:
    """Utility wrapper around SQLAlchemy sessions with Pydantic integration."""

    def __init__(self, database_url: str | None = None) -> None:
        url = os.getenv("DATABASE_URL")
        logger.info(f"Connecting to database at {url}")
        self._engine: Engine = create_engine(url, future=True)
        self._Session = sessionmaker(bind=self._engine, autoflush=False, autocommit=False, future=True)

    @contextmanager
    def session(self) -> Session:
        logger.debug("Opening new database session")
        session: Session = self._Session()
        try:
            yield session  # type: ignore
            session.commit()
        except Exception as exc:  # noqa: BLE001
            session.rollback()
            raise DatabaseError(str(exc)) from exc
        finally:
            session.close()

    def _execute(
        self,
        query: str | ClauseElement,
        params: Sequence[Any] | Mapping[str, Any] | None = None,
    ) -> Result:
        prepared_query, bound = _prepare(query, params)
        with self.session() as session:
            if isinstance(prepared_query, ClauseElement):
                result = session.execute(prepared_query, bound)
            else:
                result = session.execute(text(prepared_query), bound)
            return result

    def execute(
        self,
        query: str | ClauseElement,
        params: Sequence[Any] | Mapping[str, Any] | None = None,
    ) -> Any:
        result = self._execute(query, params)
        try:
            return result.lastrowid  # type: ignore
        except AttributeError:
            return result.rowcount  # type: ignore

    def executemany(self, query: str, param_list: Iterable[Sequence[Any] | Mapping[str, Any]]) -> None:
        iterator = iter(param_list)
        try:
            first = next(iterator)
        except StopIteration:
            return

        # Prepare statement using the first parameter set and reuse for the rest.
        base_query, bound_first = _prepare(query, first)
        remaining = []
        for params in iterator:
            _, bound = _prepare(query, params)
            remaining.append(bound)

        with self.session() as session:
            if isinstance(base_query, ClauseElement):
                session.execute(base_query, bound_first)
                for bound in remaining:
                    session.execute(base_query, bound)
            else:
                session.execute(text(base_query), bound_first)
                for bound in remaining:
                    session.execute(text(base_query), bound)

    def fetch_one(
        self,
        query: str | ClauseElement,
        params: Sequence[Any] | Mapping[str, Any] | None = None,
        model: Type[TModel] | None = None,
    ) -> TModel | dict[str, Any] | None:
        prepared_query, bound = _prepare(query, params)
        with self.session() as session:
            if isinstance(prepared_query, ClauseElement):
                result = session.execute(prepared_query, bound).mappings().first()
            else:
                result = session.execute(text(prepared_query), bound).mappings().first()
        if result is None:
            return None
        data = dict(result)
        return model.model_validate(data) if model else data

    def fetch_all(
        self,
        query: str | ClauseElement,
        params: Sequence[Any] | Mapping[str, Any] | None = None,
        model: Type[TModel] | None = None,
    ) -> list[TModel] | list[dict[str, Any]]:
        prepared_query, bound = _prepare(query, params)
        with self.session() as session:
            if isinstance(prepared_query, ClauseElement):
                result = session.execute(prepared_query, bound).mappings().all()
            else:
                result = session.execute(text(prepared_query), bound).mappings().all()
        data = [dict(row) for row in result]
        if model:
            return [model.model_validate(item) for item in data]
        return data

    def fetchall(
        self,
        query: str | ClauseElement,
        params: Sequence[Any] | Mapping[str, Any] | None = None,
    ) -> list[Any]:
        prepared_query, bound = _prepare(query, params)
        with self.session() as session:
            if isinstance(prepared_query, ClauseElement):
                result = session.execute(prepared_query, bound).all()
            else:
                result = session.execute(text(prepared_query), bound).all()
        return [row[0] for row in result]

    def fetchall_multiple(
        self,
        query: str | ClauseElement,
        params: Sequence[Any] | Mapping[str, Any] | None = None,
    ) -> list[tuple[Any, ...]]:
        prepared_query, bound = _prepare(query, params)
        with self.session() as session:
            if isinstance(prepared_query, ClauseElement):
                result = session.execute(prepared_query, bound).all()
            else:
                result = session.execute(text(prepared_query), bound).all()
        return [tuple(row) for row in result]

    def fetch_column(
        self,
        query: str | ClauseElement,
        params: Sequence[Any] | Mapping[str, Any] | None = None,
    ) -> list[Any]:
        prepared_query, bound = _prepare(query, params)
        with self.session() as session:
            if isinstance(prepared_query, ClauseElement):
                result = session.execute(prepared_query, bound).scalars().all()
            else:
                result = session.execute(text(prepared_query), bound).scalars().all()
        return list(result)

    def last_added_id(self, idt: Any) -> Any:
        values = self.fetch_column(
            "SELECT id FROM tasks WHERE idt=? ORDER BY id",
            (idt,),
        )
        return values[-1] if values else None


# Shared database instance for the application.
database = Database()
