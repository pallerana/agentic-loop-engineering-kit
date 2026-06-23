#!/usr/bin/env python3
"""Tests for apply_loop_learning.py — Phase 9d hardening."""
from __future__ import annotations

import io
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parent / "apply_loop_learning.py"
ROOT = Path(__file__).resolve().parents[4]

VALID_LEARNING = {
    "contract_version": "1",
    "mode": "loop_learning",
    "jira_key": "PROJ-9999",
    "fingerprint": "test-fingerprint",
    "scope": "single-repo",
    "profile": "my-service",
    "repo": "your-service-api",
    "rationale_path": (
        "docs/loop-learnings/by-repo/your-service-api/"
        "PROJ-9999-20260623T120000Z.md"
    ),
    "targets": [
        {
            "path": "loop-kit/patterns/feature-loop-example.md",
            "action": "append_markdown",
            "subsection": "Test",
            "lines": ["Test learning line."],
        }
    ],
    "actions": [
        {
            "action": "upsert_known_quirk",
            "profile": "my-service",
            "summary": "Test quirk summary",
        }
    ],
}


def load_module():
    spec = importlib.util.spec_from_file_location("apply_loop_learning", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def run_apply(
    root: Path,
    contract_rel: str,
    *extra: str,
    env: dict | None = None,
    repo: str = "your-service-api",
) -> subprocess.CompletedProcess[str]:
    mod = load_module()
    argv = ["apply_loop_learning.py", "--contract", contract_rel, "--repo", repo, *extra]
    run_env = {**os.environ, "CURSOR_PROJECT_DIR": str(root)}
    if env:
        run_env.update(env)
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    exit_code = 0
    with mock.patch.dict(os.environ, run_env, clear=False):
        with mock.patch("sys.argv", argv):
            with mock.patch("sys.stdout", stdout_buf):
                with mock.patch("sys.stderr", stderr_buf):
                    try:
                        mod.main()
                    except SystemExit as exc:
                        exit_code = exc.code if isinstance(exc.code, int) else 1
    return subprocess.CompletedProcess(
        argv, exit_code, stdout_buf.getvalue(), stderr_buf.getvalue()
    )


def seed_workspace(tmp: Path) -> None:
    shutil.copytree(
        ROOT / "loop-kit/contracts",
        tmp / "loop-kit/contracts",
    )
    shutil.copytree(
        ROOT / "loop-kit/profiles",
        tmp / "loop-kit/profiles",
    )
    shutil.copytree(
        ROOT / "loop-kit/patterns",
        tmp / "loop-kit/patterns",
    )
    rationale_dir = (
        tmp
        / "docs/loop-learnings/by-repo/your-service-api"
    )
    rationale_dir.mkdir(parents=True, exist_ok=True)
    (rationale_dir / "PROJ-9999-20260623T120000Z.md").write_text(
        "# Rationale\n", encoding="utf-8"
    )
    contract_dir = (
        tmp
        / "docs/loop-learnings/contracts/your-service-api"
    )
    contract_dir.mkdir(parents=True, exist_ok=True)
    contract_path = contract_dir / "PROJ-9999-20260623T120000Z-learning.json"
    contract_path.write_text(json.dumps(VALID_LEARNING, indent=2) + "\n", encoding="utf-8")
    (tmp / "docs/loop-learnings").mkdir(parents=True, exist_ok=True)
    (tmp / "docs/loop-learnings/index.json").write_text(
        '{"entries": []}\n', encoding="utf-8"
    )
    readme_src = ROOT / "docs/loop-learnings/README.md"
    if readme_src.is_file():
        shutil.copy2(readme_src, tmp / "docs/loop-learnings/README.md")


def result_code(proc: subprocess.CompletedProcess[str]) -> str | None:
    for line in proc.stdout.splitlines():
        if line.startswith("LOOP_LEARNING_RESULT="):
            return line.split("=", 1)[1]
    return None


class ApplyLoopLearningTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        seed_workspace(self.root)
        self.contract_rel = (
            "docs/loop-learnings/contracts/your-service-api/"
            "PROJ-9999-20260623T120000Z-learning.json"
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_validate_only_returns_pending_approval(self) -> None:
        proc = run_apply(self.root, self.contract_rel)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(result_code(proc), "PENDING_APPROVAL")

    def test_dry_run_returns_pending_approval(self) -> None:
        proc = run_apply(self.root, self.contract_rel, "--dry-run")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(result_code(proc), "PENDING_APPROVAL")

    def test_unknown_field_schema_invalid(self) -> None:
        path = self.root / self.contract_rel
        data = json.loads(path.read_text(encoding="utf-8"))
        data["bogus_field"] = True
        path.write_text(json.dumps(data) + "\n", encoding="utf-8")
        proc = run_apply(self.root, self.contract_rel)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(result_code(proc), "SCHEMA_INVALID")

    def test_target_path_not_allowed(self) -> None:
        path = self.root / self.contract_rel
        data = json.loads(path.read_text(encoding="utf-8"))
        data["targets"][0]["path"] = "docs/wiki/forbidden.md"
        path.write_text(json.dumps(data) + "\n", encoding="utf-8")
        proc = run_apply(self.root, self.contract_rel)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(result_code(proc), "PATH_NOT_ALLOWED")

    def test_rationale_path_not_allowed(self) -> None:
        path = self.root / self.contract_rel
        data = json.loads(path.read_text(encoding="utf-8"))
        data["rationale_path"] = "docs/wiki/forbidden.md"
        path.write_text(json.dumps(data) + "\n", encoding="utf-8")
        proc = run_apply(self.root, self.contract_rel)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(result_code(proc), "PATH_NOT_ALLOWED")

    def test_repo_mismatch(self) -> None:
        proc = run_apply(
            self.root,
            self.contract_rel,
            repo="wrong-repo",
        )
        self.assertEqual(proc.returncode, 3)
        self.assertEqual(result_code(proc), "REPO_MISMATCH")

    def test_rationale_missing(self) -> None:
        missing = (
            self.root
            / "docs/loop-learnings/by-repo/your-service-api/"
            "PROJ-9999-20260623T120000Z.md"
        )
        missing.unlink()
        proc = run_apply(self.root, self.contract_rel)
        self.assertEqual(proc.returncode, 4)
        self.assertEqual(result_code(proc), "RATIONALE_MISSING")

    def test_orphan_promotion(self) -> None:
        promo_dir = (
            self.root
            / "docs/loop-learnings/contracts/your-service-api"
        )
        learning = promo_dir / "PROJ-9999-20260623T120000Z-learning.json"
        learning.unlink()
        promo = {
            **VALID_LEARNING,
            "mode": "promotion_proposal",
            "fingerprint": "promo-fp",
            "scope": "profile-family",
            "targets": [],
            "actions": [],
        }
        promo_path = promo_dir / "PROJ-9999-20260623T120000Z-promotion.json"
        promo_path.write_text(json.dumps(promo) + "\n", encoding="utf-8")
        proc = run_apply(self.root, str(promo_path.relative_to(self.root)))
        self.assertEqual(proc.returncode, 5)
        self.assertEqual(result_code(proc), "ORPHAN_PROMOTION")

    def test_learning_not_applied(self) -> None:
        promo_dir = (
            self.root
            / "docs/loop-learnings/contracts/your-service-api"
        )
        learning_path = promo_dir / "PROJ-9999-20260623T120000Z-learning.json"
        promo = {
            **VALID_LEARNING,
            "mode": "promotion_proposal",
            "fingerprint": "promo-fp",
            "scope": "profile-family",
            "targets": [],
            "actions": [],
        }
        promo_path = promo_dir / "PROJ-9999-20260623T120000Z-promotion.json"
        promo_path.write_text(json.dumps(promo) + "\n", encoding="utf-8")
        proc = run_apply(self.root, str(promo_path.relative_to(self.root)))
        self.assertEqual(proc.returncode, 6)
        self.assertEqual(result_code(proc), "LEARNING_NOT_APPLIED")
        _ = learning_path  # sibling exists but no .applied marker

    def test_reapprove_idempotent_skip(self) -> None:
        proc1 = run_apply(self.root, self.contract_rel, "approve")
        self.assertEqual(result_code(proc1), "APPLY_SUCCESS")
        proc2 = run_apply(self.root, self.contract_rel, "approve")
        self.assertEqual(proc2.returncode, 0)
        self.assertEqual(result_code(proc2), "IDEMPOTENT_SKIP")

    def test_mid_apply_marker_idempotent_skip(self) -> None:
        path = self.root / self.contract_rel
        data = json.loads(path.read_text(encoding="utf-8"))
        target_rel = data["targets"][0]["path"]
        target = self.root / target_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "<!-- LOOP-LEARNING:test-fingerprint:1 -->\n", encoding="utf-8"
        )
        proc = run_apply(self.root, self.contract_rel, "approve")
        self.assertEqual(result_code(proc), "IDEMPOTENT_SKIP")

    def test_approve_success(self) -> None:
        proc = run_apply(self.root, self.contract_rel, "approve")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(result_code(proc), "APPLY_SUCCESS")
        index = json.loads(
            (self.root / "docs/loop-learnings/index.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(index["entries"]), 1)
        marker = (
            self.root
            / "docs/loop-learnings/.applied/PROJ-9999-20260623T120000Z.applied"
        )
        self.assertTrue(marker.is_file())

    def test_malformed_contract_filename(self) -> None:
        bad_dir = (
            self.root
            / "docs/loop-learnings/contracts/your-service-api"
        )
        bad_path = bad_dir / "PROJ-9999-badts-learning.json"
        bad_path.write_text(json.dumps(VALID_LEARNING) + "\n", encoding="utf-8")
        proc = run_apply(self.root, str(bad_path.relative_to(self.root)))
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(result_code(proc), "SCHEMA_INVALID")

    def test_jsonschema_import_error_exact_stderr(self) -> None:
        mod = load_module()
        real_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "jsonschema":
                raise ImportError("mocked")
            return real_import(name, globals, locals, fromlist, level)

        stderr_buf = io.StringIO()
        stdout_buf = io.StringIO()
        with mock.patch("builtins.__import__", side_effect=fake_import):
            with mock.patch.object(mod, "detect_toon_validator", return_value=None):
                with mock.patch(
                    "sys.argv",
                    [
                        "apply_loop_learning.py",
                        "--contract",
                        self.contract_rel,
                        "--repo",
                        "your-service-api",
                    ],
                ):
                    os.environ["CURSOR_PROJECT_DIR"] = str(self.root)
                    with mock.patch("sys.stderr", stderr_buf):
                        with mock.patch("sys.stdout", stdout_buf):
                            with self.assertRaises(SystemExit) as ctx:
                                mod.main()
        self.assertEqual(ctx.exception.code, 1)
        self.assertEqual(stderr_buf.getvalue().strip(), mod.IMPORT_ERROR_STDERR)
        self.assertIn("LOOP_LEARNING_RESULT=SCHEMA_INVALID", stdout_buf.getvalue())

    def test_missing_contract_file_schema_invalid(self) -> None:
        proc = run_apply(self.root, "docs/loop-learnings/contracts/missing.json")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(result_code(proc), "SCHEMA_INVALID")

    def test_malformed_json_schema_invalid(self) -> None:
        bad = self.root / "docs/loop-learnings/contracts/bad.json"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text("{not json", encoding="utf-8")
        proc = run_apply(self.root, str(bad.relative_to(self.root)))
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(result_code(proc), "SCHEMA_INVALID")

    def test_user_rejected_learning(self) -> None:
        proc = run_apply(self.root, self.contract_rel, "reject")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(result_code(proc), "USER_REJECTED")
        rejected = (
            self.root
            / "docs/loop-learnings/rejected/your-service-api"
        )
        self.assertTrue((rejected / Path(self.contract_rel).name).is_file())

    def test_promotion_approve_dry_run_pending_approval(self) -> None:
        promo_dir = (
            self.root
            / "docs/loop-learnings/contracts/your-service-api"
        )
        proc1 = run_apply(self.root, self.contract_rel, "approve")
        self.assertEqual(result_code(proc1), "APPLY_SUCCESS")
        promo = {
            **VALID_LEARNING,
            "mode": "promotion_proposal",
            "fingerprint": "promo-fp",
            "scope": "profile-family",
            "targets": [],
            "actions": [],
        }
        promo_path = promo_dir / "PROJ-9999-20260623T120000Z-promotion.json"
        promo_path.write_text(json.dumps(promo) + "\n", encoding="utf-8")
        proc = run_apply(
            self.root,
            str(promo_path.relative_to(self.root)),
            "--dry-run",
            "approve",
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(result_code(proc), "PENDING_APPROVAL")

    def test_promotion_approve_success(self) -> None:
        promo_dir = (
            self.root
            / "docs/loop-learnings/contracts/your-service-api"
        )
        proc1 = run_apply(self.root, self.contract_rel, "approve")
        self.assertEqual(result_code(proc1), "APPLY_SUCCESS")
        promo = {
            **VALID_LEARNING,
            "mode": "promotion_proposal",
            "fingerprint": "promo-fp",
            "scope": "profile-family",
            "targets": [],
            "actions": [],
        }
        promo_path = promo_dir / "PROJ-9999-20260623T120000Z-promotion.json"
        promo_path.write_text(json.dumps(promo) + "\n", encoding="utf-8")
        proc = run_apply(
            self.root, str(promo_path.relative_to(self.root)), "approve"
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(result_code(proc), "APPLY_SUCCESS")
        staged = (
            self.root
            / "docs/loop-learnings/pending-promotion/profile-family"
            / promo_path.name
        )
        self.assertTrue(staged.is_file())

    def test_user_rejected_promotion(self) -> None:
        promo_dir = (
            self.root
            / "docs/loop-learnings/contracts/your-service-api"
        )
        proc1 = run_apply(self.root, self.contract_rel, "approve")
        self.assertEqual(result_code(proc1), "APPLY_SUCCESS")
        promo = {
            **VALID_LEARNING,
            "mode": "promotion_proposal",
            "fingerprint": "promo-fp",
            "scope": "profile-family",
            "targets": [],
            "actions": [],
        }
        promo_path = promo_dir / "PROJ-9999-20260623T120000Z-promotion.json"
        promo_path.write_text(json.dumps(promo) + "\n", encoding="utf-8")
        proc = run_apply(
            self.root, str(promo_path.relative_to(self.root)), "reject"
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(result_code(proc), "USER_REJECTED")


class ApplyLoopLearningUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        seed_workspace(self.root)
        self.mod = load_module()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_reconcile_index_from_applied(self) -> None:
        proc = run_apply(self.root, (
            "docs/loop-learnings/contracts/your-service-api/"
            "PROJ-9999-20260623T120000Z-learning.json"
        ), "approve")
        self.assertEqual(result_code(proc), "APPLY_SUCCESS")
        changed = self.mod.reconcile_index_from_applied(self.root)
        self.assertFalse(changed)
        index_path = self.root / "docs/loop-learnings/index.json"
        index_path.write_text('{"entries": []}\n', encoding="utf-8")
        changed = self.mod.reconcile_index_from_applied(self.root)
        self.assertTrue(changed)

    def test_upsert_known_quirk_no_duplicate(self) -> None:
        profile = self.root / "loop-kit/profiles/my-service.yaml"
        text = profile.read_text(encoding="utf-8")
        if "Test quirk summary" not in text:
            quirks_line = "known_quirks:"
            self.mod.upsert_known_quirk(
                self.root, "my-service", "Test quirk summary", None
            )
            after = profile.read_text(encoding="utf-8")
            self.assertEqual(after.count("Test quirk summary"), 1)

    def test_write_staging_summary_skips_bad_filename(self) -> None:
        contract = dict(VALID_LEARNING)
        bad_rel = Path("docs/loop-learnings/contracts/bad-name.json")
        self.mod.write_staging_summary(self.root, contract, bad_rel, 1)
        staging = self.root / "docs/loop-learnings/staging"
        if staging.exists():
            self.assertEqual(list(staging.glob("*.md")), [])

    def test_main_invocation(self) -> None:
        contract_rel = (
            "docs/loop-learnings/contracts/your-service-api/"
            "PROJ-9999-20260623T120000Z-learning.json"
        )
        with mock.patch(
            "sys.argv",
            [
                "apply_loop_learning.py",
                "--contract",
                contract_rel,
                "--repo",
                "your-service-api",
            ],
        ):
            os.environ["CURSOR_PROJECT_DIR"] = str(self.root)
            with self.assertRaises(SystemExit) as ctx:
                self.mod.main()
            self.assertEqual(ctx.exception.code, 0)

    def test_classify_jsonschema_error_paths(self) -> None:
        self.assertTrue(self.mod._is_path_schema_error(("rationale_path",)))
        self.assertTrue(
            self.mod._is_path_schema_error(("targets", 0, "path"))
        )
        self.assertTrue(self.mod._is_path_schema_error(("foo", "path")))
        self.assertFalse(self.mod._is_path_schema_error(()))
        self.assertFalse(self.mod._is_path_schema_error(("jira_key",)))

    def test_detect_toon_validator_env(self) -> None:
        fake = self.root / "fake-toon"
        fake.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        fake.chmod(0o755)
        with mock.patch.dict(os.environ, {"LOOP_TOON_VALIDATOR": str(fake)}):
            self.assertEqual(self.mod.detect_toon_validator(), [str(fake)])

    def test_validate_contract_schema_toon_success(self) -> None:
        contract_path = self.root / self.contract_rel_for_tests()
        with mock.patch.object(
            self.mod, "detect_toon_validator", return_value=["true"]
        ):
            with mock.patch("subprocess.run") as mrun:
                mrun.return_value = subprocess.CompletedProcess([], 0, "", "")
                self.mod.validate_contract_schema(
                    self.root, VALID_LEARNING, contract_path
                )
                self.assertTrue(mrun.called)

    def test_validate_contract_schema_toon_path_error(self) -> None:
        contract_path = self.root / self.contract_rel_for_tests()
        with mock.patch.object(
            self.mod, "detect_toon_validator", return_value=["true"]
        ):
            with mock.patch("subprocess.run") as mrun:
                mrun.return_value = subprocess.CompletedProcess(
                    [], 1, "", "path not allowed"
                )
                with self.assertRaises(self.mod.ValidationError) as ctx:
                    self.mod.validate_contract_schema(
                        self.root, VALID_LEARNING, contract_path
                    )
                self.assertEqual(ctx.exception.code, "PATH_NOT_ALLOWED")

    def test_validate_contract_schema_toon_schema_error(self) -> None:
        contract_path = self.root / self.contract_rel_for_tests()
        with mock.patch.object(
            self.mod, "detect_toon_validator", return_value=["true"]
        ):
            with mock.patch("subprocess.run") as mrun:
                mrun.return_value = subprocess.CompletedProcess(
                    [], 1, "", "invalid schema"
                )
                with self.assertRaises(self.mod.ValidationError) as ctx:
                    self.mod.validate_contract_schema(
                        self.root, VALID_LEARNING, contract_path
                    )
                self.assertEqual(ctx.exception.code, "SCHEMA_INVALID")

    def test_jira_key_filename_mismatch(self) -> None:
        path = self.root / self.contract_rel_for_tests()
        data = json.loads(path.read_text(encoding="utf-8"))
        data["jira_key"] = "PROJ-0001"
        path.write_text(json.dumps(data) + "\n", encoding="utf-8")
        proc = run_apply(self.root, str(path.relative_to(self.root)))
        self.assertEqual(result_code(proc), "SCHEMA_INVALID")

    def test_promotion_validate_only_pending_approval(self) -> None:
        promo_path = self._seed_promotion_contract()
        proc = run_apply(self.root, str(promo_path.relative_to(self.root)))
        self.assertEqual(result_code(proc), "PENDING_APPROVAL")

    def test_append_index_updates_existing_entry(self) -> None:
        contract_rel = self.contract_rel_for_tests()
        proc1 = run_apply(self.root, contract_rel, "approve")
        self.assertEqual(result_code(proc1), "APPLY_SUCCESS")
        proc2 = run_apply(self.root, contract_rel)
        self.assertEqual(result_code(proc2), "PENDING_APPROVAL")
        index = json.loads(
            (self.root / "docs/loop-learnings/index.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(index["entries"]), 1)

    def test_reconcile_skips_bad_marker(self) -> None:
        applied = self.root / "docs/loop-learnings/.applied"
        applied.mkdir(parents=True, exist_ok=True)
        (applied / "bad-marker.applied").write_text("x\n", encoding="utf-8")
        self.assertFalse(self.mod.reconcile_index_from_applied(self.root))

    def test_sync_readme_on_approve(self) -> None:
        contract_rel = self.contract_rel_for_tests()
        run_apply(self.root, contract_rel, "approve")
        readme = (self.root / "docs/loop-learnings/README.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("test-fingerprint", readme)

    def test_apply_skips_target_without_lines(self) -> None:
        path = self.root / self.contract_rel_for_tests()
        data = json.loads(path.read_text(encoding="utf-8"))
        data["targets"] = [{"path": data["targets"][0]["path"], "action": "append_markdown"}]
        path.write_text(json.dumps(data) + "\n", encoding="utf-8")
        proc = run_apply(self.root, str(path.relative_to(self.root)), "approve")
        self.assertEqual(result_code(proc), "APPLY_SUCCESS")

    def test_quirk_rotation_at_capacity(self) -> None:
        profile = self.root / "loop-kit/profiles/my-service.yaml"
        lines = profile.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        replaced = False
        for line in lines:
            if line.strip() == "known_quirks:":
                out.append(line)
                for i in range(5):
                    out.append(f"  - old-quirk-{i}")
                replaced = True
            elif replaced and line.startswith("  - "):
                continue
            else:
                out.append(line)
        profile.write_text("\n".join(out) + "\n", encoding="utf-8")
        pattern = self.root / "loop-kit/patterns/feature-loop-example.md"
        proc = run_apply(self.root, self.contract_rel_for_tests(), "approve")
        self.assertEqual(result_code(proc), "APPLY_SUCCESS")
        quirks = self.mod.load_profile_quirks(self.root, "my-service")
        self.assertIn("Test quirk summary", quirks)

    def contract_rel_for_tests(self) -> str:
        return (
            "docs/loop-learnings/contracts/your-service-api/"
            "PROJ-9999-20260623T120000Z-learning.json"
        )

    def _seed_promotion_contract(self) -> Path:
        run_apply(self.root, self.contract_rel_for_tests(), "approve")
        promo_dir = (
            self.root
            / "docs/loop-learnings/contracts/your-service-api"
        )
        promo = {
            **VALID_LEARNING,
            "mode": "promotion_proposal",
            "fingerprint": "promo-fp",
            "scope": "profile-family",
            "targets": [],
            "actions": [],
        }
        promo_path = promo_dir / "PROJ-9999-20260623T120000Z-promotion.json"
        promo_path.write_text(json.dumps(promo) + "\n", encoding="utf-8")
        return promo_path

    def test_main_module_guard(self) -> None:
        import runpy

        contract_rel = self.contract_rel_for_tests()
        argv = [
            "apply_loop_learning.py",
            "--contract",
            contract_rel,
            "--repo",
            "your-service-api",
        ]
        with mock.patch("sys.argv", argv):
            os.environ["CURSOR_PROJECT_DIR"] = str(self.root)
            with self.assertRaises(SystemExit) as ctx:
                runpy.run_path(str(SCRIPT), run_name="__main__")
            self.assertEqual(ctx.exception.code, 0)

    def test_detect_toon_on_path_success(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("LOOP_TOON_VALIDATOR", None)
            with mock.patch("shutil.which", return_value="/usr/bin/toon"):
                with mock.patch("subprocess.run") as mrun:
                    mrun.return_value = subprocess.CompletedProcess([], 0, "", "")
                    self.assertEqual(
                        self.mod.detect_toon_validator(), ["toon", "validate"]
                    )

    def test_validate_business_wrong_kind_learning(self) -> None:
        promo_path = (
            self.root
            / "docs/loop-learnings/contracts/your-service-api/"
            "PROJ-9999-20260623T120000Z-promotion.json"
        )
        promo_path.write_text(json.dumps(VALID_LEARNING) + "\n", encoding="utf-8")
        proc = run_apply(self.root, str(promo_path.relative_to(self.root)))
        self.assertEqual(result_code(proc), "SCHEMA_INVALID")

    def test_validate_business_wrong_kind_promotion(self) -> None:
        data = {
            **VALID_LEARNING,
            "mode": "promotion_proposal",
            "targets": [],
            "actions": [],
        }
        learning_path = self.root / self.contract_rel_for_tests()
        learning_path.write_text(json.dumps(data) + "\n", encoding="utf-8")
        proc = run_apply(self.root, self.contract_rel_for_tests())
        self.assertEqual(result_code(proc), "SCHEMA_INVALID")

    def test_validate_business_path_checks_direct(self) -> None:
        contract = dict(VALID_LEARNING)
        contract_path = self.root / "docs/loop-learnings/contracts/x/PROJ-9999-20260623T120000Z-learning.json"
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract["rationale_path"] = "docs/wiki/forbidden.md"
        with self.assertRaises(self.mod.ValidationError) as ctx:
            self.mod.validate_contract_business(contract, contract_path)
        self.assertEqual(ctx.exception.code, "PATH_NOT_ALLOWED")
        contract["rationale_path"] = VALID_LEARNING["rationale_path"]
        contract["targets"] = [{"path": "docs/wiki/forbidden.md", "action": "append_markdown"}]
        with self.assertRaises(self.mod.ValidationError) as ctx:
            self.mod.validate_contract_business(contract, contract_path)
        self.assertEqual(ctx.exception.code, "PATH_NOT_ALLOWED")

    def test_marker_exists_false_when_missing_file(self) -> None:
        target = self.root / "loop-kit/patterns/missing.md"
        self.assertFalse(self.mod.marker_exists(target, "fp", 1))

    def test_count_runs_missing_index(self) -> None:
        index = self.root / "docs/loop-learnings/index.json"
        index.unlink()
        self.assertEqual(self.mod.count_runs(self.root, "fp", "single-repo"), 0)

    def test_append_index_merges_existing(self) -> None:
        entry = {
            "fingerprint": "fp",
            "scope": "single-repo",
            "profile": "my-service",
            "repo": "your-service-api",
            "runs": 1,
            "promoted": False,
            "rationale_path": "docs/x.md",
            "contract_path": "docs/y.json",
        }
        self.mod.append_index(self.root, entry)
        entry["runs"] = 2
        self.mod.append_index(self.root, entry)
        index = json.loads(
            (self.root / "docs/loop-learnings/index.json").read_text(encoding="utf-8")
        )
        self.assertEqual(index["entries"][0]["runs"], 2)

    def test_reconcile_no_applied_dir(self) -> None:
        shutil.rmtree(self.root / "docs/loop-learnings/.applied", ignore_errors=True)
        self.assertFalse(self.mod.reconcile_index_from_applied(self.root))

    def test_sync_readme_missing_file(self) -> None:
        readme = self.root / "docs/loop-learnings/README.md"
        readme.unlink()
        self.mod._sync_readme_index(self.root, {"entries": []})

    def test_sync_readme_empty_entries_placeholder(self) -> None:
        readme = self.root / "docs/loop-learnings/README.md"
        text = readme.read_text(encoding="utf-8")
        if "| _none yet_ |" not in text:
            self.mod._sync_readme_index(self.root, {"entries": []})
            self.assertIn("| _none yet_ |", readme.read_text(encoding="utf-8"))

    def test_get_pattern_doc_null_profile(self) -> None:
        path = self.root / "loop-kit/profiles/null-pattern.yaml"
        path.write_text(
            "id: null-pattern\npattern_doc: null\nknown_quirks:\n  - q\n",
            encoding="utf-8",
        )
        self.assertIsNone(self.mod.get_pattern_doc(self.root, "null-pattern"))

    def test_detect_toon_timeout(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("LOOP_TOON_VALIDATOR", None)
            with mock.patch("shutil.which", return_value="/usr/bin/toon"):
                with mock.patch(
                    "subprocess.run", side_effect=subprocess.TimeoutExpired("toon", 10)
                ):
                    self.assertIsNone(self.mod.detect_toon_validator())

    def test_reconcile_marker_without_contract(self) -> None:
        applied = self.root / "docs/loop-learnings/.applied"
        applied.mkdir(parents=True, exist_ok=True)
        (applied / "PROJ-9999-20260623T120000Z.applied").write_text(
            "missing-contract.json\n", encoding="utf-8"
        )
        fake = (
            self.root
            / "docs/loop-learnings/contracts/your-service-api/"
            "missing-contract.json"
        )
        fake.mkdir(parents=True, exist_ok=True)
        self.mod.reconcile_index_from_applied(self.root)

    def test_get_pattern_doc_missing_key(self) -> None:
        path = self.root / "loop-kit/profiles/no-pattern.yaml"
        path.write_text("id: no-pattern\nknown_quirks:\n  - q\n", encoding="utf-8")
        self.assertIsNone(self.mod.get_pattern_doc(self.root, "no-pattern"))

    def test_write_profile_quirks_replaces_old_lines(self) -> None:
        path = self.root / "loop-kit/profiles/multi-quirk.yaml"
        path.write_text(
            "id: multi-quirk\nknown_quirks:\n  - one\n  - two\n  - three\n",
            encoding="utf-8",
        )
        self.mod.write_profile_quirks(self.root, "multi-quirk", ["a", "b", "c"])
        quirks = self.mod.load_profile_quirks(self.root, "multi-quirk")
        self.assertEqual(quirks, ["a", "b", "c"])

    def test_load_profile_quirks_stops_at_sibling_key(self) -> None:
        path = self.root / "loop-kit/profiles/quirks-sibling.yaml"
        path.write_text(
            "id: quirks-sibling\nknown_quirks:\n  - first\nrepos:\n  - x\n",
            encoding="utf-8",
        )
        quirks = self.mod.load_profile_quirks(self.root, "quirks-sibling")
        self.assertEqual(quirks, ["first"])

    def test_upsert_quirk_skip_when_present(self) -> None:
        quirks = self.mod.load_profile_quirks(self.root, "my-service")
        quirks.append("already-there")
        self.mod.write_profile_quirks(self.root, "my-service", quirks)
        pattern = self.root / "loop-kit/patterns/feature-loop-example.md"
        self.mod.upsert_known_quirk(self.root, "my-service", "already-there", pattern)


class ImportErrorStderrTests(unittest.TestCase):
    def test_import_error_message_constant(self) -> None:
        mod = load_module()
        expected = (
            "validation error: jsonschema not installed; "
            "run: pip install -r scripts/requirements-loop-9d.txt"
        )
        self.assertEqual(mod.IMPORT_ERROR_STDERR, expected)


if __name__ == "__main__":
    unittest.main()
