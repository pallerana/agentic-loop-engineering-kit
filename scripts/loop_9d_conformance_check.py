#!/usr/bin/env python3
"""Phase 9d control-plane conformance — warning-first; --strict to fail."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

VERBATIM_START = "<!-- PHASE-9D-TRANSITIONS:verbatim:start"
VERBATIM_END = "<!-- PHASE-9D-TRANSITIONS:verbatim:end -->"

FILES = {
    "orchestrator": ROOT / ".cursor/agents/agentic-loop-orchestrator.md",
    "runbook": ROOT / ".cursor/skills/agentic-loop/SKILL.md",
    "gates": ROOT / "loop-kit/GATES.md",
    "help": ROOT / ".cursor/commands/agentic-loop.md",
    "contracts_readme": ROOT / "loop-kit/contracts/README.md",
    # "wiki_status": omitted in OSS kit
    # "wiki_status": ROOT / "docs/wiki/your-loop-wiki.md",
    "schema": ROOT / "loop-kit/contracts/loop-learning-v1.schema.json",
    "index": ROOT / "docs/loop-learnings/index.json",
    "applied_dir": ROOT / "docs/loop-learnings/.applied",
}

NON_ALLOWLIST_CHECKS = frozenset({"schema_parseable", "index_drift"})


def extract_verbatim_block(text: str) -> str | None:
    start = text.find(VERBATIM_START)
    end = text.find(VERBATIM_END)
    if start == -1 or end == -1 or end < start:
        return None
    return text[start : end + len(VERBATIM_END)].strip()


def load_allowlist(path: Path) -> dict[str, date]:
    entries: dict[str, date] = {}
    if not path.is_file():
        return entries
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            print(f"allowlist parse error (need check_id | reason | YYYY-MM-DD): {line}", file=sys.stderr)
            sys.exit(2)
        check_id, _reason, expiry_s = parts[0], parts[1], parts[2]
        try:
            expiry = datetime.strptime(expiry_s, "%Y-%m-%d").date()
        except ValueError:
            print(f"allowlist invalid expiry for {check_id}: {expiry_s}", file=sys.stderr)
            sys.exit(2)
        entries[check_id] = expiry
    return entries


def warn_or_fail(
    check_id: str,
    message: str,
    *,
    strict: bool,
    allowlist: dict[str, date],
    today: date,
) -> bool:
    if check_id in allowlist:
        expiry = allowlist[check_id]
        if expiry < today:
            pass  # expired — not suppressed
        else:
            days_left = (expiry - today).days
            if days_left <= 7:
                print(f"NOTE: allowlist {check_id} expires {expiry} ({days_left}d left)")
            return False
    line = f"[{check_id}] {message}"
    if strict:
        print(f"FAIL {line}", file=sys.stderr)
        return True
    print(f"WARN {line}")
    return False


def check_result_codes(strict: bool, allowlist: dict[str, date], today: date) -> bool:
    failed = False
    for name, path in (("contracts_readme", FILES["contracts_readme"]), ("gates", FILES["gates"])):
        text = path.read_text(encoding="utf-8")
        for code in ("NO_LEARNINGS", "PENDING_APPROVAL", "PATH_NOT_ALLOWED"):
            if code not in text:
                failed |= warn_or_fail(
                    "result_codes",
                    f"{name} missing {code}",
                    strict=strict,
                    allowlist=allowlist,
                    today=today,
                )
        if "dry-run" in text.lower() and "PENDING_APPROVAL" not in text:
            failed |= warn_or_fail(
                "result_codes",
                f"{name} missing dry-run → PENDING_APPROVAL",
                strict=strict,
                allowlist=allowlist,
                today=today,
            )
    readme = FILES["contracts_readme"].read_text(encoding="utf-8")
    if "`PENDING_APPROVAL`" not in readme or "dry-run" not in readme.lower():
        failed |= warn_or_fail(
            "result_codes",
            "contracts README must document dry-run → PENDING_APPROVAL",
            strict=strict,
            allowlist=allowlist,
            today=today,
        )
    return failed


def check_orchestrator_9d(strict: bool, allowlist: dict[str, date], today: date) -> bool:
    text = FILES["orchestrator"].read_text(encoding="utf-8")
    failed = False
    for kw in ("9d", "STOP", "PENDING_APPROVAL"):
        if kw not in text:
            failed |= warn_or_fail(
                "orchestrator_9d",
                f"orchestrator missing {kw}",
                strict=strict,
                allowlist=allowlist,
                today=today,
            )
    return failed


def check_verbatim_parity(
    check_id: str,
    mirror_path: Path,
    strict: bool,
    allowlist: dict[str, date],
    today: date,
) -> bool:
    orch_block = extract_verbatim_block(FILES["orchestrator"].read_text(encoding="utf-8"))
    mirror_block = extract_verbatim_block(mirror_path.read_text(encoding="utf-8"))
    if orch_block is None:
        return warn_or_fail(
            check_id,
            "orchestrator missing PHASE-9D-TRANSITIONS verbatim block",
            strict=strict,
            allowlist=allowlist,
            today=today,
        )
    if mirror_block is None:
        return warn_or_fail(
            check_id,
            f"{mirror_path.name} missing verbatim block",
            strict=strict,
            allowlist=allowlist,
            today=today,
        )
    if orch_block != mirror_block:
        return warn_or_fail(
            check_id,
            f"{mirror_path.name} verbatim block differs from orchestrator",
            strict=strict,
            allowlist=allowlist,
            today=today,
        )
    return False


def check_gates_parity(strict: bool, allowlist: dict[str, date], today: date) -> bool:
    return check_verbatim_parity("gates_parity", FILES["gates"], strict, allowlist, today)


def check_wiki_status(strict: bool, allowlist: dict[str, date], today: date) -> bool:
    path = FILES.get("wiki_status")
    if path is None:
        return False
    text = path.read_text(encoding="utf-8")
    if re.search(r"Phase 9d.*Pending", text, re.I) and re.search(
        r"Phase 9d.*Implemented", text, re.I
    ):
        return warn_or_fail(
            "wiki_status",
            "current-status.md has contradictory Pending vs Implemented for Phase 9d",
            strict=strict,
            allowlist=allowlist,
            today=today,
        )
    return False


def check_schema_parseable(strict: bool, allowlist: dict[str, date], today: date) -> bool:
    try:
        json.loads(FILES["schema"].read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return warn_or_fail(
            "schema_parseable",
            f"schema not parseable: {exc}",
            strict=strict,
            allowlist={},
            today=today,
        )
    return False


def check_index_drift(strict: bool, allowlist: dict[str, date], today: date) -> bool:
    applied = FILES["applied_dir"]
    if not applied.is_dir():
        return False
    markers = list(applied.glob("*.applied"))
    if not markers:
        return False
    index_path = FILES["index"]
    entries = []
    if index_path.is_file():
        entries = json.loads(index_path.read_text(encoding="utf-8")).get("entries", [])
    contract_paths = {e.get("contract_path") for e in entries}
    failed = False
    for marker in markers:
        name = marker.read_text(encoding="utf-8").strip()
        if not any(name in (cp or "") for cp in contract_paths):
            failed |= warn_or_fail(
                "index_drift",
                f".applied marker {marker.name} has no matching index.json entry",
                strict=strict,
                allowlist={},
                today=today,
            )
    return failed


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 9d conformance check")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument(
        "--allowlist",
        default=str(ROOT / "loop-kit/loop-9d-conformance-allowlist.txt"),
        help="Allowlist file (check_id | reason | YYYY-MM-DD)",
    )
    args = parser.parse_args()
    allowlist_path = Path(args.allowlist)
    allowlist = load_allowlist(allowlist_path)
    today = date.today()

    failed = False
    failed |= check_result_codes(args.strict, allowlist, today)
    failed |= check_orchestrator_9d(args.strict, allowlist, today)
    failed |= check_verbatim_parity("runbook_parity", FILES["runbook"], args.strict, allowlist, today)
    failed |= check_verbatim_parity("help_parity", FILES["help"], args.strict, allowlist, today)
    failed |= check_gates_parity(args.strict, allowlist, today)
    failed |= check_wiki_status(args.strict, allowlist, today)
    failed |= check_schema_parseable(args.strict, allowlist, today)
    failed |= check_index_drift(args.strict, allowlist, today)

    if failed:
        sys.exit(1)
    print("loop_9d_conformance_check: ok")
    sys.exit(0)


if __name__ == "__main__":
    main()
