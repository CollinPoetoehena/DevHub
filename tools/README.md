# DevHub Tools

Tooling for DevHub setup, automated repository management, and maintenance. Keep executable logic here and explanations in [`docs/`](../docs/README.md); project-specific operational scripts stay with their project.

- [`setup.py`](setup.py): cleanup only for the retired clone-based Copilot setup. New installs and updates use the [common APM package](../packages/apm/common/README.md), not this script.
- [`repo/`](repo/README.md): repository-management profiles and a placeholder script; automation is not implemented yet.
- [`package/`](package/README.md): reserved packaging-tool notes, not an implemented command.

Central tooling makes settings and maintenance repeatable instead of relying on remembering each convention or synchronizing copies. Add automation for a real recurring need; do not build a generic management framework in advance.

## Remove legacy workspace links

Remove any shell hook that runs `tools/setup.py`. From the original DevHub clone location, run:

```sh
python3 tools/setup.py --workspace /path/to/personal-workspace --uninstall
```

Requires Linux/WSL, Python 3.10+, and Git. Cleanup is offline and works even after the old customization sources have been deleted. It removes only links recorded in `.github/.devhub-setup.json` whose targets are unchanged; personal replacements, unrecorded links, and the clone are preserved. The state must identify the original clone location. Review any remaining links manually rather than deleting workspace customizations indiscriminately.

Without `--uninstall`, including with the historical `--no-pull` option, the command fails with APM guidance before Git operations or workspace changes. It does not install APM or migrate customizations.

## Tests

The setup tests live in [`tests/test_setup.py`](tests/test_setup.py). Run them in a Python 3.10+ Linux container with Git installed, without network access, and write output to `test-results/`:

```sh
mkdir -p test-results
docker run --rm --network none \
    --volume "$PWD:/workspace:ro" --workdir /workspace \
    <python-image-with-git> \
    python -B -m unittest discover -s tools/tests -v \
    > test-results/setup-tests.log 2>&1
```

Run from the DevHub root and replace the image placeholder with a trusted image containing Python and Git. The tests use temporary homes, historical setup journals, and local Git remotes; they verify rejected installs/updates and safe cleanup without touching the real workspace or contacting GitHub.