"""Command-line entry point: check, plan, and apply repository template syncs."""

import argparse
import logging
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from repo_fleet import git_ops
from repo_fleet.errors import FleetError
from repo_fleet.inventory import Inventory, Repository, load_inventory
from repo_fleet.paths import FleetPaths, resolve_paths
from repo_fleet.planner import RepoPlan, plan_repo
from repo_fleet.runner import CommandRunner, SubprocessRunner
from repo_fleet.templates import TemplateVariables, render_repository

LOGGER = logging.getLogger("repo_fleet")
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_CHANGES = 2
CHECK_DEFAULT_BRANCH = "main"


@dataclass(frozen=True)
class CheckedOutPlan:
    repository: Repository
    checkout: Path
    plan: RepoPlan


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--inventory", type=Path, help="inventory JSON file")
    common.add_argument("--templates", type=Path, help="templates directory")
    common.add_argument("-v", "--verbose", action="store_true", help="debug logs")

    parser = argparse.ArgumentParser(
        prog="repo-fleet",
        description="Sync DevHub repository templates through pull requests.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "check",
        parents=[common],
        help="validate the inventory and render all templates offline",
    )
    plan = commands.add_parser(
        "plan", parents=[common], help="show changes; exit 2 when any exist"
    )
    _add_repo_option(plan)
    plan.add_argument("--diff", action="store_true", help="print unified diffs")
    apply = commands.add_parser(
        "apply", parents=[common], help="push the sync branch and open PRs"
    )
    _add_repo_option(apply)
    apply.add_argument("--yes", action="store_true", help="skip the confirmation")
    return parser


def main(argv: Sequence[str] | None = None, runner: CommandRunner | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        stream=sys.stderr,
        format="%(levelname)s: %(message)s",
    )
    try:
        paths = resolve_paths(args.inventory, args.templates)
        inventory = load_inventory(paths.inventory)
        if args.command == "check":
            return run_check(inventory, paths)
        selected = select_repositories(inventory, args.repo)
        active_runner = runner or SubprocessRunner()
        if args.command == "plan":
            return run_plan(inventory, paths, selected, active_runner, args.diff)
        return run_apply(inventory, paths, selected, active_runner, args.yes)
    except FleetError as err:
        LOGGER.error("%s", err)
        return EXIT_ERROR


def run_check(inventory: Inventory, paths: FleetPaths) -> int:
    for repository in inventory.active():
        variables = TemplateVariables.for_repository(
            inventory, repository, CHECK_DEFAULT_BRANCH
        )
        rendered = render_repository(paths.templates, repository.profiles, variables)
        print(f"ok {repository.name}: {len(rendered)} file(s)")
    return EXIT_OK


def run_plan(
    inventory: Inventory,
    paths: FleetPaths,
    selected: tuple[Repository, ...],
    runner: CommandRunner,
    include_diff: bool,
) -> int:
    git_ops.ensure_gh_auth(runner)
    with tempfile.TemporaryDirectory(prefix="repo-fleet-") as workdir:
        plans = checkout_plans(
            inventory, paths, selected, runner, Path(workdir), include_diff
        )
        for item in plans:
            print_plan(item.plan, include_diff)
    return EXIT_CHANGES if any(item.plan.has_changes for item in plans) else EXIT_OK


def run_apply(
    inventory: Inventory,
    paths: FleetPaths,
    selected: tuple[Repository, ...],
    runner: CommandRunner,
    assume_yes: bool,
) -> int:
    if not assume_yes and not sys.stdin.isatty():
        raise FleetError("refusing to apply in a non-interactive session without --yes")
    git_ops.ensure_gh_auth(runner)
    with tempfile.TemporaryDirectory(prefix="repo-fleet-") as workdir:
        plans = checkout_plans(inventory, paths, selected, runner, Path(workdir), False)
        pending = tuple(item for item in plans if item.plan.has_changes)
        for item in plans:
            print_plan(item.plan, False)
        if not pending:
            return EXIT_OK
        if not assume_yes and not confirm(len(pending)):
            LOGGER.info("aborted; nothing was pushed")
            return EXIT_ERROR
        for item in pending:
            result = git_ops.sync_checkout(
                runner,
                inventory.slug(item.repository),
                item.plan.default_branch,
                item.checkout,
                item.plan.changes,
            )
            pushed = "pushed" if result.pushed else "branch unchanged"
            print(f"{item.repository.name}: {pushed}; PR {result.pull_request}")
    return EXIT_OK


def checkout_plans(
    inventory: Inventory,
    paths: FleetPaths,
    selected: tuple[Repository, ...],
    runner: CommandRunner,
    workdir: Path,
    include_diff: bool,
) -> tuple[CheckedOutPlan, ...]:
    return tuple(
        checkout_plan(inventory, paths, repository, runner, workdir, include_diff)
        for repository in selected
    )


def checkout_plan(
    inventory: Inventory,
    paths: FleetPaths,
    repository: Repository,
    runner: CommandRunner,
    workdir: Path,
    include_diff: bool,
) -> CheckedOutPlan:
    slug = inventory.slug(repository)
    branch = git_ops.default_branch(runner, slug)
    checkout = workdir / repository.name
    LOGGER.info("cloning %s (%s)", slug, branch)
    git_ops.clone(runner, slug, checkout, branch)
    variables = TemplateVariables.for_repository(inventory, repository, branch)
    rendered = render_repository(paths.templates, repository.profiles, variables)
    changes = plan_repo(rendered, checkout, include_diff=include_diff)
    plan = RepoPlan(repository=repository.name, default_branch=branch, changes=changes)
    return CheckedOutPlan(repository=repository, checkout=checkout, plan=plan)


def select_repositories(
    inventory: Inventory, names: Sequence[str] | None
) -> tuple[Repository, ...]:
    if not names:
        return inventory.active()
    unique = tuple(dict.fromkeys(names))
    unknown = [name for name in unique if inventory.find(name) is None]
    if unknown:
        raise FleetError(f"unknown repositories: {', '.join(unknown)}")
    found = tuple(repo for repo in inventory.repositories if repo.name in unique)
    for repo in found:
        if repo.archived:
            LOGGER.info("%s: archived; skipping", repo.name)
    return tuple(repo for repo in found if not repo.archived)


def print_plan(plan: RepoPlan, include_diff: bool) -> None:
    count = len(plan.writes)
    print(f"{plan.repository} ({plan.default_branch}): {count} change(s)")
    for change in plan.changes:
        if change.action == "unchanged":
            continue
        print(f"  {change.action} {change.path}")
        if include_diff and change.diff:
            print(change.diff, end="" if change.diff.endswith("\n") else "\n")


def confirm(count: int) -> bool:
    answer = input(f"Push sync branches and pull requests for {count} repo(s)? [y/N] ")
    return answer.strip().lower() in {"y", "yes"}


def _add_repo_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--repo",
        action="append",
        metavar="NAME",
        help="limit to this repository; repeatable",
    )


if __name__ == "__main__":
    sys.exit(main())
