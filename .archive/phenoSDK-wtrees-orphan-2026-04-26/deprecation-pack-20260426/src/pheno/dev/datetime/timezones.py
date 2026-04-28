"""
Timezone utilities.
"""

from datetime import UTC, datetime, timezone, tzinfo


def now_utc() -> datetime:
    """
    Get current UTC datetime.
    """
    return datetime.now(UTC)


def to_utc(dt: datetime) -> datetime:
    """
    Convert datetime to UTC.
    """
    if dt.tzinfo is None:
        # Assume naive datetime is UTC
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def to_timezone(dt: datetime, tz: tzinfo) -> datetime:
    """
    Convert datetime to specified timezone.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(tz)


def get_timezone(offset_hours: int) -> tzinfo:
    """Get timezone for UTC offset.

    Example:
        get_timezone(-5)  # UTC-5
    """
    from datetime import timedelta

    return timezone(timedelta(hours=offset_hours))
