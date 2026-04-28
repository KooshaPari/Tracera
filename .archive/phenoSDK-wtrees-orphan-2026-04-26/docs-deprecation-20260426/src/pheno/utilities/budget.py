"""
Budget management utilities shared across SDK consumers.
"""

from __future__ import annotations

import calendar
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True, slots=True)
class BudgetLimit:
    """
    Defines spending limits for a given entity.
    """

    daily_limit_usd: float
    monthly_limit_usd: float
    total_limit_usd: float | None = None
    alert_threshold_percent: float = 80.0


@dataclass(slots=True)
class BudgetUsage:
    """
    Tracks usage within the configured windows.
    """

    daily_spent_usd: float
    monthly_spent_usd: float
    total_spent_usd: float
    daily_reset_time: float
    monthly_reset_time: float
    last_alert_time: float | None = None


class BudgetManager:
    """
    In-memory budget tracker with daily/monthly windows.
    """

    def __init__(self, clock: callable = time.time) -> None:
        self._clock = clock
        self._limits: dict[str, BudgetLimit] = {}
        self._usage: dict[str, BudgetUsage] = {}

    def configure(self, key: str, limit: BudgetLimit) -> None:
        self._limits[key] = limit
        if key not in self._usage:
            now = self._clock()
            self._usage[key] = BudgetUsage(
                daily_spent_usd=0.0,
                monthly_spent_usd=0.0,
                total_spent_usd=0.0,
                daily_reset_time=self._next_day(now),
                monthly_reset_time=self._next_month(now),
            )

    def check(self, key: str, estimated_cost_usd: float) -> tuple[bool, str | None]:
        limit = self._limits.get(key)
        if limit is None:
            raise ValueError(f"Budget limit not configured for key: {key}")

        usage = self._ensure_usage(key)
        self._reset_if_needed(key)

        if usage.daily_spent_usd + estimated_cost_usd > limit.daily_limit_usd:
            return False, "daily_limit_exceeded"
        if usage.monthly_spent_usd + estimated_cost_usd > limit.monthly_limit_usd:
            return False, "monthly_limit_exceeded"
        if limit.total_limit_usd is not None:
            if usage.total_spent_usd + estimated_cost_usd > limit.total_limit_usd:
                return False, "total_limit_exceeded"
        self._check_alert_threshold(key, estimated_cost_usd)
        return True, None

    def record(self, key: str, actual_cost_usd: float) -> None:
        self._ensure_usage(key)
        self._reset_if_needed(key)
        usage = self._usage[key]
        usage.daily_spent_usd += actual_cost_usd
        usage.monthly_spent_usd += actual_cost_usd
        usage.total_spent_usd += actual_cost_usd

    def remaining(self, key: str) -> dict[str, float]:
        limit = self._limits.get(key)
        if limit is None:
            raise ValueError(f"Budget limit not configured for key: {key}")

        usage = self._ensure_usage(key)
        self._reset_if_needed(key)

        result = {
            "daily_remaining": max(0.0, limit.daily_limit_usd - usage.daily_spent_usd),
            "monthly_remaining": max(0.0, limit.monthly_limit_usd - usage.monthly_spent_usd),
            "total_remaining": float("inf"),
        }
        if limit.total_limit_usd is not None:
            result["total_remaining"] = max(0.0, limit.total_limit_usd - usage.total_spent_usd)
        return result

    def get_usage(self, key: str) -> BudgetUsage | None:
        usage = self._usage.get(key)
        if usage is None:
            return None
        self._reset_if_needed(key)
        return usage

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_usage(self, key: str) -> BudgetUsage:
        usage = self._usage.get(key)
        if usage is None:
            now = self._clock()
            usage = BudgetUsage(
                daily_spent_usd=0.0,
                monthly_spent_usd=0.0,
                total_spent_usd=0.0,
                daily_reset_time=self._next_day(now),
                monthly_reset_time=self._next_month(now),
            )
            self._usage[key] = usage
        return usage

    def _reset_if_needed(self, key: str) -> None:
        usage = self._usage[key]
        now = self._clock()

        if now >= usage.daily_reset_time:
            usage.daily_spent_usd = 0.0
            usage.daily_reset_time = self._next_day(now)
            usage.last_alert_time = None

        if now >= usage.monthly_reset_time:
            usage.monthly_spent_usd = 0.0
            usage.monthly_reset_time = self._next_month(now)
            usage.last_alert_time = None

    def _check_alert_threshold(self, key: str, estimated_cost_usd: float) -> None:
        limit = self._limits[key]
        usage = self._usage[key]
        now = self._clock()

        if limit.alert_threshold_percent <= 0:
            return

        threshold = limit.alert_threshold_percent / 100.0
        if usage.last_alert_time and now - usage.last_alert_time < 3600:
            return

        daily_ratio = (usage.daily_spent_usd + estimated_cost_usd) / limit.daily_limit_usd
        monthly_ratio = (usage.monthly_spent_usd + estimated_cost_usd) / limit.monthly_limit_usd

        if daily_ratio >= threshold or monthly_ratio >= threshold:
            usage.last_alert_time = now

    @staticmethod
    def _next_day(now: float) -> float:
        dt = datetime.fromtimestamp(now, tz=UTC) + timedelta(days=1)
        return datetime(dt.year, dt.month, dt.day, tzinfo=UTC).timestamp()

    @staticmethod
    def _next_month(now: float) -> float:
        dt = datetime.fromtimestamp(now, tz=UTC)
        last_day = calendar.monthrange(dt.year, dt.month)[1]
        next_month = dt.replace(day=1) + timedelta(days=last_day)
        return datetime(next_month.year, next_month.month, 1, tzinfo=UTC).timestamp()


__all__ = ["BudgetLimit", "BudgetManager", "BudgetUsage"]
