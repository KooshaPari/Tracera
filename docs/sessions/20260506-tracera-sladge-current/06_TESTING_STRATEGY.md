# Testing Strategy

## Commands

- `git diff --check`
- `rg -n "sladge|AI Slop" README.md`
- `git lfs status`
- `python3 Tracera/validate_governance.py` was attempted and is unavailable in
  the current checkout shape.

## Notes

The change does not touch application code. Broad package, Docker, frontend, and
workflow validation is kept out of scope because canonical local changes and LFS
checkout warnings are unrelated to this README/session-doc badge lane.
