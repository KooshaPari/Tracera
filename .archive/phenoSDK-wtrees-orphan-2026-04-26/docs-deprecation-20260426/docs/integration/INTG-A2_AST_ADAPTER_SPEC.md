# INTG-A2 – Tree-Sitter AST Adapter Design

**Status:** ✅ Complete (Design Approved)
**Date:** 2025-10-14
**Owner:** SDK Architecture Guild
**Depends On:** `INTG-A1` (analytics namespace scaffolding)
**Consumers:** Morph semantic analysis, Router routing heuristics

---

## 1. Goal

Provide language-agnostic AST parsing utilities using tree-sitter to enable Morph/Router to analyse code structure uniformly and support advanced routing heuristics.

---

## 2. Module Layout

```
src/pheno/analytics/ast/
├── __init__.py
├── adapter.py
├── registry.py
├── grammars/
│   └── README.md            # instructions for bundling/optional downloads
└── models.py
```

- Optional extra `analytics-ast` installs `tree-sitter>=0.22,<0.23`.
- Grammar packs distributed via dynamic download (`tree_sitter_languages`) with cache stored under `~/.pheno/tree-sitter`.

---

## 3. API Specification

```python
# models.py
@dataclass(frozen=True)
class AstNode:
    type: str
    text: str
    start_point: tuple[int, int]
    end_point: tuple[int, int]
    children: tuple["AstNode", ...] = ()

class TreeSitterAdapter(Protocol):
    async def parse(self, source: str | bytes) -> AstNode: ...
    async def query(self, source: str | bytes, *, pattern: str) -> list[AstNode]: ...
```

```python
# adapter.py
async def get_adapter(language: str) -> TreeSitterAdapter:
    """Return cached adapter for language (python, javascript, markdown, etc.)."""
```

```python
# registry.py
SUPPORTED_LANGUAGES = {"python", "javascript", "typescript", "markdown"}

async def ensure_grammar(language: str) -> Path:
    """Download grammar if missing, return local path."""
```

- Parsing runs in thread pool; adapters cached per language.
- Integrate with `pheno.utilities.cache.LruCache` (INTG-A5) for AST caching by file hash.

---

## 4. Operational Considerations

- **Licensing:** tree-sitter grammars use MIT/Apache; include NOTICE file and reference sources in docs.
- **Security:** restrict grammar downloads to vetted list; allow offline mode by bundling critical grammars.
- **Performance:** parse operations must complete <200ms for medium files; include benchmarks in tests.
- **Configuration:** `pheno.config.analytics.TreeSitterSettings` controlling grammar path, download toggle, max file size.

---

## 5. Testing & Verification

- Unit tests to validate adapter registry caching and AST structure.
- Integration tests parsing Morph/Router sample files.
- Query tests ensuring CSS-style queries can locate functions/classes.
- Negative tests for unsupported languages, large file rejection, grammar download errors.

---

## 6. Documentation & Samples

- Add quickstart snippet demonstrating Python AST query in `docs/guides/integration/analytics-tooling.md`.
- Provide CLI tool example under `tools/analytics/preview_ast.py`.
- Document environment variable `PHENO_ANALYTICS_DISABLE_TREE_SITTER_DOWNLOAD`.

---

## 7. Follow-ups

- [ ] Implement grammar download cache (INTG-A5 dependency).
- [ ] Update Morph migration guide to show swapping in SDK AST utilities.
- [ ] Add metrics: count AST parses, errors per language, grammar cache hits.

Approved 2025-10-14.
