"""Websocket settlement background tasks."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from time import perf_counter
from typing import Literal
from uuid import uuid4

from app.api.ws_connection import _map_exception, _send, _send_snapshot, _wrap_outbound
from app.config import get_settings
from app.protocol import SettlementBundle, SettlementTaskUpdate, SettleQuarter
from app.repo.protocols import GameSessionRepo, MetaProgressRepo
from app.services import DeathReportService, SettlementOrchestrator

__all__ = ["queue_settlement"]


@dataclass(slots=True)
class _TaskRecord:
    task_id: str
    session_id: str
    quarter_number: int
    player_id: str
    ack_for: str
    queued_at: datetime
    prompt_kind: Literal["settlement", "director", "press_eval", "death_report"] = "settlement"
    started_at: datetime | None = None
    ended_at: datetime | None = None
    retry_count: int = 0


_TASKS: dict[str, _TaskRecord] = {}
_IN_FLIGHT_BY_SESSION: dict[str, str] = {}
_TASK_GUARD = asyncio.Lock()


async def queue_settlement(
    ack_for: str,
    payload: SettleQuarter,
    player_id: str,
    orchestrator: SettlementOrchestrator,
    death_report_service: DeathReportService,
    session_repo: GameSessionRepo,
    meta_repo: MetaProgressRepo,
) -> None:
    task_id = f"SET-{uuid4().hex[:12]}"
    record = _TaskRecord(
        task_id=task_id,
        session_id=payload.session_id,
        quarter_number=payload.quarter_number,
        player_id=player_id,
        ack_for=ack_for,
        queued_at=datetime.now(UTC),
    )
    async with _TASK_GUARD:
        settings = get_settings()
        if len(_IN_FLIGHT_BY_SESSION) >= settings.settlement_queue_max_size:
            await _send(player_id, _task_update(record, "failed", error_type="queue_full"))
            await _send(player_id, _map_exception(SettlementQueueFull(), ack_for))
            return
        existing_task_id = _IN_FLIGHT_BY_SESSION.get(payload.session_id)
        if existing_task_id is not None:
            await _send(
                player_id,
                _task_update(
                    record,
                    "failed",
                    error_type="duplicate_settlement",
                    error_message=f"settlement already running: {existing_task_id}",
                ),
            )
            await _send(player_id, _map_exception(DuplicateSettlementInProgress(), ack_for))
            return
        _TASKS[task_id] = record
        _IN_FLIGHT_BY_SESSION[payload.session_id] = task_id

    await _send(player_id, _task_update(record, "queued"))
    asyncio.create_task(
        _settle_background(
            player_id,
            payload.session_id,
            task_id,
            orchestrator,
            death_report_service,
            session_repo,
            meta_repo,
            ack_for,
        )
    )


async def _settle_background(
    player_id: str,
    session_id: str,
    task_id: str,
    orchestrator: SettlementOrchestrator,
    death_report_service: DeathReportService,
    session_repo: GameSessionRepo,
    meta_repo: MetaProgressRepo,
    ack_for: str,
) -> None:
    start = perf_counter()
    record = _TASKS[task_id]

    async def _status(status: str) -> None:
        if status == "running":
            record.started_at = datetime.now(UTC)
        await _send(player_id, _task_update(record, status))

    try:
        timeout_s = get_settings().settlement_task_timeout_ms / 1000
        result = await asyncio.wait_for(
            orchestrator.settle_quarter(session_id, status_callback=_status),
            timeout=timeout_s,
        )
        bundle = SettlementBundle.from_domain(
            session_id=result.session_id,
            quarter_number=result.quarter_number,
            settlement=result.settlement,
            press_bundle=result.press_bundle,
            new_stats=result.new_stats,
            history_added=result.history_added,
            death=result.death_reason,
            llm_degraded=result.llm_degraded,
        )
        await _send(player_id, _wrap_outbound(bundle, ack_for))
        await _send_snapshot(player_id, session_id, session_repo, meta_repo, ack_for)
        record.retry_count = result.llm_retries
        status = "degraded" if result.llm_degraded else "completed"
        record.ended_at = datetime.now(UTC)
        await _send(player_id, _task_update(record, status, duration_ms=_elapsed_ms(start)))
        if result.death_reason is not None:
            await _run_death_report_task(
                player_id,
                session_id,
                result.quarter_number,
                death_report_service,
                result.death_reason,
                ack_for,
            )
    except TimeoutError:
        record.ended_at = datetime.now(UTC)
        await _send(
            player_id,
            _task_update(
                record,
                "failed",
                duration_ms=_elapsed_ms(start),
                error_type="settlement_timeout",
                error_message="settlement timed out",
            ),
        )
        await _send(player_id, _map_exception(SettlementTaskTimedOut(), ack_for))
    except Exception as exc:  # noqa: BLE001
        record.ended_at = datetime.now(UTC)
        await _send(
            player_id,
            _task_update(
                record,
                "failed",
                duration_ms=_elapsed_ms(start),
                error_type=_error_type(exc),
                error_message=str(exc) or type(exc).__name__,
            ),
        )
        await _send(player_id, _map_exception(exc, ack_for))
    finally:
        async with _TASK_GUARD:
            _IN_FLIGHT_BY_SESSION.pop(session_id, None)


class DuplicateSettlementInProgress(Exception):
    pass


class SettlementQueueFull(Exception):
    pass


class SettlementTaskTimedOut(Exception):
    pass


def _task_update(
    record: _TaskRecord,
    status: str,
    *,
    duration_ms: int | None = None,
    error_type: str | None = None,
    error_message: str | None = None,
):
    return _wrap_outbound(
        SettlementTaskUpdate(
            task_id=record.task_id,
            session_id=record.session_id,
            quarter_number=record.quarter_number,
            prompt_kind=record.prompt_kind,
            status=status,  # type: ignore[arg-type]
            queued_at=record.queued_at,
            started_at=record.started_at,
            ended_at=record.ended_at,
            duration_ms=duration_ms,
            retry_count=record.retry_count,
            error_type=error_type,
            error_message=error_message,
        ),
        record.ack_for,
        type_name="settlement_task_update",
    )


def _elapsed_ms(start: float) -> int:
    return max(0, round((perf_counter() - start) * 1000))


def _error_type(exc: Exception) -> str:
    return getattr(exc, "error_type", type(exc).__name__)


async def _run_death_report_task(
    player_id: str,
    session_id: str,
    quarter_number: int,
    death_report_service: DeathReportService,
    death_reason,
    ack_for: str,
) -> None:
    start = perf_counter()
    record = _TaskRecord(
        task_id=f"DTH-{uuid4().hex[:12]}",
        session_id=session_id,
        quarter_number=quarter_number,
        player_id=player_id,
        ack_for=ack_for,
        queued_at=datetime.now(UTC),
        prompt_kind="death_report",
    )
    await _send(player_id, _task_update(record, "queued"))
    record.started_at = datetime.now(UTC)
    await _send(player_id, _task_update(record, "running"))
    try:
        report = await death_report_service.generate(session_id, death_reason)
        record.retry_count = report.llm_retry_count
        record.ended_at = datetime.now(UTC)
        await _send(player_id, _wrap_outbound(report, ack_for))
        status = "degraded" if report.llm_degraded else "completed"
        await _send(player_id, _task_update(record, status, duration_ms=_elapsed_ms(start)))
    except Exception as exc:  # noqa: BLE001
        record.ended_at = datetime.now(UTC)
        await _send(
            player_id,
            _task_update(
                record,
                "failed",
                duration_ms=_elapsed_ms(start),
                error_type=_error_type(exc),
                error_message=str(exc) or type(exc).__name__,
            ),
        )
        await _send(player_id, _map_exception(exc, ack_for))
