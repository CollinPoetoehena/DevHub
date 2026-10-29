"""Verify the installed distribution rather than relying on source-directory imports."""

import tomllib
from importlib import metadata, resources
from pathlib import Path


def test_installed_metadata_matches_project() -> None:
    """The installed distribution must identify the current package and version."""
    project = tomllib.loads(
        (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    assert metadata.version("devhub-python-sdk") == project["version"]
    assert metadata.metadata("devhub-python-sdk")["Requires-Python"] == project["requires-python"]


def test_type_marker_is_packaged() -> None:
    """Type checkers must be able to discover the installed PEP 561 marker."""
    assert resources.files("devhub_python_sdk").joinpath("py.typed").is_file()
