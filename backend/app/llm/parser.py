"""Fault-tolerant parser for raw LLM output."""

from __future__ import annotations

import ast
import json
import logging
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from ._parser_normalize import (
    clamp_metrics_delta,
    normalize_death_report,
    normalize_director,
    normalize_press_eval,
)
from .fallback import STUB_DEATH_REPORT, STUB_DIRECTOR, STUB_PRESS_EVAL
from .schema import DeathReportRaw, DirectorRaw, PressEvalRaw

logger = logging.getLogger(__name__)
T = TypeVar("T")
M = TypeVar("M", bound=BaseModel)


class ParseError(Exception):
    """Base class for LLM output parser failures."""


class ParseSchemaError(ParseError):
    """Raised when extracted JSON cannot be coerced into the target schema."""


class ParseExtractionError(ParseError):
    """Raised when no JSON object can be extracted from raw LLM output."""


def extract_json_block(text: str) -> dict[str, Any] | None:
    """Extract the first JSON-like object from raw model text.

    Handles fenced blocks, leading/trailing prose, and Python-style single-quoted
    dicts. Invalid or non-object payloads return ``None`` instead of raising.
    """

    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None

    candidate = text[start : end + 1]
    for loader in (json.loads, ast.literal_eval):
        try:
            parsed = loader(candidate)
        except (SyntaxError, ValueError, TypeError, json.JSONDecodeError):
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def parse_director(raw_text: str) -> DirectorRaw:
    obj = _extract_or_raise(raw_text)
    try:
        return _validate(DirectorRaw, obj)
    except ParseSchemaError:
        healed = normalize_director(obj, _fallback_obj(STUB_DIRECTOR))
        return _validate(DirectorRaw, healed)


def parse_press_eval(raw_text: str) -> PressEvalRaw:
    obj = _extract_or_raise(raw_text)
    try:
        return _validate(PressEvalRaw, obj)
    except ParseSchemaError:
        healed = normalize_press_eval(obj, _fallback_obj(STUB_PRESS_EVAL))
        return _validate(PressEvalRaw, healed)


def parse_death_report(raw_text: str) -> DeathReportRaw:
    obj = _extract_or_raise(raw_text)
    try:
        return _validate(DeathReportRaw, obj)
    except ParseSchemaError:
        healed = normalize_death_report(obj, _fallback_obj(STUB_DEATH_REPORT))
        return _validate(DeathReportRaw, healed)


def parse_with_fallback(
    parser: Callable[[str], T],
    raw_text: str,
    fallback_stub: str,
    log_context: dict[str, Any],
) -> T:
    try:
        return parser(raw_text)
    except ParseError as first_error:
        logger.warning(
            "LLM output parse failed; retrying deterministic fallback",
            extra={"context": log_context, "error": repr(first_error)},
        )
    except Exception as first_error:
        logger.warning(
            "LLM output parser raised unexpected error; retrying deterministic fallback",
            extra={"context": log_context, "error": repr(first_error)},
        )

    try:
        return parser(fallback_stub)
    except ParseError:
        raise
    except Exception as second_error:
        raise ParseError("fallback parser raised unexpected error") from second_error


def _extract_or_raise(raw_text: str) -> dict[str, Any]:
    try:
        obj = extract_json_block(raw_text)
    except Exception as exc:
        raise ParseExtractionError("failed to extract JSON object") from exc
    if obj is None:
        raise ParseExtractionError("no JSON object found in LLM output")
    return obj


def _validate(model: type[M], obj: dict[str, Any]) -> M:
    try:
        return model.model_validate(obj)
    except ValidationError as exc:
        raise ParseSchemaError(str(exc)) from exc
    except Exception as exc:
        raise ParseSchemaError("schema validation failed") from exc


def _fallback_obj(stub: str) -> dict[str, Any]:
    obj = extract_json_block(stub)
    if obj is None:
        raise ParseSchemaError("fallback stub is not a JSON object")
    return obj


__all__ = (
    "ParseError",
    "ParseExtractionError",
    "ParseSchemaError",
    "clamp_metrics_delta",
    "extract_json_block",
    "parse_death_report",
    "parse_director",
    "parse_press_eval",
    "parse_with_fallback",
)
