#!/usr/bin/env python3
"""Phase 9d apply-engine coverage gate — 100% effective line coverage with allowlist."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLY_SCRIPT = (
    ROOT / ".cursor/skills/agentic-loop/scripts/apply_loop_learning.py"
)
TEST_SCRIPT = (
    ROOT / ".cursor/skills/agentic-loop/scripts/test_apply_loop_learning.py"
)
DEFAULT_ALLOWLIST = ROOT / "loop-kit/loop-9d-coverage-allowlist.txt"

REQUIRED_RESULT_CODES = (
    "PENDING_APPROVAL",
    "APPLY_SUCCESS",
    "IDEMPOTENT_SKIP",
    "SCHEMA_INVALID",
    "PATH_NOT_ALLOWED",
    "REPO_MISMATCH",
    "RATIONALE_MISSING",
    "ORPHAN_PROMOTION",
    "LEARNING_NOT_APPLIED",
    "USER_REJECTED",
)


def load_allowlist(path: Path) -> dict[int, date]:
    """Map line number -> expiry date."""
    entries: dict[int, date] = {}
    if not path.is_file():
        return entries
    today = date.today()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            print(f"allowlist parse error (need line | reason | YYYY-MM-DD): {line}", file=sys.stderr)
            sys.exit(2)
        line_spec, _reason, expiry_s = parts[0], parts[1], parts[2]
        try:
            expiry = datetime.strptime(expiry_s, "%Y-%m-%d").date()
        except ValueError:
            print(f"allowlist invalid expiry for {line_spec}: {expiry_s}", file=sys.stderr)
            sys.exit(2)
        if "-" in line_spec:
            start_s, end_s = line_spec.split("-", 1)
            start, end = int(start_s), int(end_s)
            for ln in range(start, end + 1):
                entries[ln] = expiry
        else:
            entries[int(line_spec)] = expiry
        if (expiry - today).days > 14:
            print(
                f"WARN: allowlist entry {line_spec} expires >14 days out ({expiry})",
                file=sys.stderr,
            )
    return entries


def active_allowlist(allowlist: dict[int, date], today: date) -> set[int]:
    return {ln for ln, exp in allowlist.items() if exp >= today}


def run_tests_with_coverage() -> None:
    scripts_dir = APPLY_SCRIPT.parent
    env = os.environ.copy()
    env.setdefault("CURSOR_PROJECT_DIR", str(ROOT))
    cmd = [
        sys.executable,
        "-m",
        "coverage",
        "run",
        "--source",
        "apply_loop_learning",
        "-m",
        "unittest",
        "test_apply_loop_learning",
        "-q",
    ]
    result = subprocess.run(cmd, cwd=scripts_dir, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)


def coverage_json() -> dict:
    scripts_dir = APPLY_SCRIPT.parent
    out_path = scripts_dir / ".coverage.json.tmp"
    cmd = [
        sys.executable,
        "-m",
        "coverage",
        "json",
        "-o",
        str(out_path),
        "--include",
        "apply_loop_learning.py",
    ]
    result = subprocess.run(cmd, cwd=scripts_dir, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    data = json.loads(out_path.read_text(encoding="utf-8"))
    out_path.unlink(missing_ok=True)
    return data


def check_pne_matrix(test_text: str) -> list[str]:
    missing: list[str] = []
    for code in REQUIRED_RESULT_CODES:
        if code not in test_text:
            missing.append(code)
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 9d apply-engine coverage check")
    parser.add_argument(
        "--allowlist",
        default=str(DEFAULT_ALLOWLIST),
        help="Coverage allowlist (line_or_range | reason | YYYY-MM-DD)",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Use existing .coverage data (must run tests first)",
    )
    args = parser.parse_args()

    allowlist_path = Path(args.allowlist)
    allowlist = load_allowlist(allowlist_path)
    today = date.today()
    allowed_lines = active_allowlist(allowlist, today)

    if not args.skip_tests:
        run_tests_with_coverage()

    data = coverage_json()
    files = data.get("files", {})
    apply_key = None
    for key in files:
        if key.endswith("apply_loop_learning.py"):
            apply_key = key
            break
    if not apply_key:
        print("FAIL: no coverage data for apply_loop_learning.py", file=sys.stderr)
        sys.exit(1)

    file_data = files[apply_key]
    missing_lines = [
        int(ln)
        for ln in file_data.get("missing_lines", [])
        if int(ln) not in allowed_lines
    ]
    excluded = [
        int(ln)
        for ln in file_data.get("missing_lines", [])
        if int(ln) in allowed_lines
    ]

    test_text = TEST_SCRIPT.read_text(encoding="utf-8")
    pne_missing = check_pne_matrix(test_text)

    failed = False
    if missing_lines:
        failed = True
        print(
            f"FAIL: uncovered lines in apply_loop_learning.py: {missing_lines}",
            file=sys.stderr,
        )
    if pne_missing:
        failed = True
        print(
            f"FAIL: missing P/N/E test assertions for: {', '.join(pne_missing)}",
            file=sys.stderr,
        )
    if allowed_lines and excluded:
        print(f"NOTE: {len(excluded)} line(s) covered by active allowlist")

    if failed:
        sys.exit(1)

    pct = file_data.get("summary", {}).get("percent_covered", 0)
    print(
        f"loop_9d_coverage_check: ok "
        f"(effective 100%, raw {pct:.1f}%, allowlisted {len(excluded)} line(s))"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
