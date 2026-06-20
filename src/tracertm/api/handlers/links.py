"""Link listing handlers and helpers for reducing complexity.

Functional Requirements: FR-APP-002
"""

from dataclasses import dataclass
from typing import Any, cast

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.cache_service import CacheService

# Allowlist of valid column names for dynamic SQL construction.
# Only these identifiers may be interpolated into queries to prevent SQL injection.
_VALID_LINK_COLUMNS: frozenset[str] = frozenset({
    "source_item_id",
    "source_id",
    "target_item_id",
    "target_id",
    "link_type",
    "type",
    "link_metadata",
    "metadata",
})


def _validate_column(col: str) -> str:
    """Validate that a column name is in the allowlist.

    Args:
        col: Column name to validate

    Returns:
        The validated column name

    Raises:
        ValueError: If the column name is not in the allowlist
    """
    if col not in _VALID_LINK_COLUMNS:
        msg = f"Invalid column name: {col!r}"
        raise ValueError(msg)
    return col


@dataclass(frozen=True)
class LinkColumns:
    """Resolved column names for the links table."""

    source_col: str
    target_col: str
    type_col: str
    meta_col: str


@dataclass(frozen=True)
class LinkQueryParams:
    """Parameters for link list queries."""

    project_id: str | None
    source_id: str | None
    target_id: str | None
    exclude_types: list[str]
    skip: int
    limit: int | None


def parse_exclude_types(exclude_types: str | None) -> list[str]:
    """Parse comma-separated exclude_types string into a list.

    Args:
        exclude_types: Comma-separated string of link types to exclude

    Returns:
        List of trimmed type strings, empty list if input is None
    """
    if not exclude_types:
        return []
    return [t.strip() for t in exclude_types.split(",") if t.strip()]


def link_row_to_dict(row: object, project_id: str | None) -> dict[str, Any]:
    """Build a link dict from a raw SQL row; safe for None/missing attributes.

    Supports both naming conventions:
    - source_item_id/source_id
    - target_item_id/target_id
    - link_type/type

    Args:
        row: SQL result row with link data
        project_id: Optional project ID to include in result

    Returns:
        Dictionary with normalized link data
    """
    return {
        "id": str(getattr(row, "id", "") or ""),
        "source_id": str(getattr(row, "source_item_id", None) or getattr(row, "source_id", "") or ""),
        "target_id": str(getattr(row, "target_item_id", None) or getattr(row, "target_id", "") or ""),
        "type": getattr(row, "link_type", None) or getattr(row, "type", "") or "",
        "project_id": project_id or "",
    }


async def detect_link_columns(db: AsyncSession) -> LinkColumns:
    """Detect actual column names from the database to support mixed schemas.

    Queries the database schema to find the actual column names used for links,
    supporting both Alembic 000 naming (source_item_id, target_item_id, link_type)
    and Go/045 naming (source_id, target_id, type).

    Args:
        db: Database session

    Returns:
        Tuple of (source_column, target_column, type_column, metadata_column)
    """
    try:
        schema_name = await _fetch_links_schema_name(db)
        cols = await _fetch_links_columns(db, schema_name)
        if not cols:
            return _default_link_columns()
        return LinkColumns(
            source_col=_pick_link_column(cols, "source_item_id", "source_id", "source_id"),
            target_col=_pick_link_column(cols, "target_item_id", "target_id", "target_id"),
            type_col=_pick_link_column(cols, "link_type", "type", "type"),
            meta_col=_pick_link_column(cols, "link_metadata", "metadata", "metadata"),
        )
    except (SQLAlchemyError, RuntimeError, OSError, ValueError):
        return _default_link_columns()


def _default_link_columns() -> LinkColumns:
    return LinkColumns(
        source_col="source_id",
        target_col="target_id",
        type_col="link_type",
        meta_col="metadata",
    )


async def _fetch_links_schema_name(db: AsyncSession) -> str:
    schema_row = await db.execute(
        text(
            "SELECT table_schema FROM information_schema.tables "
            "WHERE table_name = 'links' ORDER BY table_schema LIMIT 1",
        ),
    )
    return schema_row.scalar() or "public"


async def _fetch_links_columns(db: AsyncSession, schema_name: str) -> set[str]:
    cols_result = await db.execute(
        text(
            "SELECT column_name FROM information_schema.columns WHERE table_schema = :schema AND table_name = 'links'",
        ),
        {"schema": schema_name},
    )
    return {row[0] for row in cols_result}


def _pick_link_column(cols: set[str], preferred: str, fallback: str, default: str) -> str:
    if preferred in cols and fallback not in cols:
        return preferred
    if fallback in cols:
        return fallback
    return default


def build_exclude_types_clause(
    exclude_types_list: list[str],
    typ_col: str,
) -> str:
    """Build SQL WHERE clause fragment for excluding link types.

    Args:
        exclude_types_list: List of link types to exclude
        typ_col: Name of the type column in the database

    Returns:
        SQL WHERE clause fragment, empty string if no types to exclude
    """
    if not exclude_types_list:
        return ""

    placeholders = ", ".join([f":exclude_type_{i}" for i in range(len(exclude_types_list))])
    return f" AND {typ_col} NOT IN ({placeholders})"


def build_exclude_types_params(exclude_types_list: list[str]) -> dict[str, Any]:
    """Build parameter dictionary for exclude types SQL clause.

    Args:
        exclude_types_list: List of link types to exclude

    Returns:
        Dictionary mapping parameter names to values
    """
    if not exclude_types_list:
        return {}

    return {f"exclude_type_{i}": t for i, t in enumerate(exclude_types_list)}


async def query_links_by_project(
    db: AsyncSession,
    params: LinkQueryParams,
    columns: LinkColumns,
) -> tuple[int, Any]:
    """Query links filtered by project ID.

    Args:
        db: Database session
        params: Query parameters
        columns: Resolved link column names

    Returns:
        Tuple of (total_count, query_result)
    """
    if not params.project_id:
        return 0, []

    project_id = params.project_id
    exclude_types_list = params.exclude_types
    src_col = _validate_column(columns.source_col)
    tgt_col = _validate_column(columns.target_col)
    typ_col = _validate_column(columns.type_col)
    meta_col = _validate_column(columns.meta_col)
    skip = params.skip
    limit = params.limit

    # Build count query (columns validated against allowlist above)
    count_sql = f"""
        SELECT COUNT(DISTINCT l.id)
        FROM links l
        INNER JOIN items i1 ON l.{src_col} = i1.id
        INNER JOIN items i2 ON l.{tgt_col} = i2.id
        WHERE (i1.project_id = :project_id OR i2.project_id = :project_id)
          AND i1.deleted_at IS NULL
          AND i2.deleted_at IS NULL
    """  # nosec B608 -- column names validated via _validate_column allowlist
    count_sql += build_exclude_types_clause(exclude_types_list, typ_col)

    count_params: dict[str, Any] = {"project_id": project_id}
    count_params.update(build_exclude_types_params(exclude_types_list))

    count_result = await db.execute(text(count_sql), count_params)
    total_count = count_result.scalar() or 0

    # Build data query (columns validated against allowlist above)
    base_sql = f"""
        SELECT DISTINCT l.id, l.{src_col}, l.{tgt_col}, l.{typ_col}, l.created_at, l.{meta_col}
        FROM links l
        INNER JOIN items i1 ON l.{src_col} = i1.id
        INNER JOIN items i2 ON l.{tgt_col} = i2.id
        WHERE (i1.project_id = :project_id OR i2.project_id = :project_id)
          AND i1.deleted_at IS NULL
          AND i2.deleted_at IS NULL
    """  # nosec B608 -- column names validated via _validate_column allowlist
    base_sql += build_exclude_types_clause(exclude_types_list, typ_col)
    base_sql += " ORDER BY l.created_at DESC"

    query_params: dict[str, Any] = {"project_id": project_id}
    query_params.update(build_exclude_types_params(exclude_types_list))

    if limit is not None and limit > 0:
        base_sql += " LIMIT :limit OFFSET :skip"
        query_params.update({"limit": limit, "skip": skip})

    links_result = await db.execute(text(base_sql), query_params)
    return total_count, links_result


async def query_links_by_source_and_target(
    db: AsyncSession,
    params: LinkQueryParams,
    columns: LinkColumns,
) -> tuple[int, Any]:
    """Query links filtered by both source and target IDs.

    Args:
        db: Database session
        params: Query parameters
        columns: Resolved link column names

    Returns:
        Tuple of (total_count, query_result)
    """
    if not params.source_id or not params.target_id:
        return 0, []

    source_id = params.source_id
    target_id = params.target_id
    exclude_types_list = params.exclude_types
    src_col = _validate_column(columns.source_col)
    tgt_col = _validate_column(columns.target_col)
    typ_col = _validate_column(columns.type_col)
    meta_col = _validate_column(columns.meta_col)
    skip = params.skip
    limit = params.limit

    # Build count query (columns validated against allowlist above)
    count_sql = f"""
        SELECT COUNT(*) FROM links
        WHERE {src_col} = :source_id AND {tgt_col} = :target_id
    """  # nosec B608 -- column names validated via _validate_column allowlist
    count_sql += build_exclude_types_clause(exclude_types_list, typ_col)

    count_params: dict[str, Any] = {"source_id": source_id, "target_id": target_id}
    count_params.update(build_exclude_types_params(exclude_types_list))

    count_result = await db.execute(text(count_sql), count_params)
    total_count = count_result.scalar() or 0

    # Build data query (columns validated against allowlist above)
    base_sql = f"""
        SELECT id, {src_col}, {tgt_col}, {typ_col}, created_at, {meta_col}
        FROM links
        WHERE {src_col} = :source_id AND {tgt_col} = :target_id
    """  # nosec B608 -- column names validated via _validate_column allowlist
    base_sql += build_exclude_types_clause(exclude_types_list, typ_col)
    base_sql += " ORDER BY created_at DESC"

    query_params: dict[str, Any] = {"source_id": source_id, "target_id": target_id}
    query_params.update(build_exclude_types_params(exclude_types_list))

    if limit is not None and limit > 0:
        base_sql += " LIMIT :limit OFFSET :skip"
        query_params["limit"] = limit
        query_params["skip"] = skip

    links_result = await db.execute(text(base_sql), query_params)
    return total_count, links_result


async def query_links_by_source(
    db: AsyncSession,
    params: LinkQueryParams,
    columns: LinkColumns,
) -> tuple[int, Any]:
    """Query links filtered by source ID.

    Args:
        db: Database session
        params: Query parameters
        columns: Resolved link column names

    Returns:
        Tuple of (total_count, query_result)
    """
    if not params.source_id:
        return 0, []

    source_id = params.source_id
    exclude_types_list = params.exclude_types
    src_col = _validate_column(columns.source_col)
    tgt_col = _validate_column(columns.target_col)
    typ_col = _validate_column(columns.type_col)
    meta_col = _validate_column(columns.meta_col)
    skip = params.skip
    limit = params.limit

    # Build count query (columns validated against allowlist)
    count_sql = f"SELECT COUNT(*) FROM links WHERE {src_col} = :source_id"  # nosec B608
    count_sql += build_exclude_types_clause(exclude_types_list, typ_col)

    count_params: dict[str, Any] = {"source_id": source_id}
    count_params.update(build_exclude_types_params(exclude_types_list))

    count_result = await db.execute(text(count_sql), count_params)
    total_count = count_result.scalar() or 0

    # Build data query (columns validated against allowlist)
    base_sql = f"""
        SELECT id, {src_col}, {tgt_col}, {typ_col}, created_at, {meta_col}
        FROM links
        WHERE {src_col} = :source_id
    """  # nosec B608 -- column names validated via _validate_column allowlist
    base_sql += build_exclude_types_clause(exclude_types_list, typ_col)
    base_sql += " ORDER BY created_at DESC"

    query_params: dict[str, Any] = {"source_id": source_id}
    query_params.update(build_exclude_types_params(exclude_types_list))

    if limit is not None and limit > 0:
        base_sql += " LIMIT :limit OFFSET :skip"
        query_params["limit"] = limit
        query_params["skip"] = skip

    links_result = await db.execute(text(base_sql), query_params)
    return total_count, links_result


async def query_links_by_target(
    db: AsyncSession,
    params: LinkQueryParams,
    columns: LinkColumns,
) -> tuple[int, Any]:
    """Query links filtered by target ID.

    Args:
        db: Database session
        params: Query parameters
        columns: Resolved link column names

    Returns:
        Tuple of (total_count, query_result)
    """
    if not params.target_id:
        return 0, []

    target_id = params.target_id
    exclude_types_list = params.exclude_types
    src_col = _validate_column(columns.source_col)
    tgt_col = _validate_column(columns.target_col)
    typ_col = _validate_column(columns.type_col)
    meta_col = _validate_column(columns.meta_col)
    skip = params.skip
    limit = params.limit

    # Build count query (columns validated against allowlist)
    count_sql = f"SELECT COUNT(*) FROM links WHERE {tgt_col} = :target_id"  # nosec B608
    count_sql += build_exclude_types_clause(exclude_types_list, typ_col)

    count_params: dict[str, Any] = {"target_id": target_id}
    count_params.update(build_exclude_types_params(exclude_types_list))

    count_result = await db.execute(text(count_sql), count_params)
    total_count = count_result.scalar() or 0

    # Build data query (columns validated against allowlist)
    base_sql = f"""
        SELECT id, {src_col}, {tgt_col}, {typ_col}, created_at, {meta_col}
        FROM links
        WHERE {tgt_col} = :target_id
    """  # nosec B608 -- column names validated via _validate_column allowlist
    base_sql += build_exclude_types_clause(exclude_types_list, typ_col)
    base_sql += " ORDER BY created_at DESC"

    query_params: dict[str, Any] = {"target_id": target_id}
    query_params.update(build_exclude_types_params(exclude_types_list))

    if limit is not None and limit > 0:
        base_sql += " LIMIT :limit OFFSET :skip"
        query_params["limit"] = limit
        query_params["skip"] = skip

    links_result = await db.execute(text(base_sql), query_params)
    return total_count, links_result


def generate_links_cache_key(cache: CacheService, params: LinkQueryParams) -> str:
    """Generate cache key for links query.

    Args:
        cache: Cache service instance
        params: Query parameters

    Returns:
        Cache key string
    """
    return cache._generate_key(
        "links",
        project_id=params.project_id or "",
        source_id=params.source_id or "",
        target_id=params.target_id or "",
        skip=params.skip,
        limit=params.limit or 0,
        exclude_types=",".join(params.exclude_types),
    )


async def try_get_links_from_cache(
    cache: CacheService,
    params: LinkQueryParams,
) -> tuple[str | None, dict[str, Any] | None]:
    """Attempt to get cached result for links query.

    Args:
        cache: Cache service instance
        params: Query parameters

    Returns:
        Tuple of (cache_key, cached_result). Both may be None if caching
        is not applicable or cache miss.
    """
    # Only cache when project_id is specified
    if not params.project_id:
        return None, None

    cache_key = generate_links_cache_key(cache, params)
    cached = await cache.get(cache_key)
    return cache_key, cached


async def execute_links_query(
    db: AsyncSession,
    params: LinkQueryParams,
    columns: LinkColumns,
) -> tuple[int, Any]:
    """Execute the appropriate links query based on filter criteria.

    Args:
        db: Database session
        params: Query parameters
        columns: Resolved link column names

    Returns:
        Tuple of (total_count, query_result)
    """
    if params.project_id:
        return await query_links_by_project(db, params, columns)
    if params.source_id and params.target_id:
        return await query_links_by_source_and_target(db, params, columns)
    if params.source_id:
        return await query_links_by_source(db, params, columns)
    if params.target_id:
        return await query_links_by_target(db, params, columns)
    return 0, None


def build_links_response(
    links_result: object | None,
    total_count: int,
    project_id: str | None,
) -> dict[str, Any]:
    """Build the final links list response.

    Args:
        links_result: Database query result with link rows
        total_count: Total count of matching links
        project_id: Optional project ID to include in link dicts

    Returns:
        Dictionary with total count and list of links
    """
    links_list: list[dict[str, Any]] = []
    if links_result:
        links_list.extend(link_row_to_dict(row, project_id) for row in cast("Any", links_result))

    return {
        "total": total_count,
        "links": links_list,
    }
