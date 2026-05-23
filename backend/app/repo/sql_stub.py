"""SQLAlchemy ORM skeletons and SQL repo placeholders."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.domain import DeathLogEntry, MemoryEntry, MemoryWindow, MetaProgress, PressBundle

from .protocols import (
    AgentMemoryRepo,
    GameSession,
    GameSessionRepo,
    MetaProgressRepo,
    PressArchiveRepo,
)

__all__ = (
    "AgentMemoryORM",
    "GameSessionORM",
    "MetaProgressORM",
    "PressArchiveORM",
    "SqlAgentMemoryRepo",
    "SqlGameSessionRepo",
    "SqlMetaProgressRepo",
    "SqlPressArchiveRepo",
    "Base",
)

SQL_REPO_ERROR = "SQL repo not implemented in v1; see migration_plan.md"


class Base(DeclarativeBase):
    pass


class GameSessionORM(Base):
    __tablename__ = "game_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    player_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    company_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    stats_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    quarter_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(8), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class MetaProgressORM(Base):
    __tablename__ = "meta_progress"

    player_id: Mapped[str] = mapped_column(String, primary_key=True)
    data_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    total_runs: Mapped[int] = mapped_column(Integer, nullable=False)


class PressArchiveORM(Base):
    __tablename__ = "press_archive"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("game_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    bundle_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class AgentMemoryORM(Base):
    __tablename__ = "agent_memory"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    player_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    entry_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)


class SqlGameSessionRepo(GameSessionRepo):
    async def create(self, session: GameSession) -> GameSession:
        raise NotImplementedError(SQL_REPO_ERROR)

    async def get(self, session_id: str) -> GameSession | None:
        raise NotImplementedError(SQL_REPO_ERROR)

    async def save(self, session: GameSession) -> GameSession:
        raise NotImplementedError(SQL_REPO_ERROR)

    async def list_by_player(self, player_id: str, limit: int = 20) -> list[GameSession]:
        raise NotImplementedError(SQL_REPO_ERROR)

    async def delete(self, session_id: str) -> bool:
        raise NotImplementedError(SQL_REPO_ERROR)


class SqlMetaProgressRepo(MetaProgressRepo):
    async def get(self, player_id: str) -> MetaProgress:
        raise NotImplementedError(SQL_REPO_ERROR)

    async def save(self, meta: MetaProgress) -> MetaProgress:
        raise NotImplementedError(SQL_REPO_ERROR)

    async def list_recent_deaths(self, player_id: str, limit: int = 10) -> list[DeathLogEntry]:
        raise NotImplementedError(SQL_REPO_ERROR)


class SqlPressArchiveRepo(PressArchiveRepo):
    async def append(self, session_id: str, bundle: PressBundle) -> str:
        raise NotImplementedError(SQL_REPO_ERROR)

    async def get(self, archive_id: str) -> PressBundle | None:
        raise NotImplementedError(SQL_REPO_ERROR)

    async def list_by_session(self, session_id: str) -> list[PressBundle]:
        raise NotImplementedError(SQL_REPO_ERROR)


class SqlAgentMemoryRepo(AgentMemoryRepo):
    async def append(self, player_id: str, session_id: str, entry: MemoryEntry) -> None:
        raise NotImplementedError(SQL_REPO_ERROR)

    async def fetch_window(self, player_id: str, max_size: int = 6) -> MemoryWindow:
        raise NotImplementedError(SQL_REPO_ERROR)
