#!/usr/bin/env python3
"""Phase 9d — apply TOON loop-learning contracts. See loop-kit/contracts/README.md."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

IMPORT_ERROR_STDERR = (
    "validation error: jsonschema not installed; "
    "run: pip install -r scripts/requirements-loop-9d.txt"
)
FILENAME_ERROR_STDERR = (
    "validation error: contract filename must be <JIRA>-<UTC-ts>-learning|promotion"
)

ALLOWED_PATH = re.compile(
    r"^(loop-kit/|\.cursor/skills/|\.cursor/rules/|docs/loop-learnings/)"
)
MAX_QUIRKS = 5


class ValidationError(Exception):
    def __init__(self, message: str, code: str = "SCHEMA_INVALID") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


def workspace_root() -> Path:
    script = Path(__file__).resolve()
    return Path(os.environ.get("CURSOR_PROJECT_DIR", script.parents[4]))


def emit(code: str, exit_code: int = 0) -> None:
    print(f"LOOP_LEARNING_RESULT={code}")
    sys.exit(exit_code)


def emit_validation_error(err: ValidationError) -> None:
    print(f"validation error: {err.message}", file=sys.stderr)
    exit_code = 2 if err.code == "PATH_NOT_ALLOWED" else 1
    emit(err.code, exit_code)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def detect_toon_validator() -> list[str] | None:
    env = os.environ.get("LOOP_TOON_VALIDATOR", "").strip()
    if env:
        parts = env.split()
        if parts and (shutil.which(parts[0]) or Path(parts[0]).is_file()):
            return parts
    if shutil.which("toon"):
        try:
            result = subprocess.run(
                ["toon", "validate", "--version"],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                return ["toon", "validate"]
        except (OSError, subprocess.TimeoutExpired):
            pass
    return None


def _is_path_schema_error(error_path: tuple[str | int, ...]) -> bool:
    if not error_path:
        return False
    if error_path[0] == "rationale_path":
        return True
    if len(error_path) >= 3 and error_path[0] == "targets" and error_path[2] == "path":
        return True
    if error_path[-1] == "path":
        return True
    return False


def classify_jsonschema_error(exc: Exception) -> str:
    path = getattr(exc, "absolute_path", None) or getattr(exc, "path", ())
    if _is_path_schema_error(tuple(path)):
        return "PATH_NOT_ALLOWED"
    return "SCHEMA_INVALID"


def validate_contract_schema(root: Path, contract: dict, contract_path: Path) -> None:
    toon_cmd = detect_toon_validator()
    if toon_cmd:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(contract, tmp)
            tmp_path = tmp.name
        schema_path = root / "loop-kit/contracts/loop-learning-v1.schema.json"
        try:
            result = subprocess.run(
                [*toon_cmd, tmp_path, str(schema_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                msg = (result.stderr or result.stdout or "TOON validator failed").strip()
                if "path" in msg.lower() and "allow" in msg.lower():
                    raise ValidationError(msg, "PATH_NOT_ALLOWED")
                raise ValidationError(msg, "SCHEMA_INVALID")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
        return

    try:
        import jsonschema
        from jsonschema import ValidationError as JsonSchemaValidationError
    except ImportError:
        print(IMPORT_ERROR_STDERR, file=sys.stderr)
        emit("SCHEMA_INVALID", 1)

    schema_path = root / "loop-kit/contracts/loop-learning-v1.schema.json"
    schema = load_json(schema_path)
    try:
        jsonschema.validate(instance=contract, schema=schema)
    except JsonSchemaValidationError as exc:
        code = classify_jsonschema_error(exc)
        raise ValidationError(exc.message, code) from exc


def validate_contract_business(contract: dict, contract_path: Path) -> None:
    parsed = parse_contract_filename(contract_path)
    if not parsed:
        raise ValidationError(
            "contract filename must be <JIRA>-<UTC-ts>-learning|promotion",
            "SCHEMA_INVALID",
        )
    jira, _utc_ts, kind = parsed
    if contract.get("jira_key") != jira:
        raise ValidationError("jira_key does not match contract filename", "SCHEMA_INVALID")
    mode = contract.get("mode")
    if mode == "loop_learning" and kind != "learning":
        raise ValidationError(
            "contract filename must end with -learning for loop_learning mode",
            "SCHEMA_INVALID",
        )
    if mode == "promotion_proposal" and kind != "promotion":
        raise ValidationError(
            "contract filename must end with -promotion for promotion_proposal mode",
            "SCHEMA_INVALID",
        )

    rationale = contract.get("rationale_path", "")
    if rationale and not ALLOWED_PATH.match(rationale):
        raise ValidationError("rationale_path not allowed", "PATH_NOT_ALLOWED")
    for i, t in enumerate(contract.get("targets", [])):
        path = t.get("path", "")
        if path and not ALLOWED_PATH.match(path):
            raise ValidationError(f"targets[{i}] path not allowed", "PATH_NOT_ALLOWED")


def parse_contract_filename(contract_path: Path) -> tuple[str, str, str] | None:
    name = contract_path.stem
    m = re.match(r"^([A-Z]+-\d+)-(\d{8}T\d{6}Z)-(learning|promotion)$", name)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def sibling_learning_path(root: Path, repo: str, jira: str, utc_ts: str) -> Path:
    return root / "docs/loop-learnings/contracts" / repo / f"{jira}-{utc_ts}-learning.json"


def learning_applied_marker(root: Path, jira: str, utc_ts: str) -> Path:
    return root / "docs/loop-learnings" / ".applied" / f"{jira}-{utc_ts}.applied"


def marker_id(fingerprint: str, run: int) -> str:
    return f"LOOP-LEARNING:{fingerprint}:{run}"


def marker_exists(target_file: Path, fp: str, run: int) -> bool:
    if not target_file.is_file():
        return False
    mid = marker_id(fp, run)
    return f"<!-- {mid} -->" in target_file.read_text(encoding="utf-8")


def count_runs(root: Path, fingerprint: str, scope: str) -> int:
    index_path = root / "docs/loop-learnings" / "index.json"
    if not index_path.is_file():
        return 0
    for row in load_json(index_path).get("entries", []):
        if row.get("fingerprint") == fingerprint and row.get("scope") == scope:
            return int(row.get("runs", 0))
    return 0


def append_index(root: Path, entry: dict) -> None:
    index_path = root / "docs/loop-learnings" / "index.json"
    data = load_json(index_path) if index_path.is_file() else {"entries": []}
    entries = data.setdefault("entries", [])
    for row in entries:
        if row.get("fingerprint") == entry["fingerprint"] and row.get("scope") == entry["scope"]:
            row.update(entry)
            break
    else:
        entries.append(entry)
    index_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    _sync_readme_index(root, data)


def reconcile_index_from_applied(root: Path) -> bool:
    """Rebuild index.json from .applied markers + contracts. Returns True if changed."""
    applied_dir = root / "docs/loop-learnings" / ".applied"
    if not applied_dir.is_dir():
        return False
    entries: list[dict] = []
    for marker in sorted(applied_dir.glob("*.applied")):
        m = re.match(r"^([A-Z]+-\d+)-(\d{8}T\d{6}Z)$", marker.stem)
        if not m:
            continue
        jira, utc_ts = m.group(1), m.group(2)
        contract_name = marker.read_text(encoding="utf-8").strip()
        for contract_path in root.glob(f"docs/loop-learnings/contracts/**/{contract_name}"):
            if not contract_path.is_file():
                continue
            contract = load_json(contract_path)
            fp = contract["fingerprint"]
            scope = contract["scope"]
            runs = count_runs(root, fp, scope)
            if runs == 0:
                runs = 1
            entries.append(
                {
                    "fingerprint": fp,
                    "scope": scope,
                    "profile": contract["profile"],
                    "repo": contract["repo"],
                    "runs": runs,
                    "promoted": contract.get("mode") == "promotion_proposal",
                    "rationale_path": contract["rationale_path"],
                    "contract_path": str(contract_path.relative_to(root)),
                }
            )
            break
    index_path = root / "docs/loop-learnings" / "index.json"
    existing = load_json(index_path) if index_path.is_file() else {"entries": []}
    if existing.get("entries") == entries:
        return False
    data = {"entries": entries}
    index_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    _sync_readme_index(root, data)
    return True


def _sync_readme_index(root: Path, data: dict) -> None:
    readme = root / "docs/loop-learnings/README.md"
    if not readme.is_file():
        return
    lines = readme.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    in_table = False
    past_sep = False
    for line in lines:
        if line.startswith("| fingerprint |"):
            in_table = True
            out.append(line)
            continue
        if in_table and line.startswith("|---"):
            out.append(line)
            past_sep = True
            continue
        if in_table and past_sep and line.startswith("|"):
            continue
        if in_table and past_sep and not line.startswith("|"):
            in_table = False
            past_sep = False
            for e in data.get("entries", []):
                out.append(
                    "| {fingerprint} | {scope} | {profile} | {repo} | {runs} | "
                    "{promoted} | {rationale_path} | {contract_path} |".format(
                        fingerprint=e.get("fingerprint", ""),
                        scope=e.get("scope", ""),
                        profile=e.get("profile", ""),
                        repo=e.get("repo", ""),
                        runs=e.get("runs", ""),
                        promoted=e.get("promoted", False),
                        rationale_path=e.get("rationale_path", ""),
                        contract_path=e.get("contract_path", ""),
                    )
                )
            if not data.get("entries"):
                out.append("| _none yet_ | | | | | | | | |")
        out.append(line)
    readme.write_text("\n".join(out) + "\n", encoding="utf-8")


def append_markdown_block(
    target: Path,
    fp: str,
    run: int,
    subsection: str | None,
    lines: list[str],
) -> None:
    mid = marker_id(fp, run)
    block_lines = [f"<!-- {mid} -->"]
    if subsection:
        block_lines.append(f"### {subsection}")
    for line in lines:
        block_lines.append(f"- {line}" if not line.startswith("-") else line)
    block_lines.append(f"<!-- END-{mid} -->")
    block_lines.append("")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as f:
        f.write("\n".join(block_lines))


def load_profile_quirks(root: Path, profile_id: str) -> list[str]:
    path = root / "loop-kit/profiles" / f"{profile_id}.yaml"
    quirks: list[str] = []
    in_quirks = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "known_quirks:":
            in_quirks = True
            continue
        if in_quirks:
            if line.startswith("  - "):
                quirks.append(line[4:].strip().strip('"').strip("'"))
            elif not line.startswith("  "):
                in_quirks = False
    return quirks


def write_profile_quirks(root: Path, profile_id: str, quirks: list[str]) -> None:
    path = root / "loop-kit/profiles" / f"{profile_id}.yaml"
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == "known_quirks:":
            out.append(lines[i])
            for q in quirks:
                out.append(f"  - {q}")
            i += 1
            while i < len(lines) and lines[i].startswith("  - "):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def get_pattern_doc(root: Path, profile_id: str) -> Path | None:
    path = root / "loop-kit/profiles" / f"{profile_id}.yaml"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("pattern_doc:"):
            val = line.split(":", 1)[1].strip()
            if val in ("null", "~", ""):
                return None
            return root / val
    return None


def upsert_known_quirk(
    root: Path,
    profile_id: str,
    summary: str,
    pattern_doc: Path | None,
) -> None:
    quirks = load_profile_quirks(root, profile_id)
    if summary in quirks:
        return
    if len(quirks) >= MAX_QUIRKS:
        oldest = quirks.pop(0)
        if pattern_doc and oldest not in pattern_doc.read_text(encoding="utf-8"):
            append_markdown_block(
                pattern_doc,
                "rotated-quirk",
                count_runs(root, "rotated-quirk", "single-repo") + 1,
                "Known Quirks (rotated from profile)",
                [oldest],
            )
    quirks.append(summary)
    write_profile_quirks(root, profile_id, quirks)


def apply_loop_learning(root: Path, contract: dict, next_run: int) -> None:
    fp = contract["fingerprint"]
    pattern_doc = get_pattern_doc(root, contract["profile"])
    for t in contract.get("targets", []):
        if t.get("action") != "append_markdown" or not t.get("lines"):
            continue
        target = root / t["path"]
        if marker_exists(target, fp, next_run):
            emit("IDEMPOTENT_SKIP", 0)
        append_markdown_block(
            target, fp, next_run, t.get("subsection"), t.get("lines", [])
        )
    for a in contract.get("actions", []):
        if a.get("action") == "upsert_known_quirk":
            upsert_known_quirk(root, a["profile"], a["summary"], pattern_doc)


def print_summary(contract: dict, next_run: int, contract_path: Path | str) -> None:
    print("--- loop learning approval summary ---")
    print(f"jira_key: {contract['jira_key']}")
    print(f"mode: {contract['mode']}")
    print(f"fingerprint: {contract['fingerprint']}")
    print(f"scope: {contract['scope']}")
    print(f"repo: {contract['repo']}")
    print(f"run: {next_run}")
    print(f"contract: {contract_path}")
    print(f"targets: {len(contract.get('targets', []))}")
    print(f"actions: {len(contract.get('actions', []))}")
    print("------------------------------------")


def write_staging_summary(
    root: Path, contract: dict, contract_rel: Path, next_run: int
) -> None:
    parsed = parse_contract_filename(root / contract_rel)
    if not parsed:
        return
    jira, utc_ts, _ = parsed
    staging_dir = root / "docs/loop-learnings/staging"
    staging_dir.mkdir(parents=True, exist_ok=True)
    staging_path = staging_dir / f"{jira}-{utc_ts}-summary.md"
    rows = [
        "| Field | Value |",
        "|-------|-------|",
        f"| jira_key | {contract['jira_key']} |",
        f"| mode | {contract['mode']} |",
        f"| fingerprint | {contract['fingerprint']} |",
        f"| scope | {contract['scope']} |",
        f"| repo | {contract['repo']} |",
        f"| run | {next_run} |",
        f"| contract | {contract_rel} |",
        f"| targets | {len(contract.get('targets', []))} |",
        f"| actions | {len(contract.get('actions', []))} |",
    ]
    staging_path.write_text(
        f"# Loop learning summary — {jira}\n\n" + "\n".join(rows) + "\n",
        encoding="utf-8",
    )


def finish_pending(
    root: Path, contract: dict, contract_rel: Path, next_run: int
) -> None:
    print_summary(contract, next_run, contract_rel)
    write_staging_summary(root, contract, contract_rel, next_run)
    emit("PENDING_APPROVAL", 0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply loop-learning TOON contract")
    parser.add_argument("--contract", required=True)
    parser.add_argument("--repo", help="Active repo dir name")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("decision", nargs="?", choices=["approve", "reject"])
    args = parser.parse_args()

    root = workspace_root()
    rel = Path(args.contract)
    contract_path = rel if rel.is_absolute() else root / rel
    if not contract_path.is_file():
        emit("SCHEMA_INVALID", 1)

    try:
        contract = load_json(contract_path)
    except json.JSONDecodeError:
        emit("SCHEMA_INVALID", 1)

    try:
        validate_contract_schema(root, contract, contract_path)
        validate_contract_business(contract, contract_path)
    except ValidationError as err:
        emit_validation_error(err)

    active_repo = args.repo or contract.get("repo", "")
    if contract.get("repo") != active_repo:
        emit("REPO_MISMATCH", 3)

    rationale = root / contract["rationale_path"]
    if not rationale.is_file():
        emit("RATIONALE_MISSING", 4)

    mode = contract["mode"]
    fp = contract["fingerprint"]
    scope = contract["scope"]
    runs = count_runs(root, fp, scope)
    next_run = runs + 1
    rel_contract = contract_path.relative_to(root)
    parsed = parse_contract_filename(contract_path)

    if mode == "promotion_proposal":
        assert parsed is not None
        jira, utc_ts, _kind = parsed
        if not sibling_learning_path(root, contract["repo"], jira, utc_ts).is_file():
            emit("ORPHAN_PROMOTION", 5)
        if not learning_applied_marker(root, jira, utc_ts).is_file():
            emit("LEARNING_NOT_APPLIED", 6)
        if args.decision == "reject":
            rej = root / "docs/loop-learnings/rejected" / contract["repo"]
            rej.mkdir(parents=True, exist_ok=True)
            shutil.copy2(contract_path, rej / contract_path.name)
            shutil.copy2(rationale, rej / rationale.name)
            emit("USER_REJECTED", 0)
        if args.decision == "approve":
            if args.dry_run:
                finish_pending(root, contract, rel_contract, next_run)
            else:
                dest = root / "docs/loop-learnings/pending-promotion" / scope
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(contract_path, dest / contract_path.name)
                emit("APPLY_SUCCESS", 0)
        else:
            finish_pending(root, contract, rel_contract, next_run)

    if args.decision == "reject":
        rej = root / "docs/loop-learnings/rejected" / contract["repo"]
        rej.mkdir(parents=True, exist_ok=True)
        shutil.copy2(contract_path, rej / contract_path.name)
        shutil.copy2(rationale, rej / rationale.name)
        emit("USER_REJECTED", 0)

    if args.dry_run:
        finish_pending(root, contract, rel_contract, next_run)

    if args.decision == "approve":
        if parsed:
            jira, utc_ts, _ = parsed
            if learning_applied_marker(root, jira, utc_ts).is_file():
                emit("IDEMPOTENT_SKIP", 0)
        apply_loop_learning(root, contract, next_run)
        append_index(
            root,
            {
                "fingerprint": fp,
                "scope": scope,
                "profile": contract["profile"],
                "repo": contract["repo"],
                "runs": next_run,
                "promoted": False,
                "rationale_path": contract["rationale_path"],
                "contract_path": str(rel_contract),
            },
        )
        if parsed:
            jira, utc_ts, _ = parsed
            marker = learning_applied_marker(root, jira, utc_ts)
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text(contract_path.name + "\n", encoding="utf-8")
        emit("APPLY_SUCCESS", 0)

    finish_pending(root, contract, rel_contract, next_run)


if __name__ == "__main__":
    main()
