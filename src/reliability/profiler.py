"""Lightweight profiling for tabular reliability analysis."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any


def profile_rows(rows: Iterable[Mapping[str, Any]], *, dataset_name: str, source: str, freshness_column: str | None = None) -> dict[str, Any]:
    """Return deterministic, JSON-friendly profiling metrics for a dataset."""
    rows = list(rows)
    columns = list(rows[0].keys()) if rows else []
    profile = {"dataset_name": dataset_name, "source": source, "row_count": len(rows), "column_count": len(columns), "columns": {}, "duplicate_row_count": _duplicate_row_count(rows)}
    for column in columns:
        values = [row.get(column) for row in rows]
        non_null = [v for v in values if not _is_missing(v)]
        metrics = {"dtype": _infer_dtype(non_null), "null_count": len(values)-len(non_null), "null_percentage": _percentage(len(values)-len(non_null), len(values)), "unique_count": len(_hashable_values(non_null))}
        numeric = _numeric_values(non_null)
        if numeric:
            metrics["min"], metrics["max"] = min(numeric), max(numeric)
        profile["columns"][column] = metrics
    if freshness_column:
        profile["freshness"] = _profile_freshness(rows, freshness_column)
    return profile


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _percentage(count: int, total: int) -> float:
    return round(count / total * 100, 2) if total else 0.0


def _infer_dtype(values: list[Any]) -> str:
    if not values: return "unknown"
    if all(_is_bool(v) for v in values): return "boolean"
    if all(_is_integer(v) for v in values): return "integer"
    if all(_is_number(v) for v in values): return "number"
    if all(_is_date(v) for v in values): return "date"
    return "string"


def _is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def _is_integer(value: Any) -> bool:
    if isinstance(value, bool): return False
    if isinstance(value, int): return True
    if isinstance(value, str):
        try: return float(value).is_integer()
        except ValueError: return False
    return False


def _is_number(value: Any) -> bool:
    if isinstance(value, bool): return False
    try: float(value); return True
    except (TypeError, ValueError): return False


def _is_date(value: Any) -> bool:
    if isinstance(value, datetime): return True
    if not isinstance(value, str): return False
    try: datetime.fromisoformat(value); return True
    except ValueError: return False


def _numeric_values(values: list[Any]) -> list[float | int]:
    if not values or not all(_is_number(v) for v in values): return []
    converted = [float(v) for v in values]
    return [int(v) for v in converted] if all(v.is_integer() for v in converted) else converted


def _hashable_values(values: list[Any]) -> set[Any]:
    return {v if isinstance(v, (str, int, float, bool, type(None))) else repr(v) for v in values}


def _duplicate_row_count(rows: list[Mapping[str, Any]]) -> int:
    seen, duplicates = set(), 0
    for row in rows:
        key = tuple((column, repr(value)) for column, value in row.items())
        if key in seen: duplicates += 1
        else: seen.add(key)
    return duplicates


def _profile_freshness(rows: list[Mapping[str, Any]], column: str) -> dict[str, Any]:
    dates, invalid_count = [], 0
    for row in rows:
        value = row.get(column)
        if _is_missing(value): continue
        try: dates.append(datetime.fromisoformat(str(value)))
        except ValueError: invalid_count += 1
    result = {"column": column, "invalid_date_count": invalid_count}
    if dates:
        result["min_date"], result["max_date"] = min(dates).date().isoformat(), max(dates).date().isoformat()
    return result
