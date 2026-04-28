#!/usr/bin/env python3
"""rewrite_code_like_titles module."""

import contextlib
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

POSTGRES_URL = os.environ.get(
    "TRACERTM_DATABASE_URL",
    "postgresql://kooshapari@localhost:5432/agent_api",
)

SKIP_DIRS = {
    ".git",
    ".venv",
    ".venv_test",
    "node_modules",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    ".uv-cache",
    ".playwright-mcp",
    ".sessions",
    ".trace",
    "__pycache__",
    ".hypothesis",
}

CODE_LIKE_RE = re.compile(
    r"("  # group
    r"^[A-Z0-9_]{4,}$|"  # ALLCAPS snake
    r"^[a-z0-9_]{4,}$|"  # lowercase snake
    r".*\w+\(.*\).*|"  # function-like
    r".*::.*|"  # namespace
    r".*->.*|"  # arrow
    r".*\\.*|"  # backslash path
    r".*\.[tg]s$|"  # file extension
    r".*\.py$|"  # file extension
    r".*\.go$|"  # file extension
    r".*_.*"  # underscores
    r")",
)

HTTP_VERB_RE = re.compile(r"^(GET|POST|PUT|PATCH|DELETE)\s+/")

CAMEL_RE_1 = re.compile(r"([a-z0-9])([A-Z])")
CAMEL_RE_2 = re.compile(r"([A-Z]+)([A-Z][a-z])")

ACRONYMS = {
    "api",
    "id",
    "url",
    "ui",
    "qa",
    "db",
    "sql",
    "http",
    "grpc",
    "sso",
    "jwt",
    "oauth",
    "cdn",
    "ux",
    "tls",
    "ip",
    "cpu",
    "gpu",
}

SMALL_WORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "to",
    "of",
    "in",
    "at",
    "on",
    "for",
    "by",
    "with",
    "from",
    "into",
    "over",
    "per",
    "vs",
    "via",
}

PREFIX_LABELS = {
    "metric": "Metric",
    "event": "Event",
    "table": "Table",
    "schema": "Schema",
    "index": "Index",
    "cache": "Cache",
    "policy": "Policy",
    "alert": "Alert",
    "service": "Service",
    "field": "Field",
}


FIELD_SUFFIX_RE = re.compile(r"\s+(id|ids|at|on|by|to|from|of|for|in|out|key|url|uri|ip)$", re.IGNORECASE)


def title_case_words(text: str) -> str:
    """Title case words."""
    words = []
    tokens = text.split(" ")
    for i, token in enumerate(tokens):
        lower = token.lower()
        if lower in ACRONYMS:
            words.append(lower.upper())
        elif lower in SMALL_WORDS and i != 0:
            words.append(lower)
        elif token.isupper() and len(token) <= 4:
            words.append(token)
        else:
            words.append(token[:1].upper() + token[1:])
    return " ".join(words)


def normalize_token(token: str) -> str:
    """Normalize token."""
    return CAMEL_RE_1.sub(r"\1 \2", CAMEL_RE_2.sub(r"\1 \2", token))


def singularize(word: str) -> str:
    """Singularize."""
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("ses"):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def normalize_field_phrase(text: str) -> str:
    """Normalize field phrase."""
    words = text.split(" ")
    if len(words) >= 2:
        words[0] = singularize(words[0].lower())
    return title_case_words(" ".join(words))


def humanize_dot_notation(title: str) -> str:
    """Humanize dot notation."""
    parts = title.split(".")
    if not parts:
        return title
    head = parts[0].lower()
    label = PREFIX_LABELS.get(head)
    tail = parts[1:]
    tail_text = " ".join(normalize_token(p.replace("_", " ")) for p in tail).strip()
    tail_text = re.sub(r"\s+", " ", tail_text).strip()

    if label == "Field" and len(tail) >= 2:
        field_text = normalize_field_phrase(" ".join(tail))
        return f"Field: {field_text}"

    tail_text = title_case_words(tail_text)
    if label:
        return f"{label}: {tail_text}" if tail_text else label

    full_text = " ".join(normalize_token(p.replace("_", " ")) for p in parts)
    return title_case_words(re.sub(r"\s+", " ", full_text).strip())


def humanize_parens(title: str) -> str:
    """Humanize parens."""
    match = re.match(r"^(.*?)\((.*?)\)(.*)$", title)
    if not match:
        return title
    before, inside, after = match.groups()
    before = title_case_words(normalize_token(before.replace("_", " ")).strip())
    inside = title_case_words(normalize_token(inside.replace("_", " ")).strip())
    after = title_case_words(normalize_token(after.replace("_", " ")).strip())
    if after:
        return f"{before} {after} ({inside})".strip()
    return f"{before} ({inside})".strip()


def maybe_field_style(original: str) -> str:
    """Maybe field style."""
    if "." in original:
        return ""
    normalized = normalize_token(original.replace("_", " "))
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if not normalized:
        return ""
    if FIELD_SUFFIX_RE.search(normalized):
        return f"Field: {normalize_field_phrase(normalized)}"
    return ""


def humanize_title(title: str) -> str:
    """Humanize title."""
    original = title
    if HTTP_VERB_RE.search(title):
        return title

    if "." in title and " " not in title:
        return humanize_dot_notation(title)

    # Remove file extensions
    title = re.sub(r"\.(ts|js|py|go)$", "", title)

    # Remove parameter lists
    title = re.sub(r"\([^)]*\)", "", title)

    # Replace separators
    title = title.replace("_", " ").replace("-", " ")

    # Normalize camel case
    parts = [normalize_token(token) for token in title.split()]
    title = " ".join(parts)

    # Cleanup arrows/namespaces
    title = title.replace("::", " ").replace("->", " to ")

    if "(" in original and ")" in original:
        return humanize_parens(original)

    title = re.sub(r"\s+", " ", title).strip()
    if not title:
        return original

    field_style = maybe_field_style(original)
    if field_style:
        return field_style

    return title_case_words(title)


def is_code_like(title: str) -> bool:
    """Is code like."""
    if HTTP_VERB_RE.search(title):
        return False
    return bool(CODE_LIKE_RE.match(title))


def report_postgres(conn: Any) -> None:
    """Report postgres."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            select project_id, count(*) as total,
                   sum(case when title ~ '^[A-Z0-9_]{4,}$' then 1 else 0 end) as allcaps_snake,
                   sum(case when title ~ '^[a-z0-9_]{4,}$' then 1 else 0 end) as lowersnake,
                   sum(case when title ~ '\\w+\\(.*\\)' then 1 else 0 end) as function_like,
                   sum(case when title ~ '::' then 1 else 0 end) as namespaced,
                   sum(case when title ~ '->' then 1 else 0 end) as arrow,
                   sum(case when title ~ '\\.[tg]s$|\\.py$|\\.go$' then 1 else 0 end) as file_ext,
                   sum(case when title ~ '_' then 1 else 0 end) as underscore
            from items
            where title !~ '^(GET|POST|PUT|PATCH|DELETE) '
            group by project_id
            order by total desc;
            """,
        )
        return cur.fetchall()


def rewrite_postgres(conn: Any) -> None:
    """Rewrite postgres."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("select id, title, item_metadata->>'original_title' as original_title from items")
        rows = cur.fetchall()
        updates = []
        for row in rows:
            title = row["title"]
            original_title = row["original_title"] or ""
            source = original_title or title
            if not is_code_like(source):
                continue
            new_title = humanize_title(source)
            if new_title and new_title != title:
                updates.append((new_title, source, row["id"]))

        if not updates:
            return 0

        cur.execute(
            f"""
            update items
            set title = %s,
                item_metadata = jsonb_set(item_metadata, '{original_title}', to_jsonb(%s::text), true)
            where id = %s
        """,
            updates[0],
        )

        if len(updates) > 1:
            cur.executemany(
                f"""
                update items
                set title = %s,
                    item_metadata = jsonb_set(item_metadata, '{original_title}', to_jsonb(%s::text), true)
                where id = %s
            """,
                updates[1:],
            )

        return len(updates)


def iter_db_files(root: str) -> None:
    """Iter db files."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if filename.endswith(".db"):
                yield str(Path(dirpath) / filename)


def has_table(conn: sqlite3.Connection, table: str) -> bool:
    """Has table."""
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def rewrite_sqlite(db_path: str) -> None:
    """Rewrite sqlite."""
    result = {
        "db": db_path,
        "updated": 0,
        "skipped": False,
        "reason": "",
    }

    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as exc:
        result["skipped"] = True
        result["reason"] = f"connect_error:{exc}"
        return result

    try:
        if not has_table(conn, "items"):
            result["skipped"] = True
            result["reason"] = "missing_items_table"
            return result

        cur = conn.execute("SELECT id, title, COALESCE(item_metadata, '{}') FROM items")
        updates = []
        for item_id, title, item_metadata in cur.fetchall():
            original_title = ""
            if item_metadata and isinstance(item_metadata, str) and "original_title" in item_metadata:
                original_title = item_metadata
            source = original_title or title
            if not is_code_like(source):
                continue
            new_title = humanize_title(source)
            if new_title and new_title != title:
                updates.append((new_title, source, item_id))

        if updates:
            conn.executemany(
                "UPDATE items SET title = ?, item_metadata = json_set(COALESCE(item_metadata,'{}'),'$.original_title', ?) WHERE id = ?",
                updates,
            )
            result["updated"] = len(updates)
            conn.commit()
        with contextlib.suppress(sqlite3.Error):
            conn.execute("VACUUM")
    finally:
        conn.close()

    return result


def main() -> None:
    """Main."""
    conn = psycopg2.connect(POSTGRES_URL)
    try:
        report = report_postgres(conn)
        for _row in report:
            pass

        rewrite_postgres(conn)
        conn.commit()
    finally:
        conn.close()

    root = str(Path(__file__).resolve().parent.parent)
    for db_path in sorted(set(iter_db_files(root))):
        res = rewrite_sqlite(db_path)
        if res["skipped"]:
            pass


if __name__ == "__main__":
    main()
