"""Resolve and render profile templates into repository files."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from string import Template
from typing import Literal

from repo_fleet.errors import TemplateError
from repo_fleet.inventory import Inventory, Repository

Mode = Literal["sync", "seed"]
MODES: tuple[Mode, ...] = ("sync", "seed")
TEMPLATE_SUFFIX = ".tmpl"
MANAGED_HEADER_FORMAT = (
    "# Managed by DevHub tools/repo (templates/{profile}/sync); "
    "local changes are overwritten.\n"
)
HASH_COMMENT_SUFFIXES = frozenset(
    {".yml", ".yaml", ".sh", ".toml", ".tf", ".py", ".cfg"}
)
HASH_COMMENT_NAMES = frozenset(
    {"CODEOWNERS", ".gitignore", ".gitattributes", ".editorconfig"}
)
SHEBANG = b"#!"
FORBIDDEN_PATH_PART = ".git"


@dataclass(frozen=True)
class RenderedFile:
    path: PurePosixPath
    content: bytes
    mode: Mode
    profile: str


@dataclass(frozen=True)
class TemplateVariables:
    owner: str
    repository: str
    visibility: str
    profiles: str
    default_branch: str
    apm_dependencies: str

    @classmethod
    def for_repository(
        cls, inventory: Inventory, repository: Repository, default_branch: str
    ) -> "TemplateVariables":
        return cls(
            owner=inventory.owner,
            repository=repository.name,
            visibility=repository.visibility,
            profiles=",".join(repository.profiles),
            default_branch=default_branch,
            apm_dependencies="\n".join(
                f"    - CollinPoetoehena/DevHub/packages/apm/{stack}#main"
                for stack in ("common", *repository.apm_stacks)
            ),
        )

    def as_mapping(self) -> Mapping[str, str]:
        return {
            "owner": self.owner,
            "repository": self.repository,
            "visibility": self.visibility,
            "profiles": self.profiles,
            "default_branch": self.default_branch,
            "apm_dependencies": self.apm_dependencies,
        }


def managed_header(profile: str) -> bytes:
    return MANAGED_HEADER_FORMAT.format(profile=profile).encode("utf-8")


def render_repository(
    templates_dir: Path,
    profiles: tuple[str, ...],
    variables: TemplateVariables,
    *,
    include_apm_seed: bool = False,
) -> tuple[RenderedFile, ...]:
    """Render every sync and seed template of the given profiles, in order.

    A profile without a templates directory contributes no files.
    """
    if not templates_dir.is_dir():
        raise TemplateError(f"{templates_dir}: templates directory not found")
    rendered = tuple(
        render_file(source, root, profile, mode, variables)
        for profile in profiles
        for mode in MODES
        for root in (templates_dir / profile / mode,)
        for source in _template_sources(root)
        if include_apm_seed
        or profile != "common"
        or mode != "seed"
        or source.relative_to(root).as_posix() != "apm.yml.tmpl"
    )
    _reject_conflicts(rendered)
    return rendered


def render_file(
    source: Path,
    root: Path,
    profile: str,
    mode: Mode,
    variables: TemplateVariables,
) -> RenderedFile:
    relative = PurePosixPath(source.relative_to(root).as_posix())
    target = _target_path(relative)
    content = (
        _substitute(source, variables)
        if relative.suffix == TEMPLATE_SUFFIX
        else source.read_bytes()
    )
    if mode == "sync":
        content = _with_header(target, content, profile, source)
    return RenderedFile(path=target, content=content, mode=mode, profile=profile)


def _template_sources(root: Path) -> tuple[Path, ...]:
    if not root.is_dir():
        return ()
    entries = sorted(root.rglob("*"))
    links = [entry for entry in entries if entry.is_symlink()]
    if links:
        raise TemplateError(f"{links[0]}: symbolic links are not supported")
    return tuple(entry for entry in entries if entry.is_file())


def _target_path(relative: PurePosixPath) -> PurePosixPath:
    target = (
        relative.with_suffix("") if relative.suffix == TEMPLATE_SUFFIX else relative
    )
    if FORBIDDEN_PATH_PART in target.parts:
        raise TemplateError(f"{relative}: templates must not write into .git")
    return target


def _substitute(source: Path, variables: TemplateVariables) -> bytes:
    try:
        text = source.read_text(encoding="utf-8")
        return Template(text).substitute(variables.as_mapping()).encode("utf-8")
    except UnicodeDecodeError as err:
        raise TemplateError(f"{source}: template is not valid UTF-8") from err
    except KeyError as err:
        raise TemplateError(f"{source}: unknown template variable {err}") from err
    except ValueError as err:
        raise TemplateError(f"{source}: invalid placeholder: {err}") from err


def _with_header(
    target: PurePosixPath, content: bytes, profile: str, source: Path
) -> bytes:
    if target.suffix not in HASH_COMMENT_SUFFIXES and (
        target.name not in HASH_COMMENT_NAMES
    ):
        raise TemplateError(
            f"{source}: sync files must support '#' comments for the managed "
            f"header; supported suffixes: {sorted(HASH_COMMENT_SUFFIXES)}, "
            f"names: {sorted(HASH_COMMENT_NAMES)}"
        )
    header = managed_header(profile)
    if not content.startswith(SHEBANG):
        return header + content
    shebang, newline, rest = content.partition(b"\n")
    return shebang + newline + header + rest


def _reject_conflicts(rendered: tuple[RenderedFile, ...]) -> None:
    seen: dict[PurePosixPath, RenderedFile] = {}
    for item in rendered:
        previous = seen.get(item.path)
        if previous is not None:
            raise TemplateError(
                f"{item.path}: rendered by both {previous.profile}/{previous.mode} "
                f"and {item.profile}/{item.mode}"
            )
        seen[item.path] = item
