#!/usr/bin/env python3
"""Re-import from a Cell Platform-style source tree (read-only). For maintainers only."""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/path/to/cell-platform")
DST = Path(__file__).resolve().parents[1]

REPLACEMENTS = [
    (r"cdp-agent-loop-runbook", "agentic-loop-runbook"),
    (r"cdp-agent-loop", "agentic-loop"),
    (r"cdp-orchestrator", "agentic-loop-orchestrator"),
    (r"cdp-springboot-default", "springboot-default"),
    (r"cdp-pr-code-review", "pr-code-review"),
    (r"cdp-service-quality-drill", "service-quality-drill"),
    (r"cba-terraform-standards", "terraform-standards"),
    (r"docs/agent-loop/", "loop-kit/"),
    (r"docs/agent-loop", "loop-kit"),
    (r"GM-DATA-ENG", "<org>"),
    (r"SDEGCCP-\d+", "PROJ-123"),
    (r"com\.gm\.cdp", "com.example.app"),
    (r"CDP Agent Loop", "Agentic Loop Engineering Kit"),
]


def genericize(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = re.sub(old, new, text)
    return text


def main() -> None:
    if not SRC.exists():
        print(f"Source not found: {SRC}", file=sys.stderr)
        sys.exit(1)
    loop_src = SRC / "docs/agent-loop"
    loop_dst = DST / "loop-kit"
    if loop_dst.exists():
        shutil.rmtree(loop_dst)
    shutil.copytree(loop_src, loop_dst)
    for p in loop_dst.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".yaml", ".yml", ".mdc"}:
            p.write_text(genericize(p.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"Imported from {SRC} into {DST}")


if __name__ == "__main__":
    main()
