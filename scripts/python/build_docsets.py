#!/usr/bin/env python3
"""Generate HTML docsets for the workspace Markdown collections.

The script keeps two docsets in sync:
1. The workspace/codebase documentation under `docs/`
2. The pheno-sdk developer documentation under `pheno-sdk/docs/`

Usage:
    python scripts/build_docsets.py              # build both docsets into build/docsets/
    python scripts/build_docsets.py --docset sdk # build only the SDK docset
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import operator
import os
import shutil
from collections import defaultdict
from pathlib import Path

try:
    from markdown import Markdown
except ImportError as exc:  # pragma: no cover - dependency guard
    msg = "Missing dependency: markdown. Install via `pip install pheno-sdk[docs]` or `pip install markdown pygments`."
    raise SystemExit(
        msg,
    ) from exc


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "build" / "docsets"


@dataclasses.dataclass(frozen=True)
class Docset:
    """Docset."""

    name: str
    title: str
    source: Path
    description: str
    audience: str


DOCSETS: list[Docset] = [
    Docset(
        name="codebase",
        title="Kush Codebase Docset",
        source=REPO_ROOT / "docs",
        description="Workspace-wide architecture, research, cleanup, and planning references.",
        audience="Workspace contributors",
    ),
    Docset(
        name="sdk",
        title="pheno-sdk Developer Docset",
        source=REPO_ROOT / "pheno-sdk" / "docs",
        description="Developer handbook for building against the pheno-sdk adapters and services.",
        audience="SDK developers",
    ),
]


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{page_title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #f7f7f9;
      --fg: #1f2933;
      --card: #ffffff;
      --accent: #2563eb;
      --muted: #64748b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--fg);
      line-height: 1.55;
    }}
    header {{
      background: var(--card);
      border-bottom: 1px solid rgba(15, 23, 42, 0.08);
      padding: 1.5rem clamp(1rem, 3vw, 3rem);
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    header h1 {{ margin: 0 0 0.25rem; font-size: 1.5rem; }}
    header p {{ margin: 0; color: var(--muted); }}
    main {{
      padding: clamp(1rem, 3vw, 3rem);
      display: grid;
      gap: 1.5rem;
    }}
    .card {{
      background: var(--card);
      border-radius: 12px;
      padding: clamp(1rem, 2vw, 2rem);
      box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    }}
    .toc h2 {{
      margin-top: 0;
      font-size: 1rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    .toc nav {{ font-size: 0.95rem; }}
    .toc nav ul {{ padding-left: 1rem; }}
    .content h1 {{ margin-top: 0; }}
    pre {{
      overflow: auto;
      background: #0f172a;
      color: #f1f5f9;
      padding: 1rem;
      border-radius: 10px;
      font-size: 0.9rem;
    }}
    code {{
      font-family: "JetBrains Mono", "Fira Code", monospace;
    }}
    a {{
      color: var(--accent);
      text-decoration: none;
    }}
    a:hover {{ text-decoration: underline; }}
    footer {{
      font-size: 0.85rem;
      color: var(--muted);
    }}
  </style>
</head>
{body}
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #0f172a;
      --fg: #e2e8f0;
      --muted: #94a3b8;
      --card: rgba(15, 23, 42, 0.65);
      --accent: #38bdf8;
    }}
    body {{
      margin: 0;
      font-family: "Inter", "Segoe UI", system-ui, sans-serif;
      background: linear-gradient(135deg, #0f172a 0%, #1d2639 100%);
      min-height: 100vh;
      color: var(--fg);
    }}
    header {{
      padding: clamp(1.5rem, 4vw, 4rem);
    }}
    main {{
      padding: 0 clamp(1.5rem, 4vw, 4rem) clamp(2rem, 5vw, 5rem);
      display: grid;
      gap: 1.5rem;
    }}
    .summary {{
      background: var(--card);
      border-radius: 16px;
      padding: clamp(1.25rem, 3vw, 3rem);
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
    }}
    .summary h1 {{ margin-top: 0; font-size: clamp(1.5rem, 3vw, 2.75rem); }}
    .summary p {{ color: var(--muted); }}
    .groups {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.5rem;
    }}
    .group {{
      background: var(--card);
      border-radius: 14px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}
    .group h2 {{
      margin: 0;
      font-size: 1.1rem;
      color: #f8fafc;
    }}
    .group ul {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }}
    .group a {{
      color: var(--accent);
      text-decoration: none;
      font-weight: 500;
    }}
    .group a:hover {{ text-decoration: underline; }}
    footer {{
      text-align: center;
      color: var(--muted);
      font-size: 0.85rem;
      margin-top: 1rem;
    }}
  </style>
</head>
<body>
  <header>
    <div class="summary">
      <h1>{title}</h1>
      <p>{description}</p>
      <p><strong>Audience:</strong> {audience} · <strong>Generated:</strong> {generated}</p>
      <p>Total Markdown files: {count}</p>
    </div>
  </header>
  <main>
    <div class="groups">
      {groups_html}
    </div>
  </main>
  <footer>
    Built by scripts/build_docsets.py · Source root: {source}
  </footer>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    """Parse args."""
    parser = argparse.ArgumentParser(
        description="Generate HTML mirrors for Markdown docsets.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--docset",
        choices=[d.name for d in DOCSETS],
        action="append",
        help="Limit the run to a specific docset. Omit to build everything.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination directory for generated HTML.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete the output directory before rebuilding.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-file log lines.",
    )
    return parser.parse_args()


def main() -> None:
    """Main."""
    args = parse_args()
    targets = [d for d in DOCSETS if args.docset is None or d.name in args.docset]
    if not targets:
        msg = "No docsets selected."
        raise SystemExit(msg)

    output_root = args.output.resolve()
    if args.clean and output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    for docset in targets:
        build_docset(docset, output_root, quiet=args.quiet)


def build_docset(docset: Docset, output_root: Path, quiet: bool = False) -> None:
    """Build docset."""
    if not docset.source.exists():
        msg = f"Docset '{docset.name}' source not found: {docset.source}"
        raise SystemExit(msg)

    destination = output_root / docset.name
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    manifest = []
    markdown_files = sorted(docset.source.rglob("*.md"))

    for md_path in markdown_files:
        rel_md = md_path.relative_to(docset.source)
        html_path = destination / rel_md.with_suffix(".html")
        html_path.parent.mkdir(parents=True, exist_ok=True)

        page_title = derive_title(rel_md)
        html_body, toc_html = render_markdown(md_path.read_text(encoding="utf-8"))
        rel_root = relative_root_prefix(html_path, destination)
        stats = md_path.stat()
        updated = dt.datetime.fromtimestamp(stats.st_mtime, tz=dt.UTC)

        page_html = HTML_TEMPLATE.format(
            page_title=f"{page_title} · {docset.title}",
            body=_page_body(
                docset=docset,
                page_title=page_title,
                toc_html=toc_html,
                content_html=html_body,
                rel_root=rel_root,
                source_rel=str(rel_md),
                updated=updated,
            ),
        )
        html_path.write_text(page_html, encoding="utf-8")

        manifest.append({
            "title": page_title,
            "source_markdown": str(md_path),
            "relative_markdown": str(rel_md).replace(os.sep, "/"),
            "relative_html": str(html_path.relative_to(destination)).replace(os.sep, "/"),
            "last_modified": updated.isoformat(),
        })

        if not quiet:
            pass

    write_index(docset, manifest, destination)
    copy_assets(docset.source, destination)
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def render_markdown(text: str) -> tuple[str, str]:
    """Render markdown."""
    md = Markdown(
        extensions=[
            "toc",
            "fenced_code",
            "codehilite",
            "tables",
            "admonition",
            "def_list",
            "attr_list",
            "abbr",
            "footnotes",
            "sane_lists",
        ],
        extension_configs={
            "toc": {"permalink": True},
            "codehilite": {
                "guess_lang": False,
                "pygments_style": "friendly",
                "noclasses": True,
            },
        },
        output_format="html5",
    )
    html = md.convert(text)
    toc_html = getattr(md, "toc", "")
    return html, toc_html


def derive_title(rel_path: Path) -> str:
    """Derive title."""
    name = rel_path.stem.replace("_", " ").replace("-", " ")
    if not name:
        return "Untitled"
    if name.isupper():
        return name
    parts = [part for part in name.split() if part]
    return " ".join(part.capitalize() for part in parts)


def relative_root_prefix(html_path: Path, docset_root: Path) -> str:
    """Relative root prefix."""
    rel = html_path.relative_to(docset_root)
    parent = rel.parent
    if parent == Path():
        return ""
    depth = len(parent.parts)
    return "../" * depth


def _page_body(
    docset: Docset,
    page_title: str,
    toc_html: str,
    content_html: str,
    rel_root: str,
    source_rel: str,
    updated: dt.datetime,
) -> str:
    toc_section = f"<section class='card toc'><h2>Outline</h2>{toc_html or '<p>No headings found.</p>'}</section>"
    return f"""
<body>
  <header>
    <h1>{page_title}</h1>
    <p>{docset.description}</p>
    <p><strong>Audience:</strong> {docset.audience} · <strong>Source:</strong> {source_rel} · <strong>Last updated:</strong> {updated.strftime("%Y-%m-%d")}</p>
    <p><a href="{rel_root}index.html">← Back to {docset.title} index</a></p>
  </header>
  <main>
    {toc_section}
    <section class="card content">
      {content_html}
    </section>
  </main>
  <footer>
    Generated by scripts/build_docsets.py on {dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")}
  </footer>
</body>
"""


def write_index(docset: Docset, manifest: list[dict], destination: Path) -> None:
    """Write index."""
    grouped = defaultdict(list)
    for entry in manifest:
        rel = entry["relative_markdown"]
        parts = rel.split("/")
        top = parts[0] if len(parts) > 1 else "root"
        grouped[top].append(entry)

    groups_html = []
    for group_name, entries in sorted(grouped.items()):
        display_name = "Root Files" if group_name == "root" else derive_title(Path(group_name))
        links = "\n".join(
            f'<li><a href="{entry["relative_html"]}">{entry["title"]}</a></li>'
            for entry in sorted(entries, key=operator.itemgetter("relative_html"))
        )
        groups_html.append(f"<section class='group'><h2>{display_name}</h2><ul>{links}</ul></section>")

    index_html = INDEX_TEMPLATE.format(
        title=docset.title,
        description=docset.description,
        audience=docset.audience,
        generated=dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC"),
        count=len(manifest),
        groups_html="\n".join(groups_html),
        source=docset.source,
    )
    (destination / "index.html").write_text(index_html, encoding="utf-8")


def copy_assets(source: Path, destination: Path) -> None:
    """Copy assets."""
    for path in source.rglob("*"):
        if path.is_dir():
            continue
        if path.suffix.lower() == ".md":
            continue
        rel = path.relative_to(source)
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


if __name__ == "__main__":
    main()
