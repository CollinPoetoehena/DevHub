from pathlib import Path, PurePosixPath

import pytest

from repo_fleet.errors import TemplateError
from repo_fleet.templates import (
    RenderedFile,
    TemplateVariables,
    managed_header,
    render_repository,
)
from tests.fakes import write_template

pytestmark = pytest.mark.unit

VARIABLES = TemplateVariables(
    owner="octo",
    repository="alpha",
    visibility="public",
    profiles="common,python",
    default_branch="trunk",
    apm_dependencies=(
        "    - CollinPoetoehena/DevHub/packages/apm/common#main\n"
        "    - CollinPoetoehena/DevHub/packages/apm/python#main"
    ),
)
HEADER = (
    b"# Managed by DevHub tools/repo (templates/common/sync); "
    b"local changes are overwritten.\n"
)


def _render(
    templates: Path,
    profiles: tuple[str, ...] = ("common",),
    *,
    include_apm_seed: bool = False,
) -> dict[str, RenderedFile]:
    rendered = render_repository(
        templates, profiles, VARIABLES, include_apm_seed=include_apm_seed
    )
    return {str(item.path): item for item in rendered}


def test_managed_header_is_exact_for_common() -> None:
    assert managed_header("common") == HEADER


def test_render_substitutes_variables_and_strips_suffix(tmp_path: Path) -> None:
    write_template(
        tmp_path,
        "common/sync/ci.yml.tmpl",
        "repo: $owner/${repository} $visibility $profiles $default_branch $$x\n",
    )

    files = _render(tmp_path)

    assert files["ci.yml"] == RenderedFile(
        PurePosixPath("ci.yml"),
        HEADER + b"repo: octo/alpha public common,python trunk $x\n",
        "sync",
        "common",
    )


def test_render_copies_non_templates_byte_for_byte(tmp_path: Path) -> None:
    content = b"key: $owner\r\n\xff"
    write_template(tmp_path, "common/sync/raw.yaml", content)

    assert _render(tmp_path)["raw.yaml"].content == HEADER + content


def test_render_seed_files_have_no_header(tmp_path: Path) -> None:
    write_template(tmp_path, "common/seed/README.md.tmpl", "# $repository\n")

    files = _render(tmp_path)

    assert files["README.md"].content == b"# alpha\n"
    assert files["README.md"].mode == "seed"


def test_render_apm_seed_includes_common_and_selected_stacks(tmp_path: Path) -> None:
    write_template(
        tmp_path,
        "common/seed/apm.yml.tmpl",
        "name: $repository\ndependencies:\n  apm:\n$apm_dependencies\n",
    )

    content = _render(tmp_path, ("common", "python"), include_apm_seed=True)[
        "apm.yml"
    ].content

    assert content == (
        b"name: alpha\ndependencies:\n  apm:\n"
        b"    - CollinPoetoehena/DevHub/packages/apm/common#main\n"
        b"    - CollinPoetoehena/DevHub/packages/apm/python#main\n"
    )


def test_render_keeps_shebang_first(tmp_path: Path) -> None:
    write_template(tmp_path, "common/sync/bin/run.sh", "#!/bin/sh\necho hi\n")

    content = _render(tmp_path)["bin/run.sh"].content

    assert content == b"#!/bin/sh\n" + HEADER + b"echo hi\n"


@pytest.mark.parametrize("name", ["CODEOWNERS", ".gitignore", ".editorconfig"])
def test_render_allows_hash_comment_names(tmp_path: Path, name: str) -> None:
    write_template(tmp_path, f"common/sync/{name}", "x\n")

    assert _render(tmp_path)[name].content == HEADER + b"x\n"


def test_render_uses_profile_specific_header(tmp_path: Path) -> None:
    write_template(tmp_path, "python/sync/ruff.toml", "x = 1\n")

    content = _render(tmp_path, ("common", "python"))["ruff.toml"].content

    assert content.startswith(b"# Managed by DevHub tools/repo (templates/python/sync)")


def test_render_skips_profiles_without_templates(tmp_path: Path) -> None:
    write_template(tmp_path, "common/sync/a.yml", "a\n")

    assert list(_render(tmp_path, ("common", "go"))) == ["a.yml"]


def test_render_rejects_missing_variable(tmp_path: Path) -> None:
    write_template(tmp_path, "common/sync/a.yml.tmpl", "$unknown\n")

    with pytest.raises(TemplateError, match="unknown template variable 'unknown'"):
        _render(tmp_path)


def test_render_rejects_invalid_placeholder(tmp_path: Path) -> None:
    write_template(tmp_path, "common/sync/a.yml.tmpl", "cost: $ 5\n")

    with pytest.raises(TemplateError, match="invalid placeholder"):
        _render(tmp_path)


def test_render_rejects_non_utf8_template(tmp_path: Path) -> None:
    write_template(tmp_path, "common/sync/a.yml.tmpl", b"\xff\n")

    with pytest.raises(TemplateError, match="not valid UTF-8"):
        _render(tmp_path)


def test_render_rejects_sync_file_without_hash_comments(tmp_path: Path) -> None:
    write_template(tmp_path, "common/sync/README.md", "text\n")

    with pytest.raises(TemplateError, match="must support '#' comments"):
        _render(tmp_path)


def test_render_rejects_conflict_between_profiles(tmp_path: Path) -> None:
    write_template(tmp_path, "common/sync/a.yml", "a\n")
    write_template(tmp_path, "python/sync/a.yml.tmpl", "b\n")

    with pytest.raises(TemplateError, match="common/sync and python/sync"):
        _render(tmp_path, ("common", "python"))


def test_render_rejects_conflict_between_sync_and_seed(tmp_path: Path) -> None:
    write_template(tmp_path, "common/sync/a.yml", "a\n")
    write_template(tmp_path, "common/seed/a.yml", "b\n")

    with pytest.raises(TemplateError, match="common/sync and common/seed"):
        _render(tmp_path)


def test_render_rejects_git_directory_targets(tmp_path: Path) -> None:
    write_template(tmp_path, "common/seed/.git/config", "x\n")

    with pytest.raises(TemplateError, match="must not write into .git"):
        _render(tmp_path)


def test_render_rejects_symlinks(tmp_path: Path) -> None:
    target = write_template(tmp_path, "outside.yml", "x\n")
    link = tmp_path / "common" / "sync" / "link.yml"
    link.parent.mkdir(parents=True)
    link.symlink_to(target)

    with pytest.raises(TemplateError, match="symbolic links"):
        _render(tmp_path)


def test_render_requires_templates_directory(tmp_path: Path) -> None:
    with pytest.raises(TemplateError, match="templates directory not found"):
        _render(tmp_path / "missing")
