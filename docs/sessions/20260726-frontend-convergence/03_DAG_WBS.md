# Convergence DAG / WBS

```text
lineage freeze (95334238c)
        |
        +--> API-base patch (local default, hosted opt-in)
        |
        +--> Rust route contract inventory
        |          |
        |          +--> implement typed missing routes/adapters
        |
        +--> rich web build --> local nginx/compose :18081
                                      |
                                      +--> Electrobun desktop smoke
                                                   |
                                                   +--> promote canonical app
```

Semantic merge rules:

1. Preserve rich views, navigation, accessibility, and tests from the canonical
   candidate; do not replace them with the minimal dashboard.
2. Port only infrastructure/runtime fixes from main when they do not reduce rich
   capabilities.
3. Resolve API differences at typed client/server boundaries, never with silent
   fallback to hosted pages.
4. Keep the current app as rollback until installed local dogfood is verified.

