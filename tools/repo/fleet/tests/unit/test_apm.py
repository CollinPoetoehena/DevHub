from pathlib import Path, PurePosixPath

import pytest
import yaml

from repo_fleet import apm
from repo_fleet.errors import FleetError
from repo_fleet.planner import PlannedChange
from tests.fakes import FakeRunner

pytestmark = pytest.mark.unit

PACKAGE = "CollinPoetoehena/DevHub/packages/apm/python#main"
MANIFEST = (
    "name: example\n"
    "dependencies:\n"
    "  apm:\n"
    "    - CollinPoetoehena/DevHub/packages/apm/common#main\n"
    f"    - {PACKAGE}\n"
)
UPDATE_OUTPUT = """[>] Checking upstream for revision-pin freshness...
[i] Update plan for apm.yml

  [~] collinpoetoehena/devhub/packages/apm/python
      ref: manage-repos-automatically -> main (0b57923 -> 07664b9)
      files: .agents/skills/python

  1 updated
  [~] updated

[i] Dry run: no changes applied. Re-run without --dry-run to update.
"""
CURRENT_OUTPUT = (
    "[>] Checking upstream for revision-pin freshness...\n"
    "[+] All dependencies already at their latest matching refs.\n"
)
LEGACY_CALLER_FIXTURE = (
    b"# Managed by DevHub tools/repo (templates/common/sync); "
    b"local changes are overwritten.\n"
    b"name: DevHub APM sync\n"
    b"\n"
    b"on:\n"
    b"  push:\n"
    b"    branches: [main]\n"
    b"  schedule:\n"
    b'    - cron: "0 6 * * 1"\n'
    b"  workflow_dispatch:\n"
    b"\n"
    b"permissions: {}\n"
    b"\n"
    b"jobs:\n"
    b"  apm-sync:\n"
    b"    permissions:\n"
    b"      contents: write\n"
    b"      pull-requests: write\n"
    b"    # Tracks DevHub main on purpose so every repository gets sync fixes "
    b"without a template change.\n"
    b"    uses: CollinPoetoehena/DevHub/.github/workflows/apm-sync.yml@main "
    b"# zizmor: ignore[unpinned-uses]\n"
)


def _lock_file(path: Path, deployed: list[str] | None = None) -> Path:
    data = {
        "lockfile_version": "1",
        "apm_version": "0.35.0",
        "dependencies": [
            {
                "deployed_files": deployed or [],
                "deployed_file_hashes": {},
            }
        ],
    }
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def test_manifest_requires_common_and_selected_stack(tmp_path: Path) -> None:
    manifest = tmp_path / "apm.yml"
    manifest.write_text(MANIFEST, encoding="utf-8")

    parsed = apm._load_manifest(manifest, ("python",))

    assert parsed.required_stacks == ("common", "python")
    assert parsed.managed_refs == (
        ("common", "collinpoetoehena/devhub/packages/apm/common"),
        ("python", "collinpoetoehena/devhub/packages/apm/python"),
    )
    assert not parsed.has_local_dependencies


def test_manifest_missing_required_dependency_fails(tmp_path: Path) -> None:
    manifest = tmp_path / "apm.yml"
    manifest.write_text(MANIFEST.replace(f"    - {PACKAGE}\n", ""), encoding="utf-8")

    with pytest.raises(FleetError, match="missing required.*python"):
        apm._load_manifest(manifest, ("python",))


def test_manifest_rejects_duplicate_managed_stacks(tmp_path: Path) -> None:
    manifest = tmp_path / "apm.yml"
    manifest.write_text(
        MANIFEST + f"    - {PACKAGE}\n",
        encoding="utf-8",
    )

    with pytest.raises(FleetError, match="duplicate DevHub APM stack"):
        apm._load_manifest(manifest, ())


def test_manifest_rejects_escaping_local_dependency(tmp_path: Path) -> None:
    manifest = tmp_path / "apm.yml"
    manifest.write_text(MANIFEST + "    - ../outside\n", encoding="utf-8")

    with pytest.raises(FleetError, match="unsafe local APM dependency path"):
        apm._load_manifest(manifest, ("python",))


def test_manifest_rejects_symlinked_local_dependency(tmp_path: Path) -> None:
    manifest = tmp_path / "apm.yml"
    manifest.write_text(MANIFEST, encoding="utf-8")
    external = tmp_path / "outside"
    external.mkdir()
    (external / "apm.yml").write_text("dependencies: {apm: []}\n", encoding="utf-8")
    (tmp_path / "linked").symlink_to(external, target_is_directory=True)
    manifest.write_text(
        MANIFEST.replace(
            "  apm:\n",
            "  apm:\n    - ./linked\n",
        ),
        encoding="utf-8",
    )

    with pytest.raises(FleetError, match="local APM dependency path is a symlink"):
        apm._load_manifest(manifest, ("python",))


def test_manifest_rejects_duplicate_yaml_keys(tmp_path: Path) -> None:
    manifest = tmp_path / "apm.yml"
    manifest.write_text("dependencies: {}\ndependencies: {}\n", encoding="utf-8")

    with pytest.raises(FleetError, match="duplicate key"):
        apm._load_manifest(manifest, ())


def test_update_output_classifies_stale_and_current() -> None:
    refs = (("python", "collinpoetoehena/devhub/packages/apm/python"),)

    assert apm._classify_update_output(UPDATE_OUTPUT, refs) == "UPDATE_REQUIRED"
    assert apm._classify_update_output(CURRENT_OUTPUT, refs) == "CURRENT"


def test_freshness_does_not_label_checked_main_dependencies_as_pinned(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "apm.yml"
    manifest_path.write_text(
        MANIFEST + "    - CollinPoetoehena/DevHub/packages/apm/java#v1\n",
        encoding="utf-8",
    )
    manifest = apm._load_manifest(manifest_path, ("python",))
    _lock_file(tmp_path / apm.APM_LOCK)
    runner = FakeRunner(
        outputs={
            ("apm", "update"): CURRENT_OUTPUT,
        }
    )

    result = apm._freshness(runner, tmp_path, manifest)

    assert result.freshness == "CURRENT"
    assert manifest.pinned_stacks == ("java",)
    assert (
        "apm",
        "update",
        "--dry-run",
        "--target",
        "copilot",
        "collinpoetoehena/devhub/packages/apm/common",
        "collinpoetoehena/devhub/packages/apm/python",
    ) in runner.commands()


def test_update_output_rejects_unknown_or_ambiguous_status() -> None:
    refs = (("python", "collinpoetoehena/devhub/packages/apm/python"),)

    with pytest.raises(FleetError, match="unrecognized update plan"):
        apm._classify_update_output("APM output changed\n", refs)
    with pytest.raises(FleetError, match="unrequested dependency"):
        apm._classify_update_output(UPDATE_OUTPUT.replace("/python\n", "/java\n"), refs)
    with pytest.raises(FleetError, match="unrequested dependency"):
        apm._classify_update_output(
            UPDATE_OUTPUT.replace(
                "collinpoetoehena/devhub/packages/apm/python",
                "other-owner/other-repo/packages/apm/python",
            ),
            refs,
        )
    with pytest.raises(FleetError, match="duplicate rows"):
        apm._classify_update_output(
            UPDATE_OUTPUT.replace(
                "  1 updated\n",
                "  [~] collinpoetoehena/devhub/packages/apm/python\n  2 updated\n",
            ),
            refs,
        )


def test_deployed_path_parser_rejects_traversal() -> None:
    with pytest.raises(FleetError, match="unsafe APM deployment path"):
        apm._safe_relative_path("../outside")
    with pytest.raises(FleetError, match="unsafe APM deployment path"):
        apm._safe_relative_path(".")


def test_deployed_lock_rejects_malformed_hash_metadata() -> None:
    lock = {
        "dependencies": [
            {
                "deployed_files": [".agents/skills/owned.md"],
                "deployed_file_hashes": {".agents/skills/owned.md": "not-a-hash"},
            }
        ]
    }

    with pytest.raises(FleetError, match="malformed deployed file hash"):
        apm._verify_deployed_files(Path("."), lock)


def test_modified_managed_file_is_a_conflict(tmp_path: Path) -> None:
    target = tmp_path / ".github" / "instructions" / "owned.md"
    target.parent.mkdir(parents=True)
    target.write_text("customized\n", encoding="utf-8")
    lock = {
        "dependencies": [
            {
                "deployed_files": [".github/instructions/owned.md"],
                "deployed_file_hashes": {
                    ".github/instructions/owned.md": "sha256:" + "0" * 64
                },
            }
        ]
    }

    with pytest.raises(FleetError, match="locally modified"):
        apm._verify_deployed_files(tmp_path, lock)


def test_legacy_caller_is_deleted_only_on_exact_match(tmp_path: Path) -> None:
    caller = tmp_path / apm.LEGACY_CALLER
    caller.parent.mkdir(parents=True)
    caller.write_bytes(LEGACY_CALLER_FIXTURE)

    assert apm.LEGACY_CALLER_CONTENT == LEGACY_CALLER_FIXTURE

    change = apm._legacy_caller_change(tmp_path, False)

    assert change == PlannedChange(apm.LEGACY_CALLER, "delete", "sync", b"", None)
    assert not caller.exists()


def test_custom_legacy_caller_is_preserved(tmp_path: Path) -> None:
    caller = tmp_path / apm.LEGACY_CALLER
    caller.parent.mkdir(parents=True)
    caller.write_bytes(LEGACY_CALLER_FIXTURE + b"\n# customization\n")

    with pytest.raises(FleetError, match="customized legacy caller"):
        apm._legacy_caller_change(tmp_path, False)

    assert caller.read_bytes().endswith(b"# customization\n")


def test_dangling_legacy_caller_symlink_is_rejected(tmp_path: Path) -> None:
    caller = tmp_path / apm.LEGACY_CALLER
    caller.parent.mkdir(parents=True)
    caller.symlink_to(tmp_path / "missing-target")

    with pytest.raises(FleetError, match="must not be a symlink"):
        apm._legacy_caller_change(tmp_path, False)


def test_manifest_symlink_is_rejected_before_read(tmp_path: Path) -> None:
    target = tmp_path / "external.yml"
    target.write_text(MANIFEST, encoding="utf-8")
    (tmp_path / apm.APM_MANIFEST).symlink_to(target)

    with pytest.raises(FleetError, match="expected a regular file"):
        apm.prepare_apm_sync(tmp_path, FakeRunner(), (), (), (), False)


def test_apm_subprocesses_do_not_receive_auth_tokens(tmp_path: Path) -> None:
    manifest = tmp_path / "apm.yml"
    manifest.write_text(MANIFEST, encoding="utf-8")
    lock = _lock_file(tmp_path / "apm.lock.yaml")
    runner = FakeRunner(
        outputs={
            ("apm", "--version"): "Agent Package Manager (APM) CLI version 0.35.0",
            ("apm", "update"): CURRENT_OUTPUT,
        }
    )

    apm._verify_cli(runner, tmp_path)
    parsed = apm._load_manifest(manifest, ("python",))
    result = apm._freshness(runner, tmp_path, parsed)

    assert result.freshness == "CURRENT"
    assert runner.environments == [apm.TOKEN_ENV, apm.TOKEN_ENV]
    assert lock.is_file()


def test_apm_preparation_isolates_all_workflow_and_terraform_credentials(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / apm.APM_MANIFEST).write_text(MANIFEST, encoding="utf-8")
    _lock_file(tmp_path / apm.APM_LOCK)
    for key in (
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "TF_TOKEN_app_terraform_io",
        "GITHUB_OUTPUT",
        "FLEET_SYNC_DIR",
    ):
        monkeypatch.setenv(key, "must-not-reach-apm")
    runner = FakeRunner(
        outputs={
            ("apm", "--version"): "APM CLI version 0.35.0",
            ("apm", "update"): CURRENT_OUTPUT,
        }
    )

    apm.prepare_apm_sync(tmp_path, runner, (), ("python",), (), False)

    apm_environments = [
        environment
        for command, environment in zip(
            runner.commands(), runner.environments, strict=True
        )
        if command[0] == "apm"
    ]
    assert apm_environments
    assert all(
        environment is not None
        and environment.get("GH_TOKEN") is None
        and environment.get("GITHUB_TOKEN") is None
        and environment.get("TF_TOKEN_app_terraform_io") is None
        and environment.get("GITHUB_OUTPUT") is None
        and environment.get("FLEET_SYNC_DIR") is None
        and environment.get("GIT_CONFIG_GLOBAL") == "/dev/null"
        and environment.get("GH_CONFIG_DIR")
        for environment in apm_environments
    )


def test_apm_cli_version_must_match_exactly(tmp_path: Path) -> None:
    runner = FakeRunner(
        outputs={
            ("apm", "--version"): ("Agent Package Manager (APM) CLI version 0.35.00"),
        }
    )

    with pytest.raises(FleetError, match="APM CLI 0.35.0 is required"):
        apm._verify_cli(runner, tmp_path)


def test_collect_changes_rejects_unowned_apm_output(tmp_path: Path) -> None:
    (tmp_path / "unowned.txt").write_text("data\n", encoding="utf-8")
    runner = FakeRunner(
        outputs={
            ("git", "diff", "--name-only", "-z"): "unowned.txt\0",
        }
    )

    with pytest.raises(FleetError, match="unowned path"):
        apm._collect_changes(
            tmp_path,
            runner,
            {PurePosixPath("apm.lock.yaml")},
            frozenset(),
            frozenset(),
            (),
            None,
            False,
        )


def test_collect_changes_rejects_dangling_symlink_output(tmp_path: Path) -> None:
    target = tmp_path / "owned.txt"
    target.symlink_to(tmp_path / "missing-target")
    runner = FakeRunner(
        outputs={
            ("git", "diff", "--name-only", "-z"): "owned.txt\0",
        }
    )

    with pytest.raises(FleetError, match="APM sync produced a symlink"):
        apm._collect_changes(
            tmp_path,
            runner,
            {PurePosixPath("owned.txt")},
            frozenset(),
            frozenset(),
            (),
            None,
            False,
        )
