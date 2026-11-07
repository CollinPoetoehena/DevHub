import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from repo_fleet import terraform_policy
from tests.fakes import FakeRunner

pytestmark = pytest.mark.integration


def test_terraform_1_17_1_cloud_init_argument_contract(tmp_path: Path) -> None:
    terraform = shutil.which("terraform")
    if terraform is None:
        pytest.skip("Terraform 1.17.1 is not installed")
    environment = {
        "PATH": os.defpath,
        "HOME": str(tmp_path),
        "TF_CLOUD_ORGANIZATION": "example",
        "TF_WORKSPACE": "fleet",
        "TF_CLOUD_HOSTNAME": "!",
        "TF_IN_AUTOMATION": "1",
    }
    version = subprocess.run(
        [terraform, "version", "-json"],
        env=environment,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    if json.loads(version.stdout)["terraform_version"] != "1.17.1":
        pytest.skip("contract diagnostic requires Terraform 1.17.1")

    (tmp_path / "main.tf").write_text("terraform {\n  cloud {}\n}\n", encoding="utf-8")
    runner = FakeRunner(outputs={("terraform", "workspace", "show"): "fleet\n"})
    terraform_policy._run_init(tmp_path, runner, "fleet", environment)
    init_args = list(runner.commands()[0][1:])

    valid = subprocess.run(
        [terraform, *init_args, "-no-color"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    invalid = subprocess.run(
        [terraform, *init_args, "-no-color", "-backend-config=organization=example"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )

    assert valid.returncode != 0
    assert "hostname is not in the correct format" in valid.stderr
    assert "Invalid command-line option" not in valid.stderr
    assert invalid.returncode != 0
    assert "Invalid command-line option" in invalid.stderr
    assert "not applicable to HCP Terraform" in invalid.stderr
