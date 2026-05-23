"""In-memory repository implementations for v1."""

from __future__ import annotations

import asyncio
from datetime import datetime
from uuid import uuid4

from app.domain import DeathLogEntry, MemoryEntry, MemoryWindow, MetaProgress, PressBundle

from .protocols import (
    AgentMemoryRepo,
    GameSession,
    GameSessionRepo,
    MetaProgressRepo,
    PressArchiveRepo,
)

__all__ = (
    "InMemoryAgentMemoryRepo",
    "InMemoryGameSessionRepo",
    "InMemoryMetaProgressRepo",
    "InMemoryPressArchiveRepo",
    "get_agent_memory_repo",
    "get_meta_repo",
    "get_press_archive_repo",
    "get_session_repo",
)


class InMemoryGameSessionRepo(GameSessionRepo):
    def __init__(self) -> None:
        self._data: dict[str, GameSession] = {}
        self._lock = asyncio.Lock()

    async def create(self, session: GameSession) -> GameSession:
        async with self._lock:
            stored = session.model_copy(deep=True)
            self._data[stored.id] = stored
            return stored.model_copy(deep=True)

    async def get(self, session_id: str) -> GameSession | None:
        async with self._lock:
            session = self._data.get(session_id)
            return None if session is None else session.model_copy(deep=True)

    async def save(self, session: GameSession) -> GameSession:
        stored = session.model_copy(update={"updated_at": datetime.utcnow()}, deep=True)
        async with self._lock:
            self._data[stored.id] = stored
        return stored.model_copy(deep=True)

    async def list_by_player(self, player_id: str, limit: int = 20) -> list[GameSession]:
        if limit <= 0:
            return []
        async with self._lock:
            sessions = [
                session.model_copy(deep=True)
                for session in self._data.values()
                if session.player_id == player_id
            ]
        sessions.sort(key=lambda item: (item.updated_at, item.created_at), reverse=True)
        return sessions[:limit]

    async def delete(self, session_id: str) -> bool:
        async with self._lock:
            return self._data.pop(session_id, None) is not None


class InMemoryMetaProgressRepo(MetaProgressRepo):
    def __init__(self) -> None:
        self._data: dict[str, MetaProgress] = {}
        self._lock = asyncio.Lock()

    async def get(self, player_id: str) -> MetaProgress:
        async with self._lock:
            meta = self._data.get(player_id)
            if meta is None:
                meta = MetaProgress(player_id=player_id)
                self._data[player_id] = meta
            return meta.model_copy(deep=True)

    async def save(self, meta: MetaProgress) -> MetaProgress:
        stored = meta.model_copy(deep=True)
        async with self._lock:
            self._data[stored.player_id] = stored
        return stored.model_copy(deep=True)

    async def list_recent_deaths(self, player_id: str, limit: int = 10) -> list[DeathLogEntry]:
        if limit <= 0:
            return []
        async with self._lock:
            meta = self._data.get(player_id)
            if meta is None:
                return []
            deaths = list(meta.death_log)
        deaths.sort(key=lambda item: item.died_at_quarter, reverse=True)
        return [death.model_copy(deep=True) for death in deaths[:limit]]


class InMemoryPressArchiveRepo(PressArchiveRepo):
    def __init__(self) -> None:
        self._bundles: dict[str, PressBundle] = {}
        self._session_index: dict[str, list[str]] = {}
        self._lock = asyncio.Lock()

    async def append(self, session_id: str, bundle: PressBundle) -> str:
        archive_id = f"P-{uuid4().hex[:10]}"
        async with self._lock:
            self._bundles[archive_id] = bundle.model_copy(deep=True)
            self._session_index.setdefault(session_id, []).append(archive_id)
        return archive_id

    async def get(self, archive_id: str) -> PressBundle | None:
        async with self._lock:
            bundle = self._bundles.get(archive_id)
            return None if bundle is None else bundle.model_copy(deep=True)

    async def list_by_session(self, session_id: str) -> list[PressBundle]:
        async with self._lock:
            archive_ids = list(self._session_index.get(session_id, []))
            bundles = [
                self._bundles[archive_id].model_copy(deep=True)
                for archive_id in archive_ids
            ]
        return bundles


class InMemoryAgentMemoryRepo(AgentMemoryRepo):
    def __init__(self) -> None:
        self._data: dict[str, list[MemoryEntry]] = {}
        self._lock = asyncio.Lock()

    async def append(self, player_id: str, session_id: str, entry: MemoryEntry) -> None:
        async with self._lock:
            self._data.setdefault(player_id, []).append(entry.model_copy(deep=True))

    async def fetch_window(self, player_id: str, max_size: int = 6) -> MemoryWindow:
        async with self._lock:
            entries = [entry.model_copy(deep=True) for entry in self._data.get(player_id, [])]
        window = MemoryWindow(entries=[], max_size=max_size)
        for entry in entries:
            window = window.append(entry)
        return window


_session_singleton = InMemoryGameSessionRepo()
_meta_singleton = InMemoryMetaProgressRepo()
_press_singleton = InMemoryPressArchiveRepo()
_agent_singleton = InMemoryAgentMemoryRepo()


def get_session_repo() -> InMemoryGameSessionRepo:
    return _session_singleton


def get_meta_repo() -> InMemoryMetaProgressRepo:
    return _meta_singleton


def get_press_archive_repo() -> InMemoryPressArchiveRepo:
    return _press_singleton


def get_agent_memory_repo() -> InMemoryAgentMemoryRepo:
    return _agent_singleton
