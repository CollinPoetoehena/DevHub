# DevHub Tools

Tooling for DevHub setup, automated repository management, and maintenance. Keep executable logic here and explanations in [`docs/`](../docs/README.md); project-specific operational scripts stay with their project.

- [`setup.py`](setup.py): the single clone-based Copilot setup/update script. Follow [Copilot setup](../docs/COPILOT-SETUP.md) for first use, the short shell hook, verification, and uninstall.
- [`repo/`](repo/README.md): repository-management profiles and a placeholder script; automation is not implemented yet.
- [`package/`](package/README.md): reserved packaging-tool notes, not an implemented command.

Central tooling makes settings and maintenance repeatable instead of relying on remembering each convention or synchronizing copies. Add automation for a real recurring need; do not build a generic management framework in advance.

The setup tests live in [`tests/test_setup.py`](tests/test_setup.py). Run them in a Python 3.10+ Linux container with Git installed, without network access, and write output to `test-results/`:

```sh
mkdir -p test-results
docker run --rm --network none \
    --volume "$PWD:/workspace:ro" --workdir /workspace \
    <python-image-with-git> \
    python -B -m unittest discover -s tools/tests -v \
    > test-results/setup-tests.log 2>&1
```

Run from the DevHub root and replace the image placeholder with a trusted image containing Python and Git. The tests use temporary homes and local Git remotes; they do not touch the real workspace or contact GitHub.