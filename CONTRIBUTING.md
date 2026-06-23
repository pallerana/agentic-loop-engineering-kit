# Contributing — OSS export maintenance

Exports are produced from the private Cell Platform workspace using the **export-orchestrator** skill.

## Maintainer workflow

1. Run Stage 1 tooling tests in Cell Platform: `pytest .cursor/skills/export-orchestrator/scripts/test_export_*.py`
2. `/export-agentic-loop` → orchestrator diff review → approve scope
3. Stage 2 export + Stage 3 ship (human-gated PR/merge)

Do not hand-edit sanitized paths without updating `export_manifest.yaml` in Cell Platform.
