#!/usr/bin/env python3
"""Code churn analysis utility for pheno-sdk.

Generates churn statistics from the git history to surface hotspots and high-velocity
contributors. The script is deliberately lightweight so it can run inside CI without
additional dependencies.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_SUBSTRINGS = (
    "node_modules/",
    ".venv/",
    ".git/",
    "htmlcov/",
)


@dataclass
class FileChurn:
    path: str
    commits: int
    lines_added: int
    lines_deleted: int

    @property
    def total_changes(self) -> int:
        return self.lines_added + self.lines_deleted

    def to_dict(self) -> dict[str, int | str]:
        payload = asdict(self)
        payload["total_changes"] = self.total_changes
        return payload


def _run_git_log(
    *,
    since: str | None = None,
    until: str | None = None,
    include: Iterable[str] | None = None,
) -> str:
    """
    Execute git log and return the raw output.
    """

    base_cmd: list[str] = [
        "git",
        "-C",
        str(REPO_ROOT),
        "log",
        "--numstat",
        "--pretty=commit\t%H\t%an\t%ad",
    ]

    if since:
        base_cmd.extend(["--since", since])
    if until:
        base_cmd.extend(["--until", until])

    if include:
        base_cmd.append("--")
        base_cmd.extend(include)

    try:
        completed = subprocess.run(
            base_cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise RuntimeError(f"Failed to collect git churn data: {exc}") from exc


def _parse_git_log(raw_output: str) -> list[dict[str, object]]:
    """
    Parse git log output into a structured representation.
    """

    commits: list[dict[str, object]] = []
    current_commit: dict[str, object] | None = None

    for line in raw_output.splitlines():
        if not line:
            continue

        if line.startswith("commit\t"):
            if current_commit:
                commits.append(current_commit)
            _, sha, author, date = line.split("\t", 3)
            current_commit = {
                "hash": sha,
                "author": author,
                "date": date,
                "files": [],
            }
            continue

        if current_commit is None:
            # Unexpected structure, skip defensively.
            continue

        parts = line.split("\t")
        if len(parts) != 3:
            continue

        added, deleted, path = parts
        if added == "-" or deleted == "-":
            # Binary files do not provide line level metrics.
            added = deleted = "0"

        try:
            additions = int(added)
            deletions = int(deleted)
        except ValueError:
            # Skip malformed lines gracefully.
            continue

        current_commit["files"].append(
            {"path": path, "additions": additions, "deletions": deletions},
        )

    if current_commit:
        commits.append(current_commit)

    return commits


def calculate_churn(commits: Iterable[dict[str, object]]) -> dict[str, object]:
    """
    Aggregate churn statistics from commit metadata.
    """

    file_accumulator: dict[str, FileChurn] = {}
    author_commits: Counter[str] = Counter()
    total_additions = 0
    total_deletions = 0
    total_file_touches = 0

    for commit in commits:
        author = str(commit.get("author", "unknown"))
        author_commits[author] += 1

        files = commit.get("files", [])
        if not isinstance(files, list):
            continue

        for file_entry in files:
            path = str(file_entry.get("path", ""))
            additions = int(file_entry.get("additions", 0))
            deletions = int(file_entry.get("deletions", 0))

            if not path:
                continue
            if any(token in path for token in EXCLUDED_SUBSTRINGS):
                continue

            total_additions += additions
            total_deletions += deletions
            total_file_touches += 1

            if path not in file_accumulator:
                file_accumulator[path] = FileChurn(
                    path=path,
                    commits=1,
                    lines_added=additions,
                    lines_deleted=deletions,
                )
            else:
                stats = file_accumulator[path]
                stats.commits += 1
                stats.lines_added += additions
                stats.lines_deleted += deletions

    sorted_paths = sorted(
        file_accumulator,
        key=lambda item: file_accumulator[item].total_changes,
        reverse=True,
    )

    churn_summary = {
        "generated_at": datetime.now(UTC).isoformat(),
        "total_commits": sum(author_commits.values()),
        "total_files_changed": total_file_touches,
        "lines_added": total_additions,
        "lines_deleted": total_deletions,
        "top_authors": [
            {"author": author, "commits": count} for author, count in author_commits.most_common(5)
        ],
        "top_files": [file_accumulator[path].to_dict() for path in sorted_paths[:50]],
    }

    return churn_summary


def summarise_churn(summary: dict[str, object], *, limit: int) -> str:
    """
    Human readable summary string.
    """

    lines = [
        "Pheno-SDK code churn analysis",
        "================================",
        f"Total commits analysed: {summary.get('total_commits', 0)}",
        f"Files touched: {summary.get('total_files_changed', 0)}",
        f"Lines added: {summary.get('lines_added', 0)}",
        f"Lines deleted: {summary.get('lines_deleted', 0)}",
        "",
        "Top contributors:",
    ]

    for author in summary.get("top_authors", []):
        lines.append(f"  - {author['author']}: {author['commits']} commits")

    lines.append("")
    lines.append(f"Top {limit} files by churn:")

    for file_info in summary.get("top_files", [])[:limit]:
        lines.append(
            "  - {path} (commits: {commits}, +{lines_added}/-{lines_deleted})".format(**file_info),
        )

    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyse git churn for pheno-sdk.")
    parser.add_argument(
        "--since",
        help="Limit analysis to commits more recent than this expression (e.g. '90 days ago').",
    )
    parser.add_argument(
        "--until",
        help="Limit analysis to commits older than this expression.",
    )
    parser.add_argument(
        "--include",
        action="append",
        help="Restrict analysis to specific paths (can be provided multiple times).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit results as JSON.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the JSON report.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top churn files to display in text mode (default: 10).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        raw_log = _run_git_log(
            since=args.since,
            until=args.until,
            include=args.include,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    commits = _parse_git_log(raw_log)
    summary = calculate_churn(commits)

    if args.json or args.output:
        payload = json.dumps(summary, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload)
        if args.json:
            print(payload)
    else:
        print(summarise_churn(summary, limit=args.top))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
