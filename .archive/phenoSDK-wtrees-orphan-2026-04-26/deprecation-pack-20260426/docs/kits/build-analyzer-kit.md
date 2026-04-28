# Build Analyzer Kit

## At a Glance
- **Purpose:** Normalize build logs, extract actionable issues, and generate reports for CI/CD pipelines.
- **Best For:** Tooling that aggregates compiler, linter, and bundler output across languages.
- **Key Building Blocks:** `BuildAnalyzer`, parser registry, normalizers, reporters (`JSONReporter`, `TableReporter`).

## Core Capabilities
- Regex-based and structured parsers for common build tools (Python, TypeScript, Rust, etc.).
- Normalization pipeline that deduplicates messages and categorizes by severity.
- Summary statistics (error/warning counts) and file-level grouping.
- Reporters that export to JSON, Markdown, or terminal tables.
- Hooks to integrate with CI status checks or messaging bots.

## Getting Started

### Installation
```
pip install build-analyzer-kit
```

### Minimal Example
```python
from build_analyzer import BuildAnalyzer

logs = "src/app.py:10: error F821 undefined name 'user'"

analyzer = BuildAnalyzer()
issues = analyzer.parse(logs)
summary = analyzer.summarize(issues)
print(summary.errors, summary.warnings)
```

## How It Works
- Parsers in `build_analyzer.parsers` convert raw lines into `Issue` objects.
- Normalizers in `build_analyzer.normalizers` clean up file paths, dedupe duplicates, and resolve severities.
- Reporters turn normalized issues into consumable output for CI dashboards.
- Parsers are registered automatically; add new ones by subclassing `BaseParser` and calling `register_parser`.

## Usage Recipes
- Attach to CI logs: stream build stdout into `BuildAnalyzer.parse_stream()`.
- Combine with workflow-kit to fail deployment steps when critical issues remain.
- Publish summarized results via stream-kit to update developer dashboards.
- Store normalized issues with db-kit for historical analysis.

## Interoperability
- Works with config-kit for customizing parser settings via typed config.
- Emits structured metrics (`build_issues_total`) when wired through observability-kit.
- Expose results through cli-builder-kit commands for local developers.

## Operations & Observability
- Export JSON reports and archive in object storage via storage-kit for auditing.
- Track issue counts over time; integrate with resource-management-kit to monitor build resource usage.
- Add logging around analyzer stages to trace parsing throughput.

## Testing & QA
- Unit tests rely on sample logs under `tests/data/`.
- Add contract tests when introducing new parsers to ensure patterns are matched correctly.
- Use fixtures to simulate noisy logs and confirm deduplication logic.

## Troubleshooting
- **No issues detected:** verify the right parser is registered or create a custom pattern.
- **Incorrect file paths:** adjust normalizers to handle workspace-relative paths.
- **Performance concerns:** batch logs and reuse analyzer instances in long-running processes.

## Primary API Surface
- `BuildAnalyzer(parse_config=None)`
- `BuildAnalyzer.parse(logs: str)` / `parse_stream(iterable)`
- `BuildAnalyzer.summarize(issues)` → `Summary` dataclass
- Parser registration: `register_parser("tool", ParserClass)`
- Reporters: `reporters.JSONReporter`, `reporters.TableReporter`

## Additional Resources
- Examples: `build-analyzer-kit/examples/`
- Tests: `build-analyzer-kit/tests/`
- Related concepts: [Testing & Quality](../concepts/testing-quality.md)
