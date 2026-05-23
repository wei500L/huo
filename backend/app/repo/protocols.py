"""Repository interfaces and environment-aware factories."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from app import config as config_module
from app.domain import (
    Company,
    DeathLogEntry,
    Employee,
    HistoryEntry,
    MemoryEntry,
    MemoryWindow,
    MetaProgress,
    PressBundle,
    Promise,
    Quarter,
    ScheduledEvent,
    Stats,
)

logger = logging.getLogger(__name__)

__all__ = (
    "AgentMemoryRepo",
    "GameSession",
    "GameSessionRepo",
    "MetaProgressRepo",
    "PressArchiveRepo",
    "get_agent_memory_repo",
    "get_meta_repo",
    "get_press_archive_repo",
    "get_session_repo",
)


class GameSession(BaseModel):
    """Aggregate root consumed by services."""

    model_config = ConfigDict(strict=True)

    id: str
    player_id: str
    company: Company
    stats: Stats
    quarter: Quarter
    employees: list[Employee]
    history: list[HistoryEntry] = Field(default_factory=list)
    promise_log: list[Promise] = Field(default_factory=list)
    agent_memory: MemoryWindow = Field(default_factory=lambda: MemoryWindow(entries=[]))
    scheduled_events: list[ScheduledEvent] = Field(default_factory=list)
    status: Literal["active", "dead", "won"] = "active"
    created_at: datetime
    updated_at: datetime


@runtime_checkable
class GameSessionRepo(Protocol):
    async def create(self, session: GameSession) -> GameSession:
        ...

    async def get(self, session_id: str) -> GameSession | None:
        ...

    async def save(self, session: GameSession) -> GameSession:
        ...

    async def list_by_player(self, player_id: str, limit: int = 20) -> list[GameSession]:
        ...

    async def delete(self, session_id: str) -> bool:
        ...


@runtime_checkable
class MetaProgressRepo(Protocol):
    async def get(self, player_id: str) -> MetaProgress:
        ...

    async def save(self, meta: MetaProgress) -> MetaProgress:
        ...

    async def list_recent_deaths(self, player_id: str, limit: int = 10) -> list[DeathLogEntry]:
        ...


@runtime_checkable
class PressArchiveRepo(Protocol):
    async def append(self, session_id: str, bundle: PressBundle) -> str:
        ...

    async def get(self, archive_id: str) -> PressBundle | None:
        ...

    async def list_by_session(self, session_id: str) -> list[PressBundle]:
        ...


@runtime_checkable
class AgentMemoryRepo(Protocol):
    async def append(self, player_id: str, session_id: str, entry: MemoryEntry) -> None:
        ...

    async def fetch_window(self, player_id: str, max_size: int = 6) -> MemoryWindow:
        ...


def _use_memory_repo() -> bool:
    return config_module.get_settings().env in {"dev", "test"}


def _warn_sql_stub(repo_name: str) -> None:
    logger.warning("%s requested in prod; returning SQL stub placeholder", repo_name)


def get_session_repo() -> GameSessionRepo:
    if _use_memory_repo():
        from .memory_impl import get_session_repo as get_memory_session_repo

        return get_memory_session_repo()
    from .sql_stub import SqlGameSessionRepo

    _warn_sql_stub("GameSessionRepo")
    return SqlGameSessionRepo()


def get_meta_repo() -> MetaProgressRepo:
    if _use_memory_repo():
        from .memory_impl import get_meta_repo as get_memory_meta_repo

        return get_memory_meta_repo()
    from .sql_stub import SqlMetaProgressRepo

    _warn_sql_stub("MetaProgressRepo")
    return SqlMetaProgressRepo()


def get_press_archive_repo() -> PressArchiveRepo:
    if _use_memory_repo():
        from .memory_impl import get_press_archive_repo as get_memory_press_repo

        return get_memory_press_repo()
    from .sql_stub import SqlPressArchiveRepo

    _warn_sql_stub("PressArchiveRepo")
    return SqlPressArchiveRepo()


def get_agent_memory_repo() -> AgentMemoryRepo:
    if _use_memory_repo():
        from .memory_impl import get_agent_memory_repo as get_memory_agent_repo

        return get_memory_agent_repo()
    from .sql_stub import SqlAgentMemoryRepo

    _warn_sql_stub("AgentMemoryRepo")
    return SqlAgentMemoryRepo()
